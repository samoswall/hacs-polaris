"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage

from homeassistant.components.select import DOMAIN, SelectEntity
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
    SELECTS,
    PolarisSelectEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
)

#_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    selectList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        SELECTS_LC = copy.deepcopy(SELECTS)
        for description in SELECTS_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_id}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_id}/{description.mqttTopicCommandMode}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_id}/{description.mqttTopicCommandTemperature}"
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(selectList, update_before_add=True)


class PolarisSelect(PolarisBaseEntity, SelectEntity):

    entity_description: PolarisSelectEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisSelectEntityDescription,
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
        self._attr_options = list(description.options.keys())
        self._attr_current_option = "not_selected"
        self._attr_has_entity_name = True

    @property
    def available(self):
        return self._attr_current_option is not None

    def key_from_option(self, option: str):
        try:
            return next(
                key
                for key, value in self.entity_description.options.items()
                if value == option
            )
        except StopIteration:
            return None

    def select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTemperature, self.entity_description.options[option])
        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, 3)
        self.async_write_ha_state()
        
    async def async_added_to_hass(self):
        @callback
        def message_received_sel(message):
            payload = message.payload
            if payload=="0":
                self._attr_current_option = "not_selected"

        await mqtt.async_subscribe(self.hass, self.entity_description.mqttTopicCurrentMode, message_received_sel, 1)
