import logging
import requests
import json
import datetime

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"

DOMAIN = "renson_ventilation"

RENSON_API_URL = "http://[host]/JSON/Vars/[field]?index0=0&index1=0&index2=0"

SET_MANUAL_LEVEL_FIELD = "Manual level"
TIME_AND_DATE_FIELD = "Date and time"
TIMER_FIELD = "Ventilation timer"

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


manualLevels = ["Off", "Level1", "Level2", "Level3", "Level4"]

class ValueData:
  def __init__(self, value):
    self.Value = value

def getUrl(host, field):
    return RENSON_API_URL.replace("[host]", host).replace("[field]", field.replace(" ", "%20"))

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

    def handle_set_pollution(call):
        day = call.data.get("day_pollution_level", "")
        night = call.data.get("night_pollution_level", "")
        humidityControl = call.data.get("humidity_control", "")
        airqualityControl = call.data.get("airquality_control", "")
        co2Control = call.data.get("co2_control", "")
        co2Threshold = call.data.get("co2_threshold", 0)
        co2Hysteresis = call.data.get("co2_hysteresis", 0)

        if day in manualLevels:
            data = ValueData(day)
            r = requests.post(getUrl(host, DAY_POLLUTION_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        if night in manualLevels:
            data = ValueData(night)
            r = requests.post(getUrl(host, NIGHT_POLLUTION_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        if isinstance(humidityControl, bool):
            data = ValueData(str(int(humidityControl)))
            r = requests.post(getUrl(host, HUMIDITY_CONTROL_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        if isinstance(airqualityControl, bool):
            data = ValueData(str(int(airqualityControl)))
            r = requests.post(getUrl(host, AIR_QUALITY_CONTROL_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        if isinstance(co2Control, bool):
            data = ValueData(str(int(co2Control)))
            r = requests.post(getUrl(host, CO2_CONTROL_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')
        
        if co2Threshold != 0:
            data = ValueData(str(int(co2Threshold)))
            r = requests.post(getUrl(host, CO2_THRESHOLD_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')

        if co2Hysteresis != 0:
            data = ValueData(str(int(co2Hysteresis)))
            r = requests.post(getUrl(host, CO2_HYSTERESIS_FIELD), data = json.dumps(data.__dict__))

            if r.status_code != 200:
                _LOGGER.error('Ventilation unit did not return 200')


    hass.services.register(DOMAIN, "manual_level", handle_manual_level_set)
    hass.services.register(DOMAIN, "sync_time", handle_sync_time)
    hass.services.register(DOMAIN, "timer_level", handle_timer_level)
    hass.services.register(DOMAIN, "set_breeze", handle_set_breeze)
    hass.services.register(DOMAIN, "set_day_night_time", handle_set_time)
    hass.services.register(DOMAIN, "set_pollution_settings", handle_set_pollution)

    return True