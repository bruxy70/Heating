import appdaemon.plugins.hass.hassapi as hass
from enum import Enum
import voluptuous as vol
import voluptuous_helper as vol_help
from datetime import datetime, time, timedelta

"""
Sets the thermostats target temperature and switches heating on and off. Also adds the current temperature and heating mode to the thermostats.
For the documentation see https://github.com/bruxy70/Heating
"""

# Here you can change the modes set in the mode selector (in lower case)
MODE_ON = "on"
MODE_OFF = "off"
MODE_AUTO = "auto"
MODE_ECO = "eco"
MODE_VACATION = "vacation"

HYSTERESIS = 1.0  # Difference between the temperature to turn heating on and off (to avoid frequent switching)
MIN_TEMPERATURE = 10  # Always turn on if teperature is below
LOG_LEVEL = "INFO"

# Other constants - do not change
HVAC_HEAT = "heat"
HVAC_OFF = "off"
ATTR_SWITCH_HEATING = "switch_heating"
ATTR_SOMEBODY_HOME = "somebody_home"
ATTR_HEATING_MODE = "heating_mode"
ATTR_TEMPERATURE_VACATION = "temperature_vacation"
ATTR_ROOMS = "rooms"
ATTR_DAYNIGHT = "day_night"
ATTR_TEMPERATURE_DAY = "temperature_day"
ATTR_TEMPERATURE_NIGHT = "temperature_night"
ATTR_SENSOR = "sensor"
ATTR_THERMOSTATS = "thermostats"
ATTR_NAME = "name"
ATTR_CURRENT_TEMP = "current_temperature"
ATTR_HVAC_MODE = "hvac_mode"
ATTR_HVAC_MODES = "hvac_modes"
ATTR_TEMPERATURE = "temperature"
ATTR_UNKNOWN = "unknown"
ATTR_UNAVAILABLE = "unavailable"


class HeatingControl(hass.Hass):
    def initialize(self):
        """Read all parameters. Set listeners. Initial run"""

        # Configuration validation schema
        ROOM_SCHEMA = vol.Schema(
            {
                vol.Required(ATTR_SENSOR): vol_help.existing_entity_id(self),
                vol.Required(ATTR_DAYNIGHT): vol_help.existing_entity_id(self),
                vol.Required(ATTR_TEMPERATURE_DAY): vol_help.existing_entity_id(self),
                vol.Required(ATTR_TEMPERATURE_NIGHT): vol_help.existing_entity_id(self),
                vol.Required(ATTR_THERMOSTATS): vol.All(
                    vol_help.ensure_list, [vol_help.existing_entity_id(self)]
                ),
            },
        )
        APP_SCHEMA = vol.Schema(
            {
                vol.Required("module"): str,
                vol.Required("class"): str,
                vol.Required(ATTR_ROOMS): vol.All(vol_help.ensure_list, [ROOM_SCHEMA]),
                vol.Required(ATTR_SWITCH_HEATING): vol_help.existing_entity_id(self),
                vol.Required(ATTR_SOMEBODY_HOME): vol_help.existing_entity_id(self),
                vol.Required(ATTR_TEMPERATURE_VACATION): vol_help.existing_entity_id(
                    self
                ),
                vol.Required(ATTR_HEATING_MODE): vol_help.existing_entity_id(self),
            },
            extra=vol.ALLOW_EXTRA,
        )
        __version__ = "0.0.2"  # pylint: disable=unused-variable
        self.__log_level = LOG_LEVEL
        try:
            config = APP_SCHEMA(self.args)
        except vol.Invalid as err:
            self.error(f"Invalid format: {err}", level="ERROR")
            return

        # Read and store configuration
        self.__switch_heating = config.get(ATTR_SWITCH_HEATING)
        self.__rooms = config.get(ATTR_ROOMS)
        self.__somebody_home = config.get(ATTR_SOMEBODY_HOME)
        self.__heating_mode = config.get(ATTR_HEATING_MODE)
        self.__temperature_vacation = config.get(ATTR_TEMPERATURE_VACATION)

        # Listen to events
        self.listen_state(self.somebody_home_changed, self.__somebody_home)
        self.listen_state(self.heating_changed, self.__switch_heating)
        self.listen_state(
            self.vacation_temperature_changed, self.__temperature_vacation
        )
        self.listen_state(self.mode_changed, self.__heating_mode)
        sensors = []
        thermostats = []
        # Listen to events for temperatuyre sensors and thermostats
        for room in self.__rooms:
            self.listen_state(self.daynight_changed, room[ATTR_DAYNIGHT])
            self.listen_state(self.target_changed, room[ATTR_TEMPERATURE_DAY])
            self.listen_state(self.target_changed, room[ATTR_TEMPERATURE_NIGHT])
            if room[ATTR_SENSOR] not in sensors:
                sensor = room[ATTR_SENSOR]
                sensors.append(sensor)
                self.listen_state(self.temperature_changed, sensor)
            for thermostat in room[ATTR_THERMOSTATS]:
                if thermostat not in thermostats:
                    thermostats.append(thermostat)
                    self.listen_state(self.thermostat_changed, thermostat)

        # Initial update
        self.__update_heating()
        self.__update_thermostats()
        self.log("Ready for action...")

    def mode_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: mode changed on/off/auto/eco/vacation"""
        heating = self.is_heating()
        self.__update_heating()
        if heating == self.is_heating():
            self.log("Heating changed, updating thermostats")
            self.__update_thermostats()

    def heating_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: boiler state changed - update information on thermostats"""
        self.__update_thermostats()

    def vacation_temperature_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: target vacation temperature"""
        if self.get_mode() == MODE_VACATION:
            self.__update_heating()
            self.__update_thermostats()

    def somebody_home_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: house is empty / somebody came home"""
        if new.lower() == "on":
            self.log("Somebody came home.", level=self.__log_level)
        elif new.lower() == "off":
            self.log("Nobody home.", level=self.__log_level)
        self.__update_heating(force=True)
        self.__update_thermostats()

    def thermostat_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: make sure thermostats do not get blank"""
        if new is None or new == ATTR_UNKNOWN or new == ATTR_UNAVAILABLE:
            self.__update_thermostats(thermostat_entity=entity)

    def temperature_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: target temperature changed"""
        self.__update_heating()
        self.__update_thermostats(sensor_entity=entity)

    def daynight_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: day/night changed"""
        self.__update_heating()
        self.log("updating daynight")
        for room in self.__rooms:
            if room[ATTR_DAYNIGHT] == entity:
                self.log(f"for sensor {room[ATTR_SENSOR]}")
                self.__update_thermostats(sensor_entity=room[ATTR_SENSOR])

    def target_changed(self, entity, attribute, old, new, kwargs):
        """Event handler: target temperature"""
        self.__update_heating()
        for room in self.__rooms:
            if (
                room[ATTR_TEMPERATURE_DAY] == entity
                or room[ATTR_TEMPERATURE_NIGHT] == entity
            ):
                self.__update_thermostats(sensor_entity=room[ATTR_SENSOR])

    def __check_temperature(self) -> (float, bool, bool):
        """Check temperature of all sensors. Are some bellow? Are all above? What is the minimum temperature"""
        some_below = False
        all_above = True
        minimum = None
        vacation_temperature = float(self.get_state(self.__temperature_vacation))
        for room in self.__rooms:
            sensor_data = self.get_state(room[ATTR_SENSOR])
            if (
                sensor_data is None
                or sensor_data == ATTR_UNKNOWN
                or sensor_data == ATTR_UNAVAILABLE
            ):
                continue
            temperature = float(sensor_data)
            if self.get_mode() == MODE_VACATION:
                target = vacation_temperature
            else:
                target = self.__get_target_room_temp(room)
            if temperature < target:
                all_above = False
            if temperature < (target - HYSTERESIS):
                some_below = True
            if minimum == None or temperature < minimum:
                minimum = temperature
        return minimum, some_below, all_above

    def is_heating(self) -> bool:
        """Is teh boiler heating?"""
        return bool(self.get_state(self.__switch_heating).lower() == "on")

    def is_somebody_home(self) -> bool:
        """Is somebody home?"""
        return bool(self.get_state(self.__somebody_home).lower() == "on")

    def get_mode(self) -> str:
        """Get heating mode off/on/auto/eco/vacation"""
        return self.get_state(self.__heating_mode).lower()

    def __set_heating(self, heat: bool):
        """Set the relay on/off"""
        is_heating = self.is_heating()
        if heat:
            if not is_heating:
                self.log("Turning heating on.", level=self.__log_level)
                self.turn_on(self.__switch_heating)
        else:
            if is_heating:
                self.log("Turning heating off.", level=self.__log_level)
                self.turn_off(self.__switch_heating)

    def __set_thermostat(
        self, entity_id: str, target_temp: float, current_temp: float, mode: str
    ):
        """Set the thermostat attrubutes and state"""
        if target_temp is None:
            target_temp = self.__get_target_temp(termostat=entity_id)
        if current_temp is None:
            current_temp = self.__get_current_temp(termostat=entity_id)
        if mode is None:
            if self.is_heating():
                mode = HVAC_HEAT
            else:
                mode = HVAC_OFF
        self.log(
            f"Updating thermostat {entity_id}: "
            f"temperature {target_temp}, "
            f"mode {mode}, "
            f"current temperature {current_temp}."
        )
        if current_temp is not None and target_temp is not None and mode is not None:
            attrs = {}
            attrs[ATTR_CURRENT_TEMP] = current_temp
            attrs[ATTR_TEMPERATURE] = target_temp
            attrs[ATTR_HVAC_MODE] = mode
            attrs[ATTR_HVAC_MODES] = [HVAC_HEAT, HVAC_OFF]
            self.set_state(entity_id, state=mode, attributes=attrs)
            self.call_service(
                "climate/set_temperature", entity_id=entity_id, temperature=target_temp
            )

    def __get_target_room_temp(self, room) -> float:
        """Returns target room temparture, based on day/night switch (not considering vacation)"""
        if bool(self.get_state(room[ATTR_DAYNIGHT]).lower() == "on"):
            return float(self.get_state(room[ATTR_TEMPERATURE_DAY]))
        else:
            return float(self.get_state(room[ATTR_TEMPERATURE_NIGHT]))

    def __get_target_temp(self, sensor: str = None, termostat: str = None) -> float:
        """Get target temperature (basd on day/night/vacation)"""
        if self.get_mode() == MODE_VACATION:
            return float(self.get_state(self.__temperature_vacation))
        if sensor is None and termostat is None:
            return None
        for room in self.__rooms:
            if sensor is not None:
                if room[ATTR_SENSOR] == sensor:
                    return self.__get_target_room_temp(room)
            else:
                if termostat in room[ATTR_THERMOSTATS]:
                    return self.__get_target_room_temp(room)
        return None

    def __get_current_temp(self, sensor: str = None, termostat: str = None) -> float:
        """Get current temperature (from temperature sensor)"""
        if sensor is not None:
            return float(self.get_state(sensor))
        if termostat is None:
            return None
        for room in self.__rooms:
            if termostat in room[ATTR_THERMOSTATS]:
                return float(self.get_state(room[ATTR_SENSOR]))
        return None

    def __update_heating(self, force: bool = False):
        """Turn boiled on/off"""
        minimum, some_below, all_above = self.__check_temperature()
        mode = self.get_mode()

        if minimum < MIN_TEMPERATURE:
            self.__set_heating(True)
            return
        if mode == MODE_ON:
            self.__set_heating(True)
            return
        if mode == MODE_OFF:
            self.__set_heating(False)
            return
        if mode == MODE_AUTO and self.is_somebody_home():
            self.__set_heating(True)
            return
        if force:
            if self.is_somebody_home():
                if not all_above:
                    self.__set_heating(True)
            else:
                if not some_below:
                    self.__set_heating(False)
        else:
            if self.is_heating():
                if all_above:
                    self.__set_heating(False)
            else:
                if some_below:
                    self.__set_heating(True)

    def __update_thermostats(
        self, thermostat_entity: str = None, sensor_entity: str = None
    ):
        """Set the thermostats target temperature, current temperature and heating mode"""
        vacation = self.get_mode() == MODE_VACATION
        vacation_temperature = float(self.get_state(self.__temperature_vacation))

        for room in self.__rooms:
            if (
                (thermostat_entity is None and sensor_entity is None)
                or (thermostat_entity in room[ATTR_THERMOSTATS])
                or (sensor_entity == room[ATTR_SENSOR])
            ):
                self.log(f"updating sensor {room[ATTR_SENSOR]}")
                temperature = float(self.get_state(room[ATTR_SENSOR]))
                target_temperature = self.__get_target_room_temp(room)
                if self.is_heating():
                    mode = HVAC_HEAT
                else:
                    mode = HVAC_OFF
                for thermostat in room[ATTR_THERMOSTATS]:
                    if vacation:
                        self.__set_thermostat(
                            thermostat, vacation_temperature, temperature, mode
                        )
                    else:
                        self.__set_thermostat(
                            thermostat, target_temperature, temperature, mode
                        )
