import logging
import requests
import json

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"

DOMAIN = "renson_ventilation"

SET_MANUAL_LEVEL_URL = "http://[host]/JSON/Vars/Manual%20level?index0=0&index1=0&index2=0"

manualLevels = ["Off", "Level1", "Level2", "Level3", "Level4"]

class ValueData:
  def __init__(self, value):
    self.Value = value

def setup(hass, config):
    host = config[DOMAIN][CONF_HOST]

    def handle_manual_level_set(call):

        level = call.data.get("manual_level", "Off")

        data = ValueData(level)

        if level in manualLevels:
            r = requests.post(SET_MANUAL_LEVEL_URL.replace("[host]", host), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        else:
            _LOGGER.error('Level does not exist', call.data.get("manual_level", "Off"))

    hass.services.register(DOMAIN, "manual_level", handle_manual_level_set)

    return True