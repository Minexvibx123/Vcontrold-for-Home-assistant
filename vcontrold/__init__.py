"""Viessmann vcontrold Integration - All-in-One Lösung."""
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
from .heating_controller import ViessmannHeatingController

_LOGGER = logging.getLogger(__name__)

PLATFORMS: Final = [Platform.SENSOR]

# Setup für YAML-Konfiguration
CONFIG_SCHEMA = None  # Wird durch Config Flow ersetzt


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Richte Integration ein."""
    _LOGGER.debug("Richte vcontrold Integration (All-in-One) ein")
    
    device = entry.data.get(CONF_DEVICE, DEFAULT_DEVICE)
    framing = entry.data.get(CONF_FRAMING, DEFAULT_FRAMING)
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    
    # Initialisiere Heating Controller
    controller = ViessmannHeatingController(
        port=device,
        framing=framing,
        timeout=10,
        cache_ttl=DEFAULT_CACHE_TTL,
    )
    
    # Prüfe Verfügbarkeit
    try:
        is_connected = await hass.async_add_executor_job(controller.connect)
        if not is_connected:
            _LOGGER.error(f"Heizung nicht erreichbar auf {device}")
            raise ConfigEntryNotReady(f"Heizung nicht erreichbar auf {device}")
        
        # Trenne wieder (wird später bei jedem Update wieder verbunden)
        await hass.async_add_executor_job(controller.disconnect)
    except Exception as e:
        _LOGGER.error(f"Fehler beim Verbindungstest: {e}")
        raise ConfigEntryNotReady(f"Verbindungsfehler: {e}")
    
    # Speichere Controller im hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = controller
    
    # Registriere Services
    _setup_services(hass, controller)
    
    # Lade Plattformen
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info(f"vcontrold Integration erfolgreich eingerichtet (Gerät: {device})")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Entlade Integration."""
    _LOGGER.debug("Entlade vcontrold Integration")
    
    # Entlade Plattformen
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        controller: ViessmannHeatingController = hass.data[DOMAIN].pop(entry.entry_id)
        controller.cleanup()
    
    return unload_ok


def _setup_services(hass: HomeAssistant, controller: ViessmannHeatingController):
    """Registriere Custom Services."""
    
    async def handle_set_temp_ww_soll(call: ServiceCall) -> None:
        """Handle Service zum Setzen der Warmwasser-Solltemperatur."""
        temp = call.data.get(ATTR_TEMPERATURE)
        
        if not isinstance(temp, (int, float)) or temp < MIN_TEMP or temp > MAX_TEMP:
            _LOGGER.error(f"Ungültige Temperatur: {temp}. Bereich: {MIN_TEMP}-{MAX_TEMP}°C")
            return
        
        result = await hass.async_add_executor_job(
            controller.set_temperature, "setTempWWsoll", float(temp)
        )
        
        if result:
            _LOGGER.info(f"Warmwasser-Solltemperatur auf {temp}°C gesetzt")
        else:
            _LOGGER.error(f"Fehler beim Setzen der Warmwasser-Solltemperatur")
    
    async def handle_set_betriebsart(call: ServiceCall) -> None:
        """Handle Service zum Setzen der Betriebsart."""
        mode = call.data.get(ATTR_MODE, "auto")
        
        if mode not in VALID_MODES:
            _LOGGER.error(f"Ungültige Betriebsart: {mode}. Gültig: {VALID_MODES}")
            return
        
        result = await hass.async_add_executor_job(
            controller.set_operating_mode, mode
        )
        
        if result:
            _LOGGER.info(f"Betriebsart auf {mode} gesetzt")
        else:
            _LOGGER.error(f"Fehler beim Setzen der Betriebsart")
    
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
    
    _LOGGER.debug("Services registriert")
