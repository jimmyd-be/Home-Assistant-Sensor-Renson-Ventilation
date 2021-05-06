import logging
import requests
import json
import datetime

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"

DOMAIN = "renson_ventilation"

RENSON_API_URL = "http://[host]/JSON/Vars/[field]?index0=0&index1=0&index2=0"

SET_MANUAL_LEVEL_FIELD = "Manual%20level"
TIME_AND_DATE_FIELD = "Date%20and%20time"
TIMER_FIELD = "Ventilation%20timer"

BREEZE_TEMPERATURE_FIELD = "Breeze%20activation%20temperature"
BREEZE_ENABLE_FIELD = "Breeze%20enable"
BREEZE_LEVEL_FIELD = "Breeze%20level"

DAYTIME_FIELD = "Start%20daytime"
NIGTHTIME_FIELD = "Start%20night-time"


manualLevels = ["Off", "Level1", "Level2", "Level3", "Level4"]

class ValueData:
  def __init__(self, value):
    self.Value = value

def getUrl(host, field):
    return RENSON_API_URL.replace("[host]", host).replace("[field]", field)

def setup(hass, config):
    host = config[DOMAIN][CONF_HOST]

    def handle_manual_level_set(call):

        level = call.data.get("manual_level", "Off")

        data = ValueData(level)

        if level in manualLevels:
            r = requests.post(getUrl(host, SET_MANUAL_LEVEL_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        else:
            _LOGGER.error('Level does not exist', call.data.get("manual_level", "Off"))

    def handle_sync_time(call):
        response = requests.get(getUrl(host, TIME_AND_DATE_FIELD))
        
        if response.status_code == 200:
            jsonResult = response.json()
            deviceTime = datetime.datetime.strptime(jsonResult["Value"], "%d %b %Y %H:%M")
            currentTime = datetime.datetime.now()

            if currentTime != deviceTime:
                data = ValueData(currentTime.strftime("%d %b %Y %H:%M").lower())
                r = requests.post(getUrl(host, TIME_AND_DATE_FIELD), data = json.dumps(data.__dict__))
        else:
            _LOGGER.error('Ventilation unit did not return 200')

    def handle_timer_level(call):
        level = call.data.get("timer_level", "Level1")
        time = call.data.get("time", 0)

        if level in manualLevels:
            data = ValueData(str(time) + " min " + level)
            r = requests.post(getUrl(host, TIMER_FIELD), data = json.dumps(data.__dict__))

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
            r = requests.post(getUrl(host, BREEZE_LEVEL_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        else:
            _LOGGER.error('Level does not exist', call.data.get("timer_level", "Off"))

        if temperature != 0:
            data = ValueData(str(temperature))
            r = requests.post(getUrl(host, BREEZE_TEMPERATURE_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        data = ValueData(str(int(activated)))
        r = requests.post(getUrl(host, BREEZE_ENABLE_FIELD), data = json.dumps(data.__dict__))

        if r.status_code != 200:
            _LOGGER.error('Ventilation unit did not return 200')

    def handle_set_time(call):
        day = call.data.get("day", "7:00")
        nigth = call.data.get("night", "22:00")

        data = ValueData(day)
        r = requests.post(getUrl(host, DAYTIME_FIELD), data = json.dumps(data.__dict__))

        if r.status_code != 200:
            _LOGGER.error('Start daytime cannot be set')

        data = ValueData(nigth)
        r = requests.post(getUrl(host, NIGTHTIME_FIELD), data = json.dumps(data.__dict__))

        if r.status_code != 200:
            _LOGGER.error('Start nigthtime cannot be set')


    hass.services.register(DOMAIN, "manual_level", handle_manual_level_set)
    hass.services.register(DOMAIN, "sync_time", handle_sync_time)
    hass.services.register(DOMAIN, "timer_level", handle_timer_level)
    hass.services.register(DOMAIN, "set_breeze", handle_set_breeze)
    hass.services.register(DOMAIN, "set_day_night_time", handle_set_time)

    return True