
# Home Assistant Sensor for Renson ventilation

This is an unofficial way of getting data from the ventilation system and changing some settings of the ventilation system.

Tested with Endura Delta on firmware version 0.0.67

### Installation

Copy this folder to `<config_dir>/custom_components/example_sensor/`.

Add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry
sensor:
  - platform: renson_ventilation
    host: 127.0.0.1
```
