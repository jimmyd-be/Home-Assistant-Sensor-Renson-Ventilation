
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

For configuring the build in services:
```yaml
# Example configuration.yaml entry
renson_ventilation:
  host: 127.0.0.1
```

## Features
- Set the manual level of the ventilation system (manual_level service).
- Gets all the data from the ventilation system that can be viewed in the Endura Delta application on the tab 'Data'.