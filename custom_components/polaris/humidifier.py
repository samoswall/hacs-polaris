"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature   #    ?????
from homeassistant.components.humidifier import (
    DOMAIN,
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
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
    HUMIDIFIERS,
    PolarisHumidifierEntityDescription,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_HUMIDDIFIER_7_MODE_TYPE,
    POLARIS_HUMIDDIFIER_5A_MODE_TYPE,
    POLARIS_HUMIDDIFIER_5B_MODE_TYPE,
    POLARIS_HUMIDDIFIER_4_MODE_TYPE,
    POLARIS_HUMIDDIFIER_3A_MODE_TYPE,
    POLARIS_HUMIDDIFIER_3B_MODE_TYPE,
    POLARIS_HUMIDDIFIER_1_MODE_TYPE,
    HUMIDDIFIER_5A_AVAILABLE_MODES,
    HUMIDDIFIER_5B_AVAILABLE_MODES,
    HUMIDDIFIER_4_AVAILABLE_MODES,
    HUMIDDIFIER_3A_AVAILABLE_MODES,
    HUMIDDIFIER_3B_AVAILABLE_MODES,
    HUMIDDIFIER_1_AVAILABLE_MODES,
)

SUPPORT_FLAGS = HumidifierEntityFeature(1)

#_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:

    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    humidifierList = []
    
    if (device_type in POLARIS_HUMIDDIFIER_TYPE):
        # Create humidifier  
            HUMIDIFIERS_LC = copy.deepcopy(HUMIDIFIERS)
            for description in HUMIDIFIERS_LC:
                description.mqttTopicCurrentState = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentState}"
                description.mqttTopicCommandState = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandState}"
                description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
                description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
                description.mqttTopicCurrentHumidity = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentHumidity}"
                description.mqttTopicCurrentTargetHumidity = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTargetHumidity}"
                description.mqttTopicCommandTargetHumidity = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTargetHumidity}"
                description.device_prefix_topic = device_prefix_topic
                humidifierList.append(
                    PolarisHumidifier(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    async_add_entities(humidifierList, update_before_add=True)

    
class PolarisHumidifier(PolarisBaseEntity, HumidifierEntity):

    entity_description: PolarisHumidifierEntityDescription
    _attr_supported_features = HumidifierEntityFeature.MODES

    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisHumidifierEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None,
        device_class: HumidifierDeviceClass | None = None,
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
        self._attr_is_on = True
        self._attr_max_humidity = description.max_humidity
        self._attr_min_humidity = description.min_humidity
        if device_type in POLARIS_HUMIDDIFIER_7_MODE_TYPE:
            self.my_operation_list = description.available_modes
        elif device_type in POLARIS_HUMIDDIFIER_5A_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_5A_AVAILABLE_MODES
        elif device_type in POLARIS_HUMIDDIFIER_5B_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_5B_AVAILABLE_MODES
        elif device_type in POLARIS_HUMIDDIFIER_4_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_4_AVAILABLE_MODES
        elif device_type in POLARIS_HUMIDDIFIER_3A_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_3A_AVAILABLE_MODES
        elif device_type in POLARIS_HUMIDDIFIER_3B_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_3B_AVAILABLE_MODES
        elif device_type in POLARIS_HUMIDDIFIER_1_MODE_TYPE:
            self.my_operation_list = HUMIDDIFIER_1_AVAILABLE_MODES
        self._attr_mode = description.mode
        self._attr_available_modes = list(self.my_operation_list.keys())
        self.payload_on=description.payload_on
        self.payload_off=description.payload_off
        self._attr_has_entity_name = True
        self._attr_available = False
        self._attr_current_humidity = self._attr_min_humidity
        self._attr_target_humidity = self._attr_min_humidity


    async def async_added_to_hass(self):
        @callback
        def message_received_curr_humid(message):
            self._attr_current_humidity = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_targ_humid(message):
            if float(message.payload) < self._attr_min_humidity:
                self._attr_target_humidity = self._attr_min_humidity
            else:
                self._attr_target_humidity = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_mode(message):
            payload = message.payload
            if int(payload)==0:
                self._attr_is_on = 0
            else:
                self._attr_is_on = 1
                self._attr_mode = list(self.my_operation_list.keys())[list(self.my_operation_list.values()).index(message.payload)]
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentHumidity,
            message_received_curr_humid,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentTargetHumidity,
            message_received_targ_humid,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentState,
            message_received_mode,
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


    def turn_on(self, **kwargs):
        self._attr_is_on = self.payload_on
        topic = f"{self.entity_description.mqttTopicCommandState}"
        self.publishToMQTT(topic)

    def turn_off(self, **kwargs):
        self._attr_is_on = self.payload_off
        topic = f"{self.entity_description.mqttTopicCommandState}"
        self.publishToMQTT(topic)

    def publishToMQTT(self, topic: str):
        mqtt.publish(self.hass, topic, str(self._attr_is_on))

    def set_humidity(self, humidity: int):
        self._attr_target_humidity = humidity
        topic = f"{self.entity_description.mqttTopicCommandTargetHumidity}"
        mqtt.publish(self.hass, topic, str(humidity))


    def set_mode(self, mode: str):
        self._attr_mode = mode
        topic = f"{self.entity_description.mqttTopicCommandMode}"
        mqtt.publish(self.hass, topic, self.my_operation_list[mode])

