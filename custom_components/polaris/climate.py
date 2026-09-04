"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.components.climate import (
    DOMAIN,
    ATTR_HVAC_MODE,
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .common import PolarisBaseEntity
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    CLIMATES,
    CLIMATES_200,
    AIRCLEANER,
    AIRCLEANER_EAP,
    CLIMATES_HEATER,
    CLIMATES_AIRCONDITIONER,
    CLIMATES_THERMOSTAT,
    PolarisClimateEntityDescription,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
    POLARIS_AIRCLEANER_EAP_TYPE,
    POLARIS_HEATER_TYPE,
    POLARIS_AIRCONDITIONER_TYPE,
    POLARIS_THERMOSTAT_TYPE,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:

    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    climateList = []
    
    if (device_type in POLARIS_CLIMATE_TYPE):
        # Create humidifier  
        if (device_type == "859"):
            CLIMATES_LC = copy.deepcopy(CLIMATES_200)
        else:
            CLIMATES_LC = copy.deepcopy(CLIMATES)
        for description in CLIMATES_LC:
            description.mqttTopicStateTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateTemperature}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_AIRCLEANER_TYPE):
        # Create humidifier  
        AIRCLEANER_LC = copy.deepcopy(AIRCLEANER)
        for description in AIRCLEANER_LC:
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_AIRCLEANER_EAP_TYPE):
        # Create aircleaner  
        AIRCLEANER_EAP_LC = copy.deepcopy(AIRCLEANER_EAP)
        for description in AIRCLEANER_EAP_LC:
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HEATER_TYPE):
        # Create Heater  
        CLIMATES_HEATER_LC = copy.deepcopy(CLIMATES_HEATER)
        for description in CLIMATES_HEATER_LC:
            description.mqttTopicStateTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateTemperature}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_AIRCONDITIONER_TYPE):
        # Create AIRCONDITIONER
        CLIMATES_AIRCONDITIONER_LC = copy.deepcopy(CLIMATES_AIRCONDITIONER)
        for description in CLIMATES_AIRCONDITIONER_LC:
            description.mqttTopicStateTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateTemperature}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.mqttTopicStateSwingMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateSwingMode}"
            description.mqttTopicCommandSwingMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandSwingMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_THERMOSTAT_TYPE):
        # Create THERMOSTAT
        CLIMATES_THERMOSTAT_LC = copy.deepcopy(CLIMATES_THERMOSTAT)
        for description in CLIMATES_THERMOSTAT_LC:
            description.mqttTopicStateTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateTemperature}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicCommandPower = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPower}"
            description.mqttTopicCurrentPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentPresetMode}"
            description.mqttTopicCommandPresetMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandPresetMode}"
            description.device_prefix_topic = device_prefix_topic
            climateList.append(
                PolarisClimate(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(climateList, update_before_add=True)
    
    
class PolarisClimate(PolarisBaseEntity, ClimateEntity):

    entity_description: PolarisClimateEntityDescription

    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisClimateEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None,
        device_class: ClimateDeviceClass | None = None,
    ) -> None:
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id,
        )
        self.entity_description = description
        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device_type)]['model'].replace('-', '_').lower()}_{description.key}"
        self.payload_on=description.payload_on
        self.payload_off=description.payload_off
        self._attr_has_entity_name = True

        self._attr_precision = 1.0
        self._attr_target_temperature_step = 1.0
        self._attr_hvac_modes = self.entity_description.hvac_modes
        if device_type in {"140","172"}:
            self.entity_description.preset_modes = {"hands": "1", "auto": "2"}
            self.entity_description.fan_modes = {"low": "1", "middle": "2", "high": "3"}
            self.entity_description.fan_mode = "low"
        if device_type == "846":
            self.entity_description.preset_modes = {"comfort": "1", "eco": "2", "away": "3", "hands": "4"}
        self._attr_preset_modes = list(self.entity_description.preset_modes.keys())
        if device_type in {"806","847","849","814"}:
            self.entity_description.fan_modes = {"auto": "0", "20_5_percent": "1", "40_5_percent": "2", "60_5_percent": "3", "80_5_percent": "4", "100_5_percent": "5"}
        if device_type in {"820","808"}:
            self.entity_description.fan_modes = {"auto": "0", "low": "1", "middle": "2", "high": "3"}
        if device_type == "857":
            self.entity_description.fan_modes = {"auto": "0", "low": "1", "middle": "2", "high": "3", "turbo": "4"}
        if device_type == "851":
            self.entity_description.fan_modes = {"auto": "0", "low": "1", "high": "2"}
        if device_type == "860":
            self.entity_description.fan_modes = {"auto": "0", "quite": "1", "min": "2", "low": "3", "middle": "4", "high": "5", "max": "6"}
            self._attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.FAN_ONLY, HVACMode.DRY]
        if device_type == "856":
            self.entity_description.fan_modes = {"auto": "0", "quite": "1", "min": "2", "low": "3", "middle": "4", "high": "5", "max": "6"}
        if self.entity_description.fan_modes is not None:
           self._attr_fan_modes = list(self.entity_description.fan_modes.keys())
           self._attr_fan_mode = self.entity_description.fan_mode
        self._attr_supported_features = self.entity_description.supported_features
        self._enable_turn_on_off_backwards_compatibility = False
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        self._attr_precision = self.entity_description.temp_step
        self._attr_target_temperature = 20
        if device_type in ("820","851","857"):
            self._attr_max_temp = 32
        else:
            self._attr_max_temp = self.entity_description.max_temp
        if device_type == "851":
            self._attr_min_temp = 18
        elif device_type == "856":
            self._attr_min_temp = 17
        else:
            self._attr_min_temp = self.entity_description.min_temp
        self._attr_preset_mode = self.entity_description.preset_mode
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_available = False
        if device_type == "851":
            self.entity_description.swing_mode = "off"
            self.entity_description.swing_modes = {"off": "0", "vertical": "2"}
        if self.entity_description.swing_mode is not None:
            self._attr_swing_mode = self.entity_description.swing_mode
            self._attr_swing_modes = list(self.entity_description.swing_modes.keys())
#        self._attr_supported_features |= ClimateEntityFeature.SWING_MODE
        self._swing_message = "00000000"
        if device_type == "826":
            self._EAP_data0 = "0000"
        if device_type in ("882","821","868"):
            self._swing_message = "000000000000"
        if device_type in ("808","851"):
            self._swing_message = "0000"

    async def async_added_to_hass(self):
        @callback
        def message_received_curr_temp(message):
            self._attr_current_temperature = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_targ_temp(message):
            if float(message.payload) < self._attr_min_temp:
                self._attr_target_temperature = self._attr_min_temp
            else:
                self._attr_target_temperature = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_mode(message):
            payload = message.payload
            if int(payload)==0:
                self._attr_hvac_mode = HVACMode.OFF
            elif (self.device_type in POLARIS_AIRCLEANER_TYPE):
                self._attr_hvac_mode = HVACMode.DRY
            elif (self.device_type in POLARIS_AIRCLEANER_EAP_TYPE):
                self._attr_hvac_mode = HVACMode.DRY
            elif (self.device_type in POLARIS_HEATER_TYPE):
                self._attr_hvac_mode = HVACMode.HEAT
            elif (self.device_type in POLARIS_THERMOSTAT_TYPE):
                self._attr_hvac_mode = HVACMode.HEAT
            elif (self.device_type in POLARIS_AIRCONDITIONER_TYPE):
                match int(payload):
                    case 1: 
                        self._attr_hvac_mode = HVACMode.AUTO
                    case 3: 
                        self._attr_hvac_mode = HVACMode.DRY
                    case 5: 
                        self._attr_hvac_mode = HVACMode.FAN_ONLY
                    case 4: 
                        self._attr_hvac_mode = HVACMode.HEAT
                    case 2: 
                        self._attr_hvac_mode = HVACMode.COOL
            else:
                self._attr_hvac_mode = HVACMode.FAN_ONLY
            self.async_write_ha_state()
        @callback
        def message_received_preset_mode(message):
            payload = message.payload
            if int(payload) > 0:
#                if (self.device_type == "846" and int(payload) > 3): 
#                    return
                self._attr_preset_mode = list(self.entity_description.preset_modes.keys())[list(self.entity_description.preset_modes.values()).index(payload)]
            if self.device_type == "826":
                self._EAP_data0 = "0" + payload + self._EAP_data0[-2:]
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode.replace("mode", "program_data/0"), self._EAP_data0)
            self.async_write_ha_state()
        @callback
        def message_received_fan_mode(message):
            self._attr_fan_mode = list(self.entity_description.fan_modes.keys())[list(self.entity_description.fan_modes.values()).index(message.payload)]
            self.async_write_ha_state()
        @callback
        def message_received_swing_mode(message):
#            _LOGGER.debug("swing message %s", message.payload)
            self._swing_message = message.payload    # 00112233  00-качание верх/низ 11-качание влево/вправо 22-эко режим охлаждения 33-автообогрев
            if self.device_type == "851":
                if self._swing_message[:2] == "01":
                    swmode = "vertical"
                else:
                    swmode = "off"
            else:
                match self._swing_message[:4]:
                    case "0000": 
                        swmode = "off"
                    case "0001": 
                        swmode = "horizontal"
                    case "0100" | "0200" | "0300" | "0400" | "0500" | "0600": 
                        swmode = "vertical"
                    case "0101" | "0201" | "0301" | "0401" | "0501" | "0601": 
                        swmode = "both"
#            _LOGGER.debug("swing mode %s", swmode)
            self._attr_swing_mode = swmode
            self.async_write_ha_state()
            
        @callback
        def EAP_data_message_received(message):
            self._EAP_data0 = message.payload
#            _LOGGER.debug("EAP mode data0 message %s", self._EAP_data0)


        if self.device_type == "826":
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentPresetMode.replace("mode", "program_data/0"),
                EAP_data_message_received,
                1,
            )
            
            
        if self.entity_description.mqttTopicCurrentTemperature is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentTemperature,
                message_received_curr_temp,
                1,
            )
        if self.entity_description.mqttTopicStateTemperature is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicStateTemperature,
                message_received_targ_temp,
                1,
            )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentPresetMode,
            message_received_mode,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentPresetMode,
            message_received_preset_mode,
            1,
        )
        if self.entity_description.mqttTopicStateFanMode is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicStateFanMode,
                message_received_fan_mode,
                1,
            )
        if self.entity_description.mqttTopicStateSwingMode is not None:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicStateSwingMode,
                message_received_swing_mode,
                1,
            )
        
        @callback
        async def entity_availability(message):
            if self.entity_description.name != "available":
                if str(message.payload).lower() in ("1", "true"):
                    self._attr_available = False
                else:
                    self._attr_available = True
                self.async_write_ha_state()
            
        await mqtt.async_subscribe(self.hass, f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/error/connection", entity_availability, 1)


    async def async_turn_on(self) -> None:
        if (self.device_type in POLARIS_AIRCLEANER_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 1)
            await self.async_set_hvac_mode(HVACMode.DRY)
        elif (self.device_type in POLARIS_AIRCLEANER_EAP_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 1)
            await self.async_set_hvac_mode(HVACMode.DRY)
        elif (self.device_type in POLARIS_HEATER_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 1)
            await self.async_set_hvac_mode(HVACMode.HEAT)
        elif (self.device_type in POLARIS_THERMOSTAT_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 1)
            await self.async_set_hvac_mode(HVACMode.HEAT)
        else:
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 5)
            await self.async_set_hvac_mode(HVACMode.FAN_ONLY)

    async def async_turn_off(self) -> None:
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 0)
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._attr_target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if (kwargs.get(ATTR_TARGET_TEMP_HIGH) is not None and kwargs.get(ATTR_TARGET_TEMP_LOW) is not None):
            self._attr_target_temperature_high = kwargs.get(ATTR_TARGET_TEMP_HIGH)
            self._attr_target_temperature_low = kwargs.get(ATTR_TARGET_TEMP_LOW)
        if (hvac_mode := kwargs.get(ATTR_HVAC_MODE)) is not None:
            self._attr_hvac_mode = hvac_mode
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTemperature, int(self._attr_target_temperature))
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        if (fan_mode == "9_speed"):
            fan_mode = "8_speed"
        if self.device_type == "857" and self._attr_hvac_mode not in ("heat", "cool") and fan_mode == "turbo":
            fan_mode = "high"
        if (self.device_type == "826" and fan_mode == "off"):
            fan_mode = "low"
        self._attr_fan_mode = fan_mode
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFanMode, self.entity_description.fan_modes[fan_mode])
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        self._attr_hvac_mode = hvac_mode
        if hvac_mode == "off":
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, 0)
        elif ((self.device_type in POLARIS_AIRCLEANER_TYPE) or (self.device_type in POLARIS_HEATER_TYPE) or (self.device_type in POLARIS_AIRCLEANER_EAP_TYPE)):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 1)
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFanMode, self.entity_description.fan_modes[self._attr_fan_mode])                   # add for on fan after off heater
        elif (self.device_type in POLARIS_AIRCONDITIONER_TYPE):
            match hvac_mode:
                case "auto": 
                    command = 1
                case "dry": 
                    command = 3
                case "fan_only": 
                    command = 5
                case "heat": 
                    command = 4
                case "cool": 
                    command = 2
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, command)
            if self.device_type == "868" and hvac_mode in ("heat", "cool"):
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTemperature, int(self._attr_target_temperature))
        else:
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, 5)  # 5 = FAN_ONLY for AIRCLEANER and HEATER_TYPE
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Update preset_mode on."""
        self._attr_preset_mode = preset_mode
        if (self.device_type == "846" and preset_mode == "hands"):
            self._attr_fan_mode = "10_percent"
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFanMode, self.entity_description.fan_modes[self._attr_fan_mode])
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, self.entity_description.preset_modes[preset_mode])
        if self.device_type == "826":
            if (preset_mode != "night" and int(self._EAP_data0[-2:]) > 1): 
                self._EAP_data0 = "0" + self.entity_description.preset_modes[preset_mode] + "01"
            else:
                self._EAP_data0 = "0" + self.entity_description.preset_modes[preset_mode] + self._EAP_data0[-2:]
#                _LOGGER.debug("EAP data0 mode select %s", self._EAP_data0)  # отправить в prog_data
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode.replace("mode", "program_data/0"), self._EAP_data0)
        self.async_write_ha_state()
        
    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new swing mode."""
        self._attr_swing_mode = swing_mode
#        _LOGGER.debug("set swing mode %s", swing_mode)
        match swing_mode:
            case "off": 
                swmessage = "0000"
            case "horizontal": 
                swmessage = "0001"
            case "vertical": 
                swmessage = "0100"
            case "both": 
                swmessage = "0101"
        if self.device_type == "808":
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandSwingMode, swmessage)
        elif self.device_type == "851":
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandSwingMode, swmessage[:2] + self._swing_message[-2:])
        else:
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandSwingMode, swmessage + self._swing_message[4:])
        self.async_write_ha_state()
        
    @property
    def fan_modes(self) -> list[str] | None:
        return self._attr_fan_modes
        
    @property
    def fan_mode(self) -> list[str] | None:
        return self._attr_fan_mode