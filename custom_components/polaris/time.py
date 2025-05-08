"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from datetime import time
from homeassistant.components.time import DOMAIN, TimeEntity, TimeEntityDescription
#from homeassistant.components.datetime import DOMAIN, DateTimeEntity, DateTimeEntityDescription
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
    TIME_COOKER,
    PolarisTimeEntityDescription,
    POLARIS_COOKER_TYPE,
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
    timeList = []
    
    if (device_type in POLARIS_COOKER_TYPE):
        TIME_COOKER_LC = copy.deepcopy(TIME_COOKER)
        for description in TIME_COOKER_LC:
            description.mqttTopicCurrentTime = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTime}"
            description.mqttTopicCommandTime = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTime}"
            description.device_prefix_topic = device_prefix_topic
            timeList.append(
                PolarisTime(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(timeList, update_before_add=True)


class PolarisTime(PolarisBaseEntity, TimeEntity):

    entity_description: PolarisTimeDescription

    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisTimeEntityDescription,
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
        self._attr_available = False
        self._attr_has_entity_name = True
        self._attr_native_value = time(0, self.entity_description.default_time, 0)

    async def async_added_to_hass(self):
        @callback
        async def entity_availability(message):
            if self.entity_description.name != "available":
                if str(message.payload).lower() in ("1", "true"):
                    self._attr_available = False
                else:
                    self._attr_available = True
                self.async_write_ha_state()
            
        await mqtt.async_subscribe(self.hass, f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/error/connection", entity_availability, 1)



    async def async_set_value(self, value: time) -> None:
        """Update the time."""
        value_hour=value.hour
        value_minute=value.minute
        value_second=0
        value_in_seconds = value.hour * 3600 + value.minute * 60
        if (value_in_seconds > (self.entity_description.max_time * 60)):
            value_hour = int(self.entity_description.max_time / 60) - 1
        self._attr_native_value = time(value_hour,value_minute,value_second)
        value_in_seconds = value_hour * 3600 + value_minute * 60
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTime, str(value_in_seconds))

