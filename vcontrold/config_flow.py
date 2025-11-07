"""Config Flow für vcontrold Integration - All-in-One."""
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
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class VcontroledConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für vcontrold Integration - All-in-One."""

    VERSION = 3
    
    def _get_serial_ports(self) -> Dict[str, str]:
        """Hole verfügbare serielle Ports."""
        ports = {}
        for port_info in serial.tools.list_ports.comports():
            ports[port_info.device] = f"{port_info.device} ({port_info.description})"
        return ports
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handling User Step - Daemon-Setup auswählen."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            manage_daemon = user_input.get("manage_daemon", True)
            
            if manage_daemon:
                return await self.async_step_ha_managed()
            else:
                return await self.async_step_external()
        
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
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/Minexvibx123/Vcontrold-for-Home-assistant",
            },
        )
    
    async def async_step_ha_managed(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Home Assistant verwaltet Daemon."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            device = user_input.get(CONF_DEVICE, DEFAULT_DEVICE)
            host = user_input.get("host", "localhost")
            port = user_input.get("port", 3002)
            
            # Erstelle Config Entry
            return self.async_create_entry(
                title="🔧 Viessmann vcontrold (All-in-One)",
                data={
                    "manage_daemon": True,
                    CONF_DEVICE: device,
                    CONF_FRAMING: user_input.get(CONF_FRAMING, DEFAULT_FRAMING),
                    "host": host,
                    "port": port,
                },
            )
        
        serial_ports = self._get_serial_ports()
        if not serial_ports:
            serial_ports = {"/dev/ttyUSB0": "/dev/ttyUSB0"}
        
        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): vol.In(serial_ports),
                vol.Required("host", default="localhost"): str,
                vol.Required("port", default=3002): int,
                vol.Optional(CONF_FRAMING, default=DEFAULT_FRAMING): vol.In(
                    ["raw", "framing", "kw"]
                ),
            }
        )
        
        return self.async_show_form(
            step_id="ha_managed",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device_help": "Serielles Gerät für Heizung",
                "host_help": "TCP Host (localhost für lokales Netzwerk)",
                "port_help": "TCP Port (default: 3002)",
            },
        )
    
    async def async_step_external(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Externe vcontrold Instanz."""
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
                    return self.async_create_entry(
                        title=f"🌐 Viessmann vcontrold ({host}:{port})",
                        data={
                            "manage_daemon": False,
                            "host": host,
                            "port": port,
                        },
                    )
                else:
                    errors["base"] = "cannot_connect"
            except Exception as e:
                errors["base"] = "connection_error"
                _LOGGER.error(f"Verbindungsfehler: {e}")
        
        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("port", default=3002): int,
            }
        )
        
        return self.async_show_form(
            step_id="external",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "host_help": "IP-Adresse oder Hostname",
            },
        )

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """YAML-Import."""
        _LOGGER.debug(f"Importiere vcontrold Config von YAML")
        
        try:
            return await self.async_step_user(import_data)
        except Exception as e:
            _LOGGER.error(f"YAML Import Fehler: {e}")
            return self.async_abort(reason="unknown_error")
