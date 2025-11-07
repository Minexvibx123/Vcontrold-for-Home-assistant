"""Config Flow für vcontrold Integration."""
import logging
from typing import Any, Dict, Optional

import serial
import serial.tools.list_ports
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE,
    CONF_FRAMING,
    DEFAULT_DEVICE,
    DEFAULT_FRAMING,
    DOMAIN,
)
from .heating_controller import ViessmannHeatingController

_LOGGER = logging.getLogger(__name__)


class VcontroledConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für vcontrold Integration - All-in-One."""

    VERSION = 2
    
    def _get_serial_ports(self) -> Dict[str, str]:
        """Hole verfügbare serielle Ports."""
        ports = {}
        for port_info in serial.tools.list_ports.comports():
            ports[port_info.device] = f"{port_info.device} ({port_info.description})"
        return ports
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handling User Step - Benutzer-Konfiguration."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Validiere Eingabe
            try:
                device = user_input.get(CONF_DEVICE, DEFAULT_DEVICE)
                framing = user_input.get(CONF_FRAMING, DEFAULT_FRAMING)
                
                # Test Verbindung
                controller = ViessmannHeatingController(
                    port=device,
                    framing=framing,
                )
                
                is_connected = await self.hass.async_add_executor_job(
                    controller.connect
                )
                
                if not is_connected:
                    errors["base"] = "cannot_connect"
                    _LOGGER.error(f"Heizung nicht erreichbar auf {device}")
                else:
                    # Cleanup
                    await self.hass.async_add_executor_job(
                        controller.disconnect
                    )
                    
                    # Erstelle Config Entry
                    return self.async_create_entry(
                        title=f"Viessmann Heizung ({device})",
                        data={
                            CONF_DEVICE: device,
                            CONF_FRAMING: framing,
                        },
                    )
            
            except Exception as e:
                _LOGGER.error(f"Config Flow Fehler: {e}")
                errors["base"] = "unknown"
        
        # Hole verfügbare Ports
        serial_ports = self._get_serial_ports()
        
        if not serial_ports:
            return self.async_abort(reason="no_ports_found")
        
        # Schema für Benutzereingabe
        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): vol.In(serial_ports),
                vol.Optional(CONF_FRAMING, default=DEFAULT_FRAMING): vol.In(
                    ["raw", "framing", "kw"]
                ),
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

    async def async_step_import(self, import_data: Dict[str, Any]) -> FlowResult:
        """Handling Import Step - YAML-Import."""
        _LOGGER.debug(f"Importiere vcontrold Config von YAML: {import_data}")
        
        try:
            return await self.async_step_user(import_data)
        except Exception as e:
            _LOGGER.error(f"YAML Import Fehler: {e}")
            return self.async_abort(reason="unknown_error")
