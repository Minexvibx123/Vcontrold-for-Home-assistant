"""Config Flow für vcontrold Integration - All-in-One mit erweiterter GUI."""
import logging
from typing import Any, Dict, Optional

import serial
import serial.tools.list_ports
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE,
    CONF_FRAMING,
    DEFAULT_DEVICE,
    DEFAULT_FRAMING,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class VcontroledConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für vcontrold Integration - All-in-One mit GUI."""

    VERSION = 4
    
    def _get_serial_ports(self) -> Dict[str, str]:
        """Hole verfügbare serielle Ports."""
        ports = {}
        for port_info in serial.tools.list_ports.comports():
            ports[port_info.device] = f"{port_info.device} ({port_info.description})"
        return ports
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 1: Daemon-Setup auswählen."""
        if user_input is not None:
            manage_daemon = user_input.get("manage_daemon", True)
            
            if manage_daemon:
                return await self.async_step_ha_managed_device()
            else:
                return await self.async_step_external_connection()
        
        data_schema = vol.Schema(
            {
                vol.Required("manage_daemon", default=True): vol.In({
                    True: "🔧 HA verwaltet Daemon (All-in-One - EMPFOHLEN)",
                    False: "🌐 Externe vcontrold Instanz",
                }),
            }
        )
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            description_placeholders={
                "docs_url": "https://github.com/Minexvibx123/Vcontrold-for-Home-assistant",
            },
        )
    
    async def async_step_ha_managed_device(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 2a: Serielles Gerät für HA-verwalteten Daemon."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            return await self.async_step_ha_managed_network()
        
        serial_ports = self._get_serial_ports()
        if not serial_ports:
            serial_ports = {"/dev/ttyUSB0": "/dev/ttyUSB0"}
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): vol.In(serial_ports),
            }
        )
        
        return self.async_show_form(
            step_id="ha_managed_device",
            data_schema=data_schema,
            description_placeholders={
                "device_help": "Wähle das USB-Seriengerät für die Heizung",
                "help_text": "Falls keine Geräte angezeigt werden, prüfe die Verbindung oder gib manuell ein",
            },
            errors=errors,
        )
    
    async def async_step_ha_managed_network(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 2b: Netzwerk-Einstellungen für HA-verwalteten Daemon."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            return await self.async_step_ha_managed_advanced()
        
        data_schema = vol.Schema(
            {
                vol.Required("host", default="localhost"): str,
                vol.Required("port", default=3002): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1024, max=65535),
                ),
            }
        )
        
        return self.async_show_form(
            step_id="ha_managed_network",
            data_schema=data_schema,
            description_placeholders={
                "host_help": "Hostname oder IP (localhost für lokales Netzwerk)",
                "port_help": "TCP Port für vcontrold Daemon (Standard: 3002)",
            },
            errors=errors,
        )
    
    async def async_step_ha_managed_advanced(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 2c: Erweiterte Einstellungen."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Sammle alle Daten aus vorherigen Steps
            device = self.context.get(CONF_DEVICE, DEFAULT_DEVICE)
            host = self.context.get("host", "localhost")
            port = self.context.get("port", 3002)
            
            # Neue Daten
            update_interval = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            log_level = user_input.get("log_level", "ERROR")
            framing = user_input.get(CONF_FRAMING, DEFAULT_FRAMING)
            
            return self.async_create_entry(
                title="🔧 Viessmann vcontrold (All-in-One)",
                data={
                    "manage_daemon": True,
                    CONF_DEVICE: device,
                    CONF_FRAMING: framing,
                    "host": host,
                    "port": port,
                    "update_interval": update_interval,
                    "log_level": log_level,
                },
            )
        
        data_schema = vol.Schema(
            {
                vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=30, max=300),
                ),
                vol.Required("log_level", default="ERROR"): vol.In({
                    "ERROR": "🔴 ERROR (nur Fehler)",
                    "WARN": "🟡 WARN (Warnungen)",
                    "INFO": "🔵 INFO (Informationen)",
                    "DEBUG": "🟣 DEBUG (Alle Details)",
                }),
                vol.Optional(CONF_FRAMING, default=DEFAULT_FRAMING): vol.In({
                    "kw": "KW Protokoll (Standard - meist kompatibel)",
                    "raw": "Raw Protokoll",
                    "framing": "Framing Protokoll",
                }),
            }
        )
        
        return self.async_show_form(
            step_id="ha_managed_advanced",
            data_schema=data_schema,
            description_placeholders={
                "update_help": "Wie oft Sensoren aktualisiert werden (30-300 Sekunden)",
                "log_help": "Detailliertheitsgrad des Logging",
                "framing_help": "RS232 Protokoll-Variante (KW für die meisten Viessmann)",
            },
            errors=errors,
        )
    
    async def async_step_external_connection(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 2: Externe vcontrold Verbindung."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            host = user_input.get("host")
            port = user_input.get("port", 3002)
            
            # Test Verbindung
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            try:
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    return await self.async_step_external_advanced()
                else:
                    errors["base"] = "cannot_connect"
            except Exception as e:
                errors["base"] = "connection_error"
                _LOGGER.error(f"Verbindungsfehler: {e}")
        
        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("port", default=3002): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=1024, max=65535),
                ),
            }
        )
        
        return self.async_show_form(
            step_id="external_connection",
            data_schema=data_schema,
            description_placeholders={
                "host_help": "IP-Adresse oder Hostname der externen vcontrold Instanz",
                "port_help": "TCP Port (Standard: 3002)",
            },
            errors=errors,
        )
    
    async def async_step_external_advanced(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Step 3: Erweiterte Einstellungen für externe vcontrold."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            host = self.context.get("host", "localhost")
            port = self.context.get("port", 3002)
            
            update_interval = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            
            return self.async_create_entry(
                title=f"🌐 Viessmann vcontrold ({host}:{port})",
                data={
                    "manage_daemon": False,
                    "host": host,
                    "port": port,
                    "update_interval": update_interval,
                },
            )
        
        data_schema = vol.Schema(
            {
                vol.Required("update_interval", default=DEFAULT_UPDATE_INTERVAL): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=30, max=300),
                ),
            }
        )
        
        return self.async_show_form(
            step_id="external_advanced",
            data_schema=data_schema,
            description_placeholders={
                "update_help": "Update-Intervall in Sekunden (30-300)",
            },
            errors=errors,
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """YAML-Import."""
        _LOGGER.debug("Importiere vcontrold Config von YAML")
        
        try:
            return await self.async_step_user(import_data)
        except Exception as e:
            _LOGGER.error(f"YAML Import Fehler: {e}")
            return self.async_abort(reason="unknown_error")


class VcontroledOptionsFlow(config_entries.OptionsFlow):
    """Options Flow für nachträgliche Einstellungen."""

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Haupt-Options Step."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        # Hole aktuelle Werte
        current_data = self.config_entry.data
        manage_daemon = current_data.get("manage_daemon", True)
        
        options_schema_dict = {
            vol.Required(
                "update_interval",
                default=current_data.get("update_interval", DEFAULT_UPDATE_INTERVAL),
            ): vol.All(
                vol.Coerce(int),
                vol.Range(min=30, max=300),
            ),
            vol.Required(
                "log_level",
                default=current_data.get("log_level", "ERROR"),
            ): vol.In({
                "ERROR": "🔴 ERROR",
                "WARN": "🟡 WARN",
                "INFO": "🔵 INFO",
                "DEBUG": "🟣 DEBUG",
            }),
        }
        
        if manage_daemon:
            options_schema_dict[vol.Required(
                "port",
                default=current_data.get("port", 3002),
            )] = vol.All(vol.Coerce(int), vol.Range(min=1024, max=65535))
        
        data_schema = vol.Schema(options_schema_dict)
        
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            description_placeholders={
                "update_help": "Sensor-Update Intervall (Sekunden)",
                "log_help": "Log-Level für Debugging",
            },
        )
