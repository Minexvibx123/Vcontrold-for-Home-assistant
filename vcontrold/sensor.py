"""Sensoren für vcontrold Integration."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from . import DOMAIN
from .const import DEFAULT_UPDATE_INTERVAL
from .heating_controller import ViessmannHeatingController

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=DEFAULT_UPDATE_INTERVAL)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richte Sensoren ein."""
    _LOGGER.debug("Richte Sensoren ein")
    
    controller: ViessmannHeatingController = hass.data[DOMAIN][entry.entry_id]
    
    # Erstelle Coordinator für Datenupdates
    coordinator = VcontroledDataUpdateCoordinator(hass, controller)
    
    # Hole erste Daten
    await coordinator.async_config_entry_first_refresh()
    
    # Erstelle Sensor-Entities
    sensors = [
        VcontroledTemperatureSensor(
            coordinator,
            "getTempKessel",
            "Kesseltemperatur",
            "kesseltemperatur",
        ),
        VcontroledTemperatureSensor(
            coordinator,
            "getTempAussen",
            "Außentemperatur",
            "aussentemperatur",
        ),
        VcontroledTemperatureSensor(
            coordinator,
            "getTempWWsoll",
            "Warmwasser-Solltemperatur",
            "warmwasser_solltemperatur",
        ),
        VcontroledTemperatureSensor(
            coordinator,
            "getTempWWist",
            "Warmwasser-Isttemperatur",
            "warmwasser_isttemperatur",
        ),
        VcontroledTemperatureSensor(
            coordinator,
            "getTempVorlaufHK1",
            "Heizkreis Vorlauftemperatur",
            "heizkreis_vorlauftemperatur",
        ),
    ]
    
    async_add_entities(sensors)
    _LOGGER.debug(f"{len(sensors)} Sensoren hinzugefügt")


class VcontroledDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator für Datenupdates."""

    def __init__(self, hass: HomeAssistant, controller: ViessmannHeatingController):
        """Initialisiere Coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="vcontrold",
            update_interval=SCAN_INTERVAL,
        )
        self.controller = controller

    async def _async_update_data(self):
        """Hole Daten von vcontrold."""
        try:
            _LOGGER.debug("Aktualisiere Daten von Heizung")
            
            # Lese alle Sensoren
            data = {}
            sensors = [
                "getTempKessel",
                "getTempAussen",
                "getTempWWsoll",
                "getTempWWist",
                "getTempVorlaufHK1",
            ]
            
            for sensor in sensors:
                try:
                    temp = await self.hass.async_add_executor_job(
                        self.controller.get_temperature, sensor
                    )
                    data[sensor] = temp
                except Exception as e:
                    _LOGGER.warning(f"Fehler beim Auslesen von {sensor}: {e}")
                    data[sensor] = None
            
            return data
            
        except Exception as e:
            _LOGGER.error(f"Fehler beim Aktualisieren der Daten: {e}")
            raise UpdateFailed(f"vcontrold Datenfehler: {e}")


class VcontroledTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Temperatur-Sensor Entity."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VcontroledDataUpdateCoordinator,
        sensor_type: str,
        name: str,
        key: str,
    ):
        """Initialisiere Sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._name = name
        self._key = key
        
        # Eindeutige ID
        self._attr_unique_id = f"vcontrold_{key}"
        self._attr_name = name

    @property
    def native_value(self):
        """Rückgabe aktueller Wert."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._sensor_type)

    @property
    def available(self) -> bool:
        """Prüfe ob Entity verfügbar ist."""
        return (
            self.coordinator.last_update_success
            and self.native_value is not None
        )
