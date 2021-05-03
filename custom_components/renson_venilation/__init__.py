import logging
import requests
import json
import datetime

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"

DOMAIN = "renson_ventilation"

SET_MANUAL_LEVEL_URL = "http://[host]/JSON/Vars/Manual%20level?index0=0&index1=0&index2=0"
TIME_AND_DATE_URL = "http://[host]/JSON/Vars/Date%20and%20time?index0=0&index1=0&index2=0"
TIMER_URL = "http://[host]/JSON/Vars/Ventilation%20timer?index0=0&index1=0&index2=0"

BREEZE_TEMPERATURE_URL = "http://[host]/JSON/Vars/Breeze%20activation%20temperature?index0=0&index1=0&index2=0"
BREEZE_ENABLE_URL = "http://[host]/JSON/Vars/Breeze%20enable?index0=0&index1=0&index2=0"
BREEZE_LEVEL_URL = "http://[host]/JSON/Vars/Breeze%20level?index0=0&index1=0&index2=0"

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

    def handle_sync_time(call):
        response = requests.get(TIME_AND_DATE_URL.replace("[host]", host))
        
        if response.status_code == 200:
            jsonResult = response.json()
            deviceTime = datetime.datetime.strptime(jsonResult["Value"], "%d %b %Y %H:%M")
            currentTime = datetime.datetime.now()

            if currentTime != deviceTime:
                data = ValueData(currentTime.strftime("%d %b %Y %H:%M").lower())
                r = requests.post(TIME_AND_DATE_URL.replace("[host]", host), data = json.dumps(data.__dict__))
        else:
            _LOGGER.error('Ventilation unit did not return 200')

    def handle_timer_level(call):
        level = call.data.get("timer_level", "Level1")
        time = call.data.get("time", 0)

        if level in manualLevels:
            data = ValueData(str(time) + " min " + level)
            r = requests.post(TIMER_URL.replace("[host]", host), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        else:
            _LOGGER.error('Level does not exist', call.data.get("timer_level", "Off"))
    
    def handle_set_breeze(call):
        level = call.data.get("breeze_level", "")
        temperature = call.data.get("temperature", 0)
        activated = call.data.get("activate", False)

        if level in manualLevels and level != "":
            data = ValueData(level)
            r = requests.post(BREEZE_LEVEL_URL.replace("[host]", host), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        else:
            _LOGGER.error('Level does not exist', call.data.get("timer_level", "Off"))

        if temperature != 0:
            data = ValueData(str(temperature))
            r = requests.post(BREEZE_TEMPERATURE_URL.replace("[host]", host), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        data = ValueData(str(int(activated)))
        r = requests.post(BREEZE_ENABLE_URL.replace("[host]", host), data = json.dumps(data.__dict__))

        if r.status_code != 200:
            _LOGGER.error('Ventilation unit did not return 200')


    hass.services.register(DOMAIN, "manual_level", handle_manual_level_set)
    hass.services.register(DOMAIN, "sync_time", handle_sync_time)
    hass.services.register(DOMAIN, "timer_level", handle_timer_level)
    hass.services.register(DOMAIN, "set_breeze", handle_set_breeze)

    return True