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

STATE_LEVEL1 = "level1"
STATE_LEVEL2 = "level2"
STATE_LEVEL3 = "level3"
STATE_LEVEL4 = "level4"

QUALITY_GOOD = "good"
QUALITY_OK = "ok"
QUALITY_BAD = "bad"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST, default=[]): cv.string})

def setup_platform(hass, config, add_entities, discovery_info=None):
    host = config[CONF_HOST]

    r =requests.get(META_DATA_URL.replace("[host]", host))

    if r.status_code != 200:
        _LOGGER.error("Failed to establish connection to ventilation unit: %s", host)
        return 1
    _LOGGER.info("Successfully connected to ventilation unit")

    add_entities([NormalNumericSensorValue("CO2", host, CO2_URL),
    NormalNumericSensorValue("Air quality", host, IAQ_URL),
    NormalStringSensorValue("Ventilation level", host, CURRENT_LEVEL_URL),
    NormalNumericSensorValue("Total airflow out", host, CURRENT_AIRFLOW_EXTRACT_URL),
    NormalNumericSensorValue("Total airflow in", host, CURRENT_AIRFLOW_INGOING_URL)])



class NormalNumericSensorValue(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, host, url):
        """Initialize the sensor."""
        self._state = None
        self.sensorName = name
        self.host = host
        self.url = url

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensorName

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""

        r = requests.get(self.url.replace("[host]", self.host))

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = int(float(jsonResult["Value"]))

class NormalStringSensorValue(Entity):
    """Representation of a Sensor."""

    def __init__(self, name, host, url):
        """Initialize the sensor."""
        self._state = None
        self.sensorName = name
        self.host = host
        self.url = url

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.sensorName

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self):
        """Fetch new state data for the sensor."""

        r = requests.get(self.url.replace("[host]", self.host))

        if r.status_code == 200:
            jsonResult = r.json()
            self._state = jsonResult["Value"]