"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.switch import DOMAIN, SwitchEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg

from .common import PolarisBaseEntity
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    SWITCHES_ALL_DEVICES,
    SWITCH_KETTLE_BACKLIGHT,
    SWITCH_HUMIDIFIER_BACKLIGHT,
    SWITCH_HUMIDIFIER_IONISER,
    SWITCH_HUMIDIFIER_WARM_STREAM,
    SWITCHES_COOKER,
    SWITCHES_COFFEEMAKER,
    SWITCHES_COFFEEMAKER_ROG,
    SWITCHES_CLIMATE,
    PolarisSwitchEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_KETTLE_WITH_BACKLIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE,
    POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
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
    switchList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create sensors for all devices
        SWITCHES_ALL_DEVICES_LC = copy.deepcopy(SWITCHES_ALL_DEVICES)
        for description in SWITCHES_ALL_DEVICES_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if device_type in POLARIS_KETTLE_WITH_BACKLIGHT_TYPE:
        # Create sensors for backlight devices
        SWITCH_KETTLE_BACKLIGHT_LC = copy.deepcopy(SWITCH_KETTLE_BACKLIGHT)
        for description in SWITCH_KETTLE_BACKLIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HUMIDDIFIER_TYPE):
        # Create switches for all devices
        SWITCHES_ALL_DEVICES_LC = copy.deepcopy(SWITCHES_ALL_DEVICES)
        for description in SWITCHES_ALL_DEVICES_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
        SWITCH_HUMIDIFIER_BACKLIGHT_LC = copy.deepcopy(SWITCH_HUMIDIFIER_BACKLIGHT)
        for description in SWITCH_HUMIDIFIER_BACKLIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE):
        # Create switch ioniser for humidifiers
        SWITCH_HUMIDIFIER_IONISER_LC = copy.deepcopy(SWITCH_HUMIDIFIER_IONISER)
        for description in SWITCH_HUMIDIFIER_IONISER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE):
        # Create switch stream warm for humidifiers
        SWITCH_HUMIDIFIER_WARM_STREAM_LC = copy.deepcopy(SWITCH_HUMIDIFIER_WARM_STREAM)
        for description in SWITCH_HUMIDIFIER_WARM_STREAM_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COOKER_TYPE):
        # Create switches for cooker
        SWITCHES_COOKER_LC = copy.deepcopy(SWITCHES_COOKER)
        for description in SWITCHES_COOKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_TYPE):
        # Create switches for coffeemaker
        SWITCHES_COFFEEMAKER_LC = copy.deepcopy(SWITCHES_COFFEEMAKER)
        for description in SWITCHES_COFFEEMAKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
        # Create switches for coffeemaker
        SWITCHES_COFFEEMAKER_ROG_LC = copy.deepcopy(SWITCHES_COFFEEMAKER_ROG)
        for description in SWITCHES_COFFEEMAKER_ROG_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_CLIMATE_TYPE):
        # Create switches for climate
        SWITCHES_CLIMATE_LC = copy.deepcopy(SWITCHES_CLIMATE)
        for description in SWITCHES_CLIMATE_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(switchList, update_before_add=True)

class PolarisSwitch(PolarisBaseEntity, SwitchEntity):
    entity_description: PolarisSwitchEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisSwitchEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None
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
#        self._old_mode = "0"
        if self.entity_description.translation_key == "keepwarm_switch":
            self._attr_available = False

    async def async_added_to_hass(self):
        @callback
        def message_received(message):
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                if int(self.device_type) == 45:
                    if str(message.payload) in ("1", "2", "3", "4", "5", "6"):
                        self._attr_is_on = True
                    else:
                        self._attr_is_on = False
                elif str(message.payload) in ("01", "1", "03", "3"):
                    self._attr_is_on = True
                else:
                    self._attr_is_on = False
            else:
                if str(message.payload).lower() in ("1", "2", "3", "4", "5", "true"):
                    self._attr_is_on = True
                elif str(message.payload).lower() in ("0", "false"):
                   self._attr_is_on = False
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
        
        @callback
        def mode_message_received(message):
            if self.entity_description.translation_key == "keepwarm_switch":
                if str(message.payload) in ("[]", '[{"mode":1,"time":0,"temperature":0}]'):
                    self._attr_available = False
                else:
                    self._attr_available = True
                    self._attr_is_on = True
                self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue.replace("keepwarm", "steps"),
            mode_message_received,
            1,
        )

    def turn_on(self, **kwargs):
        self._attr_is_on = True
        self.publishToMQTT(self.payload_on)

    def turn_off(self, **kwargs):
        self._attr_is_on = False
        self.publishToMQTT(self.payload_off)

    def publishToMQTT(self, send_message: str):
        topic = f"{self.entity_description.mqttTopicCommand}"
        self.hass.components.mqtt.publish(self.hass, topic, send_message)

