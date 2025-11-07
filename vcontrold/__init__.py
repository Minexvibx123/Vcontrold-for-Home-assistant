"""Viessmann vcontrold Integration - All-in-One Lösung mit integriertem Daemon."""
import logging
from typing import Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    ATTR_MODE,
    ATTR_TEMPERATURE,
    CONF_DEVICE,
    CONF_FRAMING,
    CONF_UPDATE_INTERVAL,
    DEFAULT_CACHE_TTL,
    DEFAULT_DEVICE,
    DEFAULT_FRAMING,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_TEMP,
    MIN_TEMP,
    SERVICE_SET_BETRIEBSART,
    SERVICE_SET_TEMP_WW_SOLL,
    VALID_MODES,
)
from .daemon_manager import VcontroledDaemonManager
from .vcontrold_manager import VcontroledManager

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.SENSOR]

# Setup für YAML-Konfiguration
CONFIG_SCHEMA = None  # Wird durch Config Flow ersetzt


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richte Integration ein - All-in-One mit integriertem Daemon."""
    _LOGGER.debug("🔧 Richte vcontrold All-in-One Integration ein")
    
    device = entry.data.get(CONF_DEVICE, DEFAULT_DEVICE)
    framing = entry.data.get(CONF_FRAMING, DEFAULT_FRAMING)
    manage_daemon = entry.data.get("manage_daemon", True)  # Default: HA verwaltet Daemon
    host = entry.data.get("host", "localhost")
    port = entry.data.get("port", 3002)
    
    # Speichere Manager im hass.data
    hass.data.setdefault(DOMAIN, {})
    
    # Starte Daemon wenn aktiviert
    if manage_daemon:
        _LOGGER.info("📡 Starte integriertem vcontrold Daemon...")
        daemon_manager = VcontroledDaemonManager(
            config_dir=hass.config.path(),
            device=device,
            host=host,
            port=port,
        )
        
        # Versuche Daemon zu starten
        daemon_started = await hass.async_add_executor_job(
            daemon_manager.start_daemon
        )
        
        if not daemon_started:
            _LOGGER.error("❌ Konnte vcontrold Daemon nicht starten")
            _LOGGER.error("💡 Bitte stelle sicher dass:")
            _LOGGER.error("   1. vcontrold Binary existiert")
            _LOGGER.error("   2. Serielles Gerät zugänglich ist")
            _LOGGER.error("   3. Benutzer passende Berechtigungen hat")
            raise ConfigEntryNotReady("vcontrold Daemon konnte nicht gestartet werden")
        
        hass.data[DOMAIN]["daemon_manager"] = daemon_manager
        _LOGGER.info(f"✅ vcontrold Daemon läuft auf {host}:{port}")
    
    # Verbinde zum vcontrold (integriert oder extern)
    manager = VcontroledManager(host=host, port=port)
    
    # Prüfe Verfügbarkeit
    try:
        is_available = await hass.async_add_executor_job(manager.is_available)
        if not is_available:
            error_msg = f"vcontrold nicht erreichbar auf {host}:{port}"
            _LOGGER.error(f"❌ {error_msg}")
            raise ConfigEntryNotReady(error_msg)
    except Exception as e:
        _LOGGER.error(f"❌ Fehler beim Verbindungstest: {e}")
        raise ConfigEntryNotReady(f"Verbindungsfehler: {e}")
    
    # Speichere Manager
    hass.data[DOMAIN][entry.entry_id] = manager
    
    # Registriere Services
    _setup_services(hass, manager)
    
    # Lade Plattformen
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info(f"✅ vcontrold Integration erfolgreich eingerichtet ({host}:{port})")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entlade Integration."""
    _LOGGER.debug("Entlade vcontrold Integration")
    
    # Stoppe Daemon wenn HA ihn verwaltet
    daemon_manager = hass.data[DOMAIN].get("daemon_manager")
    if daemon_manager:
        await hass.async_add_executor_job(daemon_manager.stop_daemon)
        _LOGGER.info("vcontrold Daemon gestoppt")
    
    # Entlade Plattformen
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        manager = hass.data[DOMAIN].pop(entry.entry_id, None)
        if manager:
            manager.cleanup()
    
    return unload_ok


def _setup_services(hass: HomeAssistant, manager: VcontroledManager):
    """Registriere Custom Services."""
    
    async def handle_set_temp_ww_soll(call: ServiceCall) -> None:
        """Handle Service zum Setzen der Warmwasser-Solltemperatur."""
        temp = call.data.get(ATTR_TEMPERATURE)
        
        if not isinstance(temp, (int, float)) or temp < MIN_TEMP or temp > MAX_TEMP:
            _LOGGER.error(f"Ungültige Temperatur: {temp}. Bereich: {MIN_TEMP}-{MAX_TEMP}°C")
            return
        
        result = await hass.async_add_executor_job(
            manager.set_temperature, "setTempWWsoll", float(temp)
        )
        
        if result:
            _LOGGER.info(f"✅ Warmwasser-Solltemperatur auf {temp}°C gesetzt")
        else:
            _LOGGER.error(f"❌ Fehler beim Setzen der Warmwasser-Solltemperatur")
    
    async def handle_set_betriebsart(call: ServiceCall) -> None:
        """Handle Service zum Setzen der Betriebsart."""
        mode = call.data.get(ATTR_MODE, "auto")
        
        if mode not in VALID_MODES:
            _LOGGER.error(f"Ungültige Betriebsart: {mode}. Gültig: {VALID_MODES}")
            return
        
        result = await hass.async_add_executor_job(
            manager.set_operating_mode, mode
        )
        
        if result:
            _LOGGER.info(f"✅ Betriebsart auf {mode} gesetzt")
        else:
            _LOGGER.error(f"❌ Fehler beim Setzen der Betriebsart")
    
    # Daemon Management Services (wenn HA Daemon verwaltet)
    daemon_manager = hass.data[DOMAIN].get("daemon_manager")
    
    if daemon_manager:
        async def handle_start_daemon(call: ServiceCall) -> None:
            """Service zum Starten des Daemons."""
            device = call.data.get("device")
            result = await hass.async_add_executor_job(
                daemon_manager.start_daemon, device
            )
            
            if result:
                _LOGGER.info("✅ vcontrold Daemon gestartet")
                await hass.async_create_task(
                    hass.components.persistent_notification.async_create(
                        "vcontrold Daemon wurde erfolgreich gestartet",
                        title="🚀 Daemon Started"
                    )
                )
            else:
                _LOGGER.error("❌ vcontrold Daemon konnte nicht gestartet werden")
        
        async def handle_stop_daemon(call: ServiceCall) -> None:
            """Service zum Stoppen des Daemons."""
            result = await hass.async_add_executor_job(
                daemon_manager.stop_daemon
            )
            
            if result:
                _LOGGER.info("✅ vcontrold Daemon gestoppt")
            else:
                _LOGGER.error("❌ vcontrold Daemon konnte nicht gestoppt werden")
        
        async def handle_check_status(call: ServiceCall) -> None:
            """Service zum Prüfen des Daemon-Status."""
            status = daemon_manager.get_daemon_status()
            health_ok = await daemon_manager.health_check()
            
            status_text = "✅ OK" if health_ok else "⚠️ ERROR"
            message = f"""
**vcontrold Daemon Status: {status_text}**

- Läuft: {'🟢 Ja' if status['running'] else '🔴 Nein'}
- PID: {status['pid'] or 'N/A'}
- Binary: {status['binary_exists']}
- Uptime: {int(status['uptime_seconds']) if status['uptime_seconds'] else 0}s
- Device: {status['config']['device']}
- Listen: {status['config']['host']}:{status['config']['port']}
- Health Checks: {status['health_checks']}
            """
            
            await hass.async_create_task(
                hass.components.persistent_notification.async_create(
                    message.strip(),
                    title="📊 vcontrold Status"
                )
            )
        
        hass.services.async_register(
            DOMAIN,
            "start_daemon",
            handle_start_daemon,
            description="Starte vcontrold Daemon",
        )
        
        hass.services.async_register(
            DOMAIN,
            "stop_daemon",
            handle_stop_daemon,
            description="Stoppe vcontrold Daemon",
        )
        
        hass.services.async_register(
            DOMAIN,
            "check_status",
            handle_check_status,
            description="Prüfe vcontrold Daemon Status",
        )
        
        _LOGGER.debug("Daemon Management Services registriert")
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_TEMP_WW_SOLL,
        handle_set_temp_ww_soll,
        description="Setze Warmwasser-Solltemperatur",
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BETRIEBSART,
        handle_set_betriebsart,
        description="Setze Betriebsart (auto, standby, party, eco)",
    )
    
    _LOGGER.debug("✅ Alle Services registriert")
