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
from homeassistant.components.water_heater import DOMAIN, WaterHeaterEntity, WaterHeaterEntityFeature
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
    WATER_HEATERS,
    PolarisWaterHeaterEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
)

#_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    waterheaterList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create water heater for kettle devices
        WATER_HEATERS_LC = copy.deepcopy(WATER_HEATERS)
        for description in WATER_HEATERS_LC:
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_id}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_id}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicTargetTemperature = f"{mqtt_root}/{device_id}/{description.mqttTopicTargetTemperature}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_id}/{description.mqttTopicCommandMode}"
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_id}/{description.mqttTopicCurrentMode}"
            waterheaterList.append(
                PolarisWaterHeater(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(waterheaterList, update_before_add=True)

class PolarisWaterHeater(PolarisBaseEntity, WaterHeaterEntity):
    entity_description: PolarisWaterHeaterEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisWaterHeaterEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None,
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
        self.temperature_unit=UnitOfTemperature.CELSIUS
        self._attr_min_temp=description.min_temp
        self._attr_max_temp=description.max_temp
        self.target_temperature = 100
        self._unit_of_measurement = UnitOfTemperature.CELSIUS
        self._away = None
        self._attr_is_on = True
        self.operation = description.mode
        self._attr_mode = description.mode
        self._min_temp = description.min_temp
        self._max_temp = description.max_temp
    #    self.optimistic = True
        self._support_flags = WaterHeaterEntityFeature.OPERATION_MODE | WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF
        self.my_operation_list = description.operation_list
        self._attr_operation_list = list(description.operation_list.keys())   # ???
        self._operation_list = list(description.operation_list.keys())
        #self.entity_picture = "https://images.cdn.polaris-iot.com/a/8c/aad08-4d13-489c-9b0f-028486297ac1/60.webp"
        self._attr_has_entity_name = True

    async def async_added_to_hass(self):
        @callback
        def message_received_temp(message):
            self.current_temperature = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_mode(message):
            self.current_operation = list(self.my_operation_list.keys())[list(self.my_operation_list.values()).index(message.payload)]
            self.async_write_ha_state()
        @callback
        def message_received_targtemp(message):
            self.target_temperature = float(message.payload)
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentTemperature,
            message_received_temp,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentMode,
            message_received_mode,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicTargetTemperature,
            message_received_targtemp,
            1,
        )

    def async_turn_on(self, **kwargs):
        self._attr_is_on = self.payload_on
        self.publishToMQTT()

    def async_turn_off(self, **kwargs):
        self._attr_is_on = self.payload_off
        self.publishToMQTT()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommandMode}"
        self.hass.components.mqtt.publish(self.hass, topic, str(self._attr_is_on))

    def set_operation_mode(self, operation_mode):
        topic = f"{self.entity_description.mqttTopicCommandTemperature}"
        self.hass.components.mqtt.publish(self.hass, topic, int(self.target_temperature))
        topic = f"{self.entity_description.mqttTopicCommandMode}"
        self.current_operation = operation_mode
        self.hass.components.mqtt.publish(self.hass, topic, int(self.my_operation_list[operation_mode]))
        self.schedule_update_ha_state()

    def set_temperature(self, **kwargs):
        self.target_temperature = kwargs.get(ATTR_TEMPERATURE)
        self.schedule_update_ha_state()

    @property
    def operation_list(self):
        return self._operation_list

    @property
    def supported_features(self):
        return self._support_flags

    @property
    def min_temp(self):
        return self._min_temp

    @property
    def max_temp(self):
        return self._max_temp
