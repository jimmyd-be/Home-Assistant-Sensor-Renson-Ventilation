[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)



# Home Assistant Sensor for Renson ventilation

> :warning: **This integration is already available to the official Home Assistant integrations. Most of the features of this plugin are already in the official ones. Missing features will be add in the future. It is better to use that integration instead of this one. The official integration will be developed further in the future.


This is an unofficial way of getting data from the ventilation system and changing some settings of the ventilation system.
I will try to implement all features of the Endura delta app inside the integration of Home Assistant.

Tested with Endura Delta on firmware version 0.0.67

### Installation

Use HACS to install the integration or copy this folder to `<config_dir>/custom_components/example_sensor/`.

#### Recommended configuration
It is recommended to configure the integration using the UI.

#### Manual configuration

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
- Configure intengration with UI
- Set the manual level of the ventilation system.
- Set ventilation timer
- Set breeze feature settings and active/deactive breeze function
- Gets all the data from the ventilation system that can be viewed in the Endura Delta application on the tab 'Data'.
- Synchronize date and time with computer and ventilation system
- Set start daytime and nighttime time
- Set pollution settings
