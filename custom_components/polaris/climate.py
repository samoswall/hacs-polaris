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
    PolarisClimateEntityDescription,
    POLARIS_CLIMATE_TYPE,
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
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class']}_{POLARIS_DEVICE[int(device_type)]['model']}_{description.name}"
        self.payload_on=description.payload_on
        self.payload_off=description.payload_off
        self._attr_has_entity_name = True

        
        self._attr_hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY]
        self._attr_preset_modes = list(self.entity_description.preset_modes.keys())
        self._attr_fan_modes = list(self.entity_description.fan_modes.keys())
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self._enable_turn_on_off_backwards_compatibility = False
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        
        self._attr_precision = self.entity_description.temp_step
        self._attr_target_temperature = 20
        self._attr_max_temp = self.entity_description.max_temp
        self._attr_min_temp = self.entity_description.min_temp
        
        self._attr_fan_mode = "off"
        self._attr_preset_mode = "off"
        self._attr_hvac_mode = HVACMode.OFF
        

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
            else:
                self._attr_hvac_mode = HVACMode.FAN_ONLY
            self.async_write_ha_state()
        @callback
        def message_received_preset_mode(message):
            payload = message.payload
            if int(payload) > 0:
                self._attr_preset_mode = list(self.entity_description.preset_modes.keys())[list(self.entity_description.preset_modes.values()).index(payload)]
            self.async_write_ha_state()
        @callback
        def message_received_fan_mode(message):
            self._attr_fan_mode = list(self.entity_description.fan_modes.keys())[list(self.entity_description.fan_modes.values()).index(message.payload)]
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentTemperature,
            message_received_curr_temp,
            1,
        )
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
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicStateFanMode,
            message_received_fan_mode,
            1,
        )

    async def async_turn_on(self) -> None:
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 5)
        await self.async_set_hvac_mode(HVACMode.FAN_ONLY)

    async def async_turn_off(self) -> None:
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPower, 0)
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
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTemperature, self._attr_target_temperature)
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        self._attr_fan_mode = fan_mode
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFanMode, self.entity_description.fan_modes[fan_mode])
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new operation mode."""
        self._attr_hvac_mode = hvac_mode
        if hvac_mode == "off":
            self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, 0)
        else:
            self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, 5)
        self.async_write_ha_state()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Update preset_mode on."""
        self._attr_preset_mode = preset_mode
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandPresetMode, self.entity_description.preset_modes[preset_mode])
        self.async_write_ha_state()