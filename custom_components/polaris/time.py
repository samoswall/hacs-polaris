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
    TIME_INPUT,
    PolarisTimeEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
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
    timeList = []
"""    
    if (device_type in POLARIS_KETTLE_TYPE):
        TIME_INPUT_LC = copy.deepcopy(TIME_INPUT)
        for description in TIME_INPUT_LC:
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
"""

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
        self._attr_available = True
        self._attr_has_entity_name = True
        self._attr_native_value = time(12, 10, 0)

    async def async_set_value(self, value: time) -> None:
        """Update the date/time."""
        self._attr_native_value = value
        _LOGGER.debug("Input Time: %s", value)

