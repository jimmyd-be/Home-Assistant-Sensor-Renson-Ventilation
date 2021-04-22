from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import requests
import logging

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"

META_DATA_URL = "http://[host]/JSON/MetaData"
CO2_URL = "http://[host]/JSON/Vars/CO2?index0=0&index1=0&index2=0"
IAQ_URL = "http://[host]/JSON/Vars/IAQ?index0=0&index1=0&index2=0"
CURRENT_LEVEL_URL = "http://[host]/JSON/Vars/Current%20ventilation%20level?index0=0&index1=0&index2=0"
CURRENT_AIRFLOW_EXTRACT_URL = "http://[host]/JSON/Vars/Current%20ETA%20airflow?index0=0&index1=0&index2=0"
CURRENT_AIRFLOW_INGOING_URL = "http://[host]/JSON/Vars/Current%20SUP%20airflow?index0=0&index1=0&index2=0"
OUTDOOR_TEMP_URL = "http://[host]/JSON/Vars/T21?index0=0&index1=0&index2=0"
INDOOR_TEMP_URL = "http://[host]/JSON/Vars/T11?index0=0&index1=0&index2=0"
FILTER_REMAIN_URL = "http://[host]/JSON/Vars/Filter%20remaining%20time?index0=0&index1=0&index2=0"
HUMIDITY_URL = "http://[host]/JSON/Vars/RH11?index0=0&index1=0&index2=0"
FROST_PROTECTION_URL = "http://[host]/JSON/Vars/Frost%20protection%20active?index0=0&index1=0&index2=0"

QUALITY_GOOD = "Good"
QUALITY_POOR = "Poor"
QUALITY_BAD = "Bad"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=[]): cv.string})

def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOST]

    r =requests.get(META_DATA_URL.replace("[host]", host))

    if r.status_code != 200:
        _LOGGER.error("Failed to establish connection to ventilation unit: %s", host)
        return 1
    _LOGGER.info("Successfully connected to ventilation unit")

    add_entities([
        NormalNumericSensorValue("CO2 value", host, CO2_URL, "carbon_dioxide", "ppm"),
        NormalNumericSensorValue("Air quality value", host, IAQ_URL, "", "ppm"),
        NormalStringSensorValue("Ventilation level", host, CURRENT_LEVEL_URL, "", ""),
        NormalNumericSensorValue("Total airflow out", host, CURRENT_AIRFLOW_EXTRACT_URL, "", "m³/h"),
        NormalNumericSensorValue("Total airflow in", host, CURRENT_AIRFLOW_INGOING_URL, "", "m³/h"),
        NormalNumericSensorValue("Outdoor air temperature", host, OUTDOOR_TEMP_URL, "temperature", "°C"),
        NormalNumericSensorValue("Extract air temperature", host, INDOOR_TEMP_URL, "temperature", "°C"),
        NormalNumericSensorValue("Filter change", host, FILTER_REMAIN_URL, "", "days"),
        NormalNumericSensorValue("Relative humidity", host, HUMIDITY_URL, "humidity", "%"),
        BooleanSensorValue("Frost protection active", host, FROST_PROTECTION_URL),
        QualitySensorValue("CO2", host, CO2_URL),
        QualitySensorValue("Air quality", host, IAQ_URL)
    ])


class QualitySensorValue(Entity):

    def __init__(self, name, host, url):
        self._state = None
        self.sensorName = name
        self.host = host
        self.url = url

    @property
    def name(self):
        return self.sensorName

    @property
    def state(self):
        return self._state

    def update(self):
        r = requests.get(self.url.replace("[host]", self.host))

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

    def __init__(self, name, host, url, deviceClass, unitOfMeasurement):
        self._state = None
        self.sensorName = name
        self.host = host
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
        r = requests.get(self.url.replace("[host]", self.host))

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = round(float(jsonResult["Value"]))

class NormalStringSensorValue(Entity):

    def __init__(self, name, host, url, deviceClass, unitOfMeasurement):
        self._state = None
        self.sensorName = name
        self.host = host
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
        r = requests.get(self.url.replace("[host]", self.host))

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = jsonResult["Value"]


class BooleanSensorValue(Entity):

    def __init__(self, name, host, url):
        self._state = None
        self.sensorName = name
        self.host = host
        self.url = url

    @property
    def name(self):
        return self.sensorName

    @property
    def state(self):
        return self._state

    def update(self):
        r = requests.get(self.url.replace("[host]", self.host))

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = bool(jsonResult["Value"])