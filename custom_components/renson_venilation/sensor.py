from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import requests
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "renson_ventilation"

CONF_HOST = "host"

RENSON_API_URL = "http://[host]/JSON/Vars/[field]?index0=0&index1=0&index2=0"
META_DATA_URL = "http://[host]/JSON/MetaData"
CO2_FIELD = "CO2"
AIR_QUALITY_FIELD = "IAQ"
CURRENT_LEVEL_FIELD = "Current%20ventilation%20level"
CURRENT_AIRFLOW_EXTRACT_FIELD = "Current%20ETA%20airflow"
CURRENT_AIRFLOW_INGOING_FIELD = "Current%20SUP%20airflow"
OUTDOOR_TEMP_FIELD = "T21"
INDOOR_TEMP_FIELD = "T11"
FILTER_REMAIN_FIELD = "Filter%20remaining%20time"
HUMIDITY_FIELD = "RH11"
FROST_PROTECTION_FIELD = "Frost%20protection%20active"

QUALITY_GOOD = "Good"
QUALITY_POOR = "Poor"
QUALITY_BAD = "Bad"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=[]): cv.string})

def getUrl(host, field):
    return RENSON_API_URL.replace("[host]", host).replace("[field]", field)

def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOST]

    r =requests.get(META_DATA_URL.replace("[host]", host))

    if r.status_code != 200:
        _LOGGER.error("Failed to establish connection to ventilation unit: %s", host)
        return 1
    _LOGGER.info("Successfully connected to ventilation unit")

    add_entities([
        NormalNumericSensorValue("CO2 value", getUrl(host, CO2_FIELD), "carbon_dioxide", "ppm"),
        NormalNumericSensorValue("Air quality value", getUrl(host, AIR_QUALITY_FIELD), "", "ppm"),
        LevelSensorValue("Ventilation level", getUrl(host, CURRENT_LEVEL_FIELD), "", ""),
        NormalNumericSensorValue("Total airflow out", getUrl(host, CURRENT_AIRFLOW_EXTRACT_FIELD), "", "m³/h"),
        NormalNumericSensorValue("Total airflow in", getUrl(host, CURRENT_AIRFLOW_INGOING_FIELD), "", "m³/h"),
        NormalNumericSensorValue("Outdoor air temperature", getUrl(host, OUTDOOR_TEMP_FIELD), "temperature", "°C"),
        NormalNumericSensorValue("Extract air temperature", getUrl(host, INDOOR_TEMP_FIELD), "temperature", "°C"),
        NormalNumericSensorValue("Filter change", getUrl(host, FILTER_REMAIN_FIELD), "", "days"),
        NormalNumericSensorValue("Relative humidity", getUrl(host, HUMIDITY_FIELD), "humidity", "%"),
        BooleanSensorValue("Frost protection active", getUrl(host, FROST_PROTECTION_FIELD)),
        QualitySensorValue("CO2", getUrl(host, CO2_FIELD)),
        QualitySensorValue("Air quality", getUrl(host, AIR_QUALITY_FIELD))
    ])


class QualitySensorValue(Entity):

    def __init__(self, name, url):
        self._state = None
        self.sensorName = name
        self.url = url

    @property
    def name(self):
        return self.sensorName

    @property
    def state(self):
        return self._state

    def update(self):
        r = requests.get(self.url)

        if r.status_code == 200:
            jsonResult = r.json()
            value = round(float(jsonResult["Value"]))

            if value < 950:
                self._state = QUALITY_GOOD
            elif value < 1500:
                self._state = QUALITY_POOR
            else:
                self._state = QUALITY_BAD

class NormalNumericSensorValue(Entity):

    def __init__(self, name, url, deviceClass, unitOfMeasurement):
        self._state = None
        self.sensorName = name
        self.url = url
        self.deviceClass = deviceClass
        self.unitOfMeasurement = unitOfMeasurement

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

    def update(self):
        r = requests.get(self.url)

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = round(float(jsonResult["Value"]))

class LevelSensorValue(Entity):

    def __init__(self, name, url, deviceClass, unitOfMeasurement):
        self._state = None
        self.sensorName = name
        self.url = url
        self.deviceClass = deviceClass
        self.unitOfMeasurement = unitOfMeasurement

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

    def update(self):
        r = requests.get(self.url)

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = jsonResult["Value"]


class BooleanSensorValue(Entity):

    def __init__(self, name, url):
        self._state = None
        self.sensorName = name
        self.url = url

    @property
    def name(self):
        return self.sensorName

    @property
    def state(self):
        return self._state

    def update(self):
        r = requests.get(self.url)

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = bool(jsonResult["Value"])