"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.button import (
    DOMAIN,
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
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
    BUTTON_COOKER,
    PolarisButtonEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
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
    buttonList = []

    if (device_type in POLARIS_COOKER_TYPE):
        BUTTON_COOKER_LC = copy.deepcopy(BUTTON_COOKER)
        for description in BUTTON_COOKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(buttonList, update_before_add=True)


class PolarisButton(PolarisBaseEntity, ButtonEntity):

    entity_description: PolarisButtonDescription

    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisButtonEntityDescription,
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

    async def async_press(self) -> None:
        """Trigger the button action."""
        _LOGGER.debug("Button press: %s", self.entity_description.payloads)
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, self.entity_description.payloads)
