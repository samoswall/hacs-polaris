"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .common import PolarisBaseEntity
from homeassistant.util import color as color_util
from homeassistant.components.light import (
    DOMAIN,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    LIGHTS,
    PolarisLightEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
)

#_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    lightList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create water heater for kettle devices
        LIGHTS_LC = copy.deepcopy(LIGHTS)
        for description in LIGHTS_LC:
            description.mqttTopicCurrentColor = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentColor}"
            description.mqttTopicCommandColor = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandColor}"
            description.mqttTopicCurrentState = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentState}"
            description.mqttTopicCommandState = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandState}"
            lightList.append(
                PolarisLight(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(lightList, update_before_add=True)


class PolarisLight(PolarisBaseEntity, LightEntity):

    entity_description: PolarisLightEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisLightEntityDescription,
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
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_has_entity_name = True
        self._attr_rgb_color = [255, 255, 255]
        self._attr_brightness = 100
        self._attr_is_on = False

    async def async_added_to_hass(self):
        @callback
        def message_received_rgb(message):
            rgb = color_util.rgb_hex_to_rgb_list(message.payload)
            self._attr_rgb_color = rgb
            bright = int(max(rgb)/255*100)
            self._attr_brightness = bright
            self.async_write_ha_state()
        @callback
        def message_received_state(message):
            if str(message.payload).lower() in ("1", "true"):
                self._attr_is_on = True
            elif str(message.payload).lower() in ("0", "false"):
                self._attr_is_on = False
            else:
                self._attr_is_on = None
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentColor,
            message_received_rgb,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentState,
            message_received_state,
            1,
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        if ATTR_RGB_COLOR in kwargs:
            color = color_util.color_rgb_to_hex(*kwargs[ATTR_RGB_COLOR])
            self._attr_rgb_color = color_util.rgb_hex_to_rgb_list(color)
        if ATTR_BRIGHTNESS in kwargs:
            level = int((kwargs.get(ATTR_BRIGHTNESS, 0) * 100) / 255)
            self._attr_brightness = level
            bright_factor_old = max(self._attr_rgb_color)/255
            bright_factor_new = level/ 100 / bright_factor_old
            self._attr_rgb_color = [int(value * bright_factor_new) for value in self._attr_rgb_color]
        topic = self.entity_description.mqttTopicCommandColor
        self.hass.components.mqtt.publish(self.hass, topic,  color_util.color_rgb_to_hex(self._attr_rgb_color[0], self._attr_rgb_color[1],self._attr_rgb_color[2]))
        topic = self.entity_description.mqttTopicCommandState
        self.hass.components.mqtt.publish(self.hass, topic, "true")
        self._attr_is_on = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        topic = self.entity_description.mqttTopicCommandState
        self.hass.components.mqtt.publish(self.hass, topic, "false")
        self._attr_is_on = False

    @property
    def is_on(self) -> bool:
        return self._attr_is_on

    @property
    def brightness(self) -> int:
        return int((self._attr_brightness * 255) / 100)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._attr_rgb_color
