# Heating

This is an AppDaemon automation of my heating in Home Assistant, as explained in this video on YouTube. It sets the thermostat's target temperature and switches heating on and off. It also adds the current temperature and heating mode to the thermostat entities.

# Installation

1. This requires AppDeamon installed and configured (follow the documentation on their web site).
2. Make sure that `voluptuous` and `datetime` are incuded in the `python_packages` option
3. Copy the content of the appdaemon directory from this repository to your home assistant `/config/appdaemon` folder
4. Add configuration to your Home Assistant's `/config/appdaemon/apps/apps.yaml`


# Configuration

This is the configuration that goes into `/config/appdaemon/apps/apps.yaml`

## Example:
```yaml
heating-control:
  module: heating-control
  class: HeatingControl
  switch_heating: switch.heating
  somebody_home: input_boolean.somebody_home
  heating_mode: input_select.heating_mode
  temperature_vacation: input_number.temperature_vacation
  rooms:
  - sensor: sensor.teplota_living_toom
    day_night: input_boolean.livingroom_day_night
    temperature_day: input_number.livingroom_day
    temperature_night: input_number.livingroom_night
    thermostats:
    - climate.termostat_living_room
    - climate.termostat_dining_area
```

## Parameters:
