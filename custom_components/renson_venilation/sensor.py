from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from datetime import timedelta
import voluptuous as vol
import requests
import logging
import aiohttp
import asyncio
import json

_LOGGER = logging.getLogger(__name__)

DOMAIN = "renson_ventilation"

CONF_HOST = "host"

DATA_URL = "http://[host]/JSON/ModifiedItems?wsn=150324488709"

CO2_FIELD = "CO2"
AIR_QUALITY_FIELD = "IAQ"
CURRENT_LEVEL_FIELD = "Current ventilation level"
CURRENT_AIRFLOW_EXTRACT_FIELD = "Current ETA airflow"
CURRENT_AIRFLOW_INGOING_FIELD = "Current SUP airflow"
OUTDOOR_TEMP_FIELD = "T21"
INDOOR_TEMP_FIELD = "T11"
FILTER_REMAIN_FIELD = "Filter remaining time"
HUMIDITY_FIELD = "RH11"
FROST_PROTECTION_FIELD = "Frost protection active"

MANUAL_LEVEL_FIELD = "Manual level"
TIME_AND_DATE_FIELD = "Date and time"

BREEZE_TEMPERATURE_FIELD = "Breeze activation temperature"
BREEZE_ENABLE_FIELD = "Breeze enable"
BREEZE_LEVEL_FIELD = "Breeze level"

DAYTIME_FIELD = "Start daytime"
NIGTHTIME_FIELD = "Start night-time"

DAY_POLLUTION_FIELD = "Day pollution-triggered ventilation level"
NIGHT_POLLUTION_FIELD ="Night pollution-triggered ventilation level"
HUMIDITY_CONTROL_FIELD = "Trigger internal pollution alert on RH"
AIR_QUALITY_CONTROL_FIELD = "Trigger internal pollution alert on IAQ"
CO2_CONTROL_FIELD = "Trigger internal pollution alert on CO2"
CO2_THRESHOLD_FIELD = "CO2 threshold"
CO2_HYSTERESIS_FIELD = "CO2 hysteresis"
BREEZE_MET_FIELD = "Breeze conditions met"

PREHEATER_FIELD = "Preheater enabled"
BYPASS_TEMPERATURE_FIELD = "Bypass activation temperature"
BYPASS_LEVEL_FIELD = "Bypass level"

QUALITY_GOOD = "Good"
QUALITY_POOR = "Poor"
QUALITY_BAD = "Bad"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=[]): cv.string})

async def getFieldValue(coordinator, field):
    for data in coordinator.data:
        if data['Name'] == field:
            _LOGGER.info(data['Value'])
            return data['Value']

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    host = config[CONF_HOST]
    
    async def async_update_data():
        _LOGGER.info("update data")
        async with aiohttp.ClientSession() as session:
            async with session.get(DATA_URL.replace("[host]", host)) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    raise UpdateFailed(f"Error communicating with API: {response.status}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="sensor",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )

    #
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        SensorValue(coordinator, "CO2", CO2_FIELD, "", "", "quality"),
        SensorValue(coordinator, "Air quality", AIR_QUALITY_FIELD, "", "", "quality"),
        SensorValue(coordinator, "CO2 value", CO2_FIELD, "carbon_dioxide", "ppm", "numeric"),
        SensorValue(coordinator, "Air quality value", AIR_QUALITY_FIELD, "", "ppm", "numeric"),
        SensorValue(coordinator, "Ventilation level", CURRENT_LEVEL_FIELD, "", "", "string"),
        SensorValue(coordinator, "Total airflow out", CURRENT_AIRFLOW_EXTRACT_FIELD, "", "m³/h", "numeric"),
        SensorValue(coordinator, "Total airflow in", CURRENT_AIRFLOW_INGOING_FIELD, "", "m³/h", "numeric"),
        SensorValue(coordinator, "Outdoor air temperature", OUTDOOR_TEMP_FIELD, "temperature", "°C", "numeric"),
        SensorValue(coordinator, "Extract air temperature", INDOOR_TEMP_FIELD, "temperature", "°C", "numeric"),
        SensorValue(coordinator, "Filter change", FILTER_REMAIN_FIELD, "", "days", "numeric"),
        SensorValue(coordinator, "Relative humidity", HUMIDITY_FIELD, "humidity", "%", "numeric"),
        SensorValue(coordinator, "Frost protection active", FROST_PROTECTION_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "Manual level", MANUAL_LEVEL_FIELD, "", "", "string"),
        SensorValue(coordinator, "System time", TIME_AND_DATE_FIELD, "timestamp", "", "string"),
        SensorValue(coordinator, "Breeze temperature", BREEZE_TEMPERATURE_FIELD, "temperature", "°C", "numeric"),
        SensorValue(coordinator, "Breeze enabled", BREEZE_ENABLE_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "Breeze level", BREEZE_LEVEL_FIELD, "", "", "string"),
        SensorValue(coordinator, "Breeze conditions met", BREEZE_MET_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "Start day time", DAYTIME_FIELD, "", "", "string"),
        SensorValue(coordinator, "Start night time", NIGTHTIME_FIELD, "", "", "string"),
        SensorValue(coordinator, "Day pollution level", DAY_POLLUTION_FIELD, "", "", "string"),
        SensorValue(coordinator, "Night pollution level", NIGHT_POLLUTION_FIELD, "", "", "string"),
        SensorValue(coordinator, "Humidity control enabled", HUMIDITY_CONTROL_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "Air quality control enabled", AIR_QUALITY_CONTROL_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "CO2 control enabled", CO2_CONTROL_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "CO2 threshold", CO2_THRESHOLD_FIELD, "", "ppm", "numeric"),
        SensorValue(coordinator, "CO2 hysteresis", CO2_HYSTERESIS_FIELD, "", "ppm", "numeric"),
        SensorValue(coordinator, "Preheater enabled", PREHEATER_FIELD, "", "", "boolean"),
        SensorValue(coordinator, "Bypass activation temperature", BYPASS_TEMPERATURE_FIELD, "temperature", "°C", "numeric"),
        SensorValue(coordinator, "Bypass level", BYPASS_LEVEL_FIELD, "power_factor", "%", "numeric")
    ])

class SensorValue(CoordinatorEntity):

    def __init__(self, coordinator, name, field, deviceClass, unitOfMeasurement, dataType):
        super().__init__(coordinator)

        self._state = None
        self.sensorName = name
        self.field = field
        self.deviceClass = deviceClass
        self.unitOfMeasurement = unitOfMeasurement
        self.datatYPE = dataType

    @property
    def name(self):
        return self.sensorName

    @property
    def device_class(self):
        return self.deviceClass

    @property
    def unit_of_measurement(self):
        return self.unitOfMeasurement

    @property
    def state(self):
        return self._state

    async def async_update(self):
        _LOGGER.info("update sensor state")
        if dataType == "numeric":
            self._state = round(float(await getFieldValue(self.coordinator, field)))
        elif dataType == "string":
            self._state = await getFieldValue(self.coordinator, field)
        elif dataType == "boolean":
            self._state = bool(int(await getFieldValue(self.coordinator, field)))
        elif dataType == "quality":
            value = round(float(await getFieldValue(self.coordinator, field)))
            if value < 950:
                self._state = QUALITY_GOOD
            elif value < 1500:
                self._state = QUALITY_POOR
            else:
                self._state = QUALITY_BAD
