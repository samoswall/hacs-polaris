"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy
from datetime import datetime

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
    BUTTON_HUMIDIFIER,
    BUTTON_COOKER,
    SELECT_COOKER,
    BUTTON_COFFEEMAKER,
    SELECT_COFFEEMAKER,
    PolarisButtonEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
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

    if (device_type in POLARIS_HUMIDDIFIER_TYPE):
        BUTTON_HUMIDIFIER_LC = copy.deepcopy(BUTTON_HUMIDIFIER)
        for description in BUTTON_HUMIDIFIER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                )
            )
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
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_TYPE):
        BUTTON_COFFEEMAKER_LC = copy.deepcopy(BUTTON_COFFEEMAKER)
        for description in BUTTON_COFFEEMAKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
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
        device_prefix_topic: str | None = None,
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
        self.device_prefix_topic = device_prefix_topic

    async def async_press(self) -> None:
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
            if self.entity_description.key == "button_stop":
                self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", "0")
            else:
                state_amount = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_amount").state
                state_weight = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_weight").state
                state_tank = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_tank").state
                state_pressure = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_pressure").state
                state_speed = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_speed").state
                state_temp = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_temperature").state
                state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_select_mode_cofeemaker").state
                state_coffee_maker = self.hass.states.get(f"switch.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_power").state
                if state_coffee_maker != "off":
                    if state_amount != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"amount", state_amount)
                    if state_weight != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"weight", state_weight)
                    if state_tank != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"tank", state_tank)
                    if state_pressure != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"pressure", state_pressure)
                    if state_speed != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"speed", state_speed)
                    if state_temp != "unavailable":
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"temperature", state_temp)
                    if state_mode != "not_selected":
                        command_mode = SELECT_COFFEEMAKER[0].options[state_mode]
                        coffee_mode = json.loads(command_mode)
                        self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", coffee_mode[0]["mode"])

        if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker":
            if self.entity_description.key == "button_stop":
                self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, "[]")
            else:
                state_temp = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_set_temperature").state
                state_time = self.hass.states.get(f"time.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_cooking_time").state
                state_time_obj = datetime.strptime(state_time, "%H:%M:%S")
                state_time_seconds = state_time_obj.hour * 3600 + state_time_obj.minute * 60 + state_time_obj.second
                state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_select_mode_cooker").state
                command_mode = SELECT_COOKER[0].options[state_mode]
                cook_mode = json.loads(command_mode)
                payload = "[{" + f'"mode":{cook_mode[0]["mode"]}, "time":{state_time_seconds}, "temperature":{state_temp}' + "}]"
                state_time_delay = self.hass.states.get(f"time.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_delay_start").state
                state_time_delay_obj = datetime.strptime(state_time_delay, "%H:%M:%S")
                state_time_delay_seconds = state_time_delay_obj.hour * 3600 + state_time_delay_obj.minute * 60 + state_time_delay_obj.second
                if state_time_delay_seconds > 59:
                    self.hass.components.mqtt.publish(self.hass, f"{self.mqtt_root}/{self.device_prefix_topic}/control/delay_start", state_time_delay_seconds)
                self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, payload)
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "humidifier":
            self.hass.components.mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, self.entity_description.payloads)
