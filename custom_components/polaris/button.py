"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy
from datetime import datetime
import os
from pathlib import Path
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
from homeassistant.helpers import entity_registry as er
from .common import PolarisBaseEntity
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    CUSTOM_SELECT_FILE_PATH,
    BUTTON_HUMIDIFIER,
    BUTTON_COOKER,
    SELECT_COOKER,
    BUTTON_COFFEEMAKER,
    SELECT_COFFEEMAKER,
    SELECT_COFFEEMAKER_ROG,
    BUTTON_CLIMATES,
    BUTTON_CLIMATES_200,
    BUTTON_AIRCLEANER,
    PolarisButtonEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
    AIRFRYER_1_MODES,
    AIRFRYER_2_MODES
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def _async_read_file(hass):
    path = Path(CUSTOM_SELECT_FILE_PATH)
    if not path.exists():
        return None
    text = await hass.async_add_executor_job(path.read_text, "utf-8")
    return json.loads(text)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    buttonList = []
    
    custom_data_select = await _async_read_file(hass)

    if (device_type in POLARIS_HUMIDDIFIER_TYPE and device_type not in {"835","881"}):
        BUTTON_HUMIDIFIER_LC = copy.deepcopy(BUTTON_HUMIDIFIER)
        for description in BUTTON_HUMIDIFIER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.device_prefix_topic = device_prefix_topic
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                    custom_data_select=custom_data_select
                )
            )
    if (device_type in POLARIS_COOKER_TYPE):
        BUTTON_COOKER_LC = copy.deepcopy(BUTTON_COOKER)
        for description in BUTTON_COOKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.device_prefix_topic = device_prefix_topic
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                    custom_data_select=custom_data_select
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_TYPE):
        BUTTON_COFFEEMAKER_LC = copy.deepcopy(BUTTON_COFFEEMAKER)
        for description in BUTTON_COFFEEMAKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.device_prefix_topic = device_prefix_topic
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                    custom_data_select=custom_data_select
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
        BUTTON_COFFEEMAKER_LC = copy.deepcopy(BUTTON_COFFEEMAKER)
        for description in BUTTON_COFFEEMAKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.device_prefix_topic = device_prefix_topic
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                    custom_data_select=custom_data_select
                )
            )
    if (device_type in POLARIS_CLIMATE_TYPE):
        if (device_type == "859"):
            BUTTON_CLIMATES_200_LC = copy.deepcopy(BUTTON_CLIMATES_200)
            for description in BUTTON_CLIMATES_200_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.device_prefix_topic = device_prefix_topic
                buttonList.append(
                    PolarisButton(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id,
                        device_prefix_topic=device_prefix_topic,
                        custom_data_select=custom_data_select
                    )
                )
        else:
            BUTTON_CLIMATES_LC = copy.deepcopy(BUTTON_CLIMATES)
            for description in BUTTON_CLIMATES_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.device_prefix_topic = device_prefix_topic
                buttonList.append(
                    PolarisButton(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id,
                        device_prefix_topic=device_prefix_topic,
                        custom_data_select=custom_data_select
                    )
                )
    if (device_type in POLARIS_AIRCLEANER_TYPE):
      if (device_type not in ("140","172")):
        BUTTON_AIRCLEANER_LC = copy.deepcopy(BUTTON_AIRCLEANER)
        for description in BUTTON_AIRCLEANER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.device_prefix_topic = device_prefix_topic
            buttonList.append(
                PolarisButton(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    device_prefix_topic=device_prefix_topic,
                    custom_data_select=custom_data_select
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
        custom_data_select: str | None=None
    ) -> None:
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id,
        )
        self._custom_data_select = custom_data_select
        self.entity_description = description
        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device_type)]['model'].replace('-', '_').lower()}_{description.key}"
        self._attr_available = False
        self._attr_has_entity_name = True
        self.device_prefix_topic = device_prefix_topic
        
        
        
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker":
            self._select_options = json.loads(json.dumps(SELECT_COOKER[0].options))
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "air_fryer":
            if self.device_type == "292":
                self._select_options = json.loads(json.dumps(AIRFRYER_2_MODES))
            else:
                self._select_options = json.loads(json.dumps(AIRFRYER_1_MODES))
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
            if self.device_type in POLARIS_COFFEEMAKER_ROG_TYPE:
                if self.device_type in ("222","274","279"): #ROG_TYPE_3
                    self._select_options = {
                        'not_selected': '[{"mode": 0, "amount": 30, "tank": 0, "temperature": 95}]',
                        'espresso': '[{"mode": 1, "amount": 65, "tank": 0, "temperature": 95}]',
                        'doppio': '[{"mode": 7, "amount": 115, "tank": 0, "temperature": 95}]',
                        'cappuccino': '[{"mode": 2, "amount": 50, "tank": 15, "temperature": 95}]',
                        'double_cappuccino': '[{"mode": 8, "amount": 100, "tank": 25, "temperature": 95}]',
                        'latte': '[{"mode": 3, "amount": 65, "tank": 32, "temperature": 95}]',
                        'double_latte': '[{"mode": 9, "amount": 115, "tank": 40, "temperature": 95}]',
                        'lungo': '[{"mode": 1, "amount": 120, "tank": 0, "temperature": 95}]',
                        'flat_white': '[{"mode": 2, "amount": 70, "tank": 20, "temperature": 95}]',
                        'clearing': '[{"mode": 4, "amount": 0, "tank": 0, "temperature": 95}]',
                        'heating': '[{"mode": 5, "amount": 0, "tank": 0, "temperature": 95}]',
                        'hot_milk': '[{"mode": 6, "amount": 0, "tank": 15, "temperature": 95}]'
                    }
                elif device_type in ("190","207","235"): #ROG_TYPE_2
                     self._select_options = {
                         'not_selected': '[{"mode": 0, "amount": 30, "tank": 0, "temperature": 95}]',
                         'espresso': '[{"mode": 1, "amount": 65, "tank": 0, "temperature": 95}]',
                         'doppio': '[{"mode": 2, "amount": 115, "tank": 0, "temperature": 95}]',
                         'cappuccino': '[{"mode": 2, "amount": 50, "tank": 15, "temperature": 95}]',
                         'double_cappuccino': '[{"mode": 2, "amount": 100, "tank": 25, "temperature": 95}]',
                         'latte': '[{"mode": 3, "amount": 65, "tank": 32, "temperature": 95}]',
                         'double_latte': '[{"mode": 2, "amount": 115, "tank": 40, "temperature": 95}]',
                         'lungo': '[{"mode": 1, "amount": 120, "tank": 0, "temperature": 95}]',
                         'flat_white': '[{"mode": 2, "amount": 70, "tank": 20, "temperature": 95}]',
                         'clearing': '[{"mode": 4, "amount": 0, "tank": 0, "temperature": 95}]',
                         'heating': '[{"mode": 5, "amount": 0, "tank": 0, "temperature": 95}]',
                         'hot_milk': '[{"mode": 6, "amount": 0, "tank": 15, "temperature": 95}]'
                     }
                else:
                    self._select_options = json.loads(json.dumps(SELECT_COFFEEMAKER_ROG[0].options))
            else:
                self._select_options = json.loads(json.dumps(SELECT_COFFEEMAKER[0].options))

        if self._custom_data_select is not None:
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker" and "SELECT_COOKER_options" in self._custom_data_select:
#                self._select_options = json.loads(json.dumps(SELECT_COOKER[0].options))
                for key, value in self._custom_data_select["SELECT_COOKER_options"].items():
                    self._select_options[key] = json.dumps([value])
#                _LOGGER.debug("cooker %s", self._select_options)
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "air_fryer" and "SELECT_AIRFRYER_options" in self._custom_data_select:
#                self._select_options = json.loads(json.dumps(SELECT_COOKER[0].options))
                for key, value in self._custom_data_select["SELECT_AIRFRYER_options"].items():
                    self._select_options[key] = json.dumps([value])
#                _LOGGER.debug("cooker %s", self._select_options)
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                if int(self.device_type) == 45 and "SELECT_COFFEEMAKER_ROG_options" in self._custom_data_select:
#                    self._select_options = json.loads(json.dumps(SELECT_COFFEEMAKER_ROG[0].options))
                    for key, value in self._custom_data_select["SELECT_COFFEEMAKER_ROG_options"].items():
                        self._select_options[key] = json.dumps([value])
#                    _LOGGER.debug("coffee_rog %s", self._select_options)
                elif "SELECT_COFFEEMAKER_options" in self._custom_data_select:
#                    self._select_options = json.loads(json.dumps(SELECT_COFFEEMAKER[0].options))
                    for key, value in self._custom_data_select["SELECT_COFFEEMAKER_options"].items():
                        self._select_options[key] = json.dumps([value])
#                    _LOGGER.debug("coffee %s", self._select_options)


        #    self._attr_options = list(self._select_options.keys())
        #    self._attr_current_option = self._attr_options[0]



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

        
    def get_state_by_unique_id(self, entity_domain, entity_name):
        entity_unique_id = f"{self.device_id}_{entity_name}"
        entity_registry = er.async_get(self.hass)
        entity_id = entity_registry.async_get_entity_id(entity_domain, "polaris", entity_unique_id)
        return self.hass.states.get(entity_id).state


    async def async_press(self) -> None:
        if (self.device_type in POLARIS_COFFEEMAKER_TYPE):
            if self.entity_description.key == "button_stop":
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", "0")
                
                # Get entity_id by unique_id
                # Работает
                zzzz = self.get_state_by_unique_id("number", "amount")
                _LOGGER.debug("state %s", zzzz)
                
            else:
                state_amount = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_amount").state
                state_weight = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_weight").state
                state_tank = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_tank").state
                state_pressure = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_pressure").state
                state_speed = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_speed").state
                state_temp = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_temperature").state
                state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_select_mode_cofeemaker").state
                state_coffee_maker = self.hass.states.get(f"switch.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_power").state
                if state_coffee_maker != "off":
                    if state_amount != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"amount", state_amount)
                    if state_weight != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"weight", state_weight)
                    if state_tank != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"tank", state_tank)
                    if state_pressure != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"pressure", state_pressure)
                    if state_speed != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"speed", state_speed)
                    if state_temp != "unavailable":
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"temperature", state_temp)
                    if state_mode != "not_selected":
 # !!!
                        command_mode = self._select_options[state_mode]
                        coffee_mode = json.loads(command_mode)
                        mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", coffee_mode[0]["mode"])

        if (self.device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
            if self.entity_description.key == "button_stop":
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", "0")
            else:
                state_amount = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_amount").state
                state_tank = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_tank").state
                state_temp = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_temperature").state
                state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_select_mode_cofeemaker_rog").state
                state_cappuccinator = self.hass.states.get(f"binary_sensor.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_cappuccinator").state
                state_power = self.hass.states.get(f"switch.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_power").state
                if state_power == "off":
                    mqtt.publish(self.hass, f"{self.mqtt_root}/{self.device_prefix_topic}/control/mode", 5)
                if state_cappuccinator == "off" and state_mode in ("cappuccino", "double_cappuccino", "latte", "double_latte", "flat_white", "hot_milk"):
                    mqtt.publish(self.hass, f"{self.mqtt_root}/{self.device_prefix_topic}/state/error/code", "99")
                    return
                elif state_mode == "not_selected":
                    mqtt.publish(self.hass, f"{self.mqtt_root}/{self.device_prefix_topic}/state/error/code", "98")
                    return
                else:
                    if state_amount == "unavailable":
                        state_amount = "0"
                    if state_tank == "unavailable":
                        state_tank = "0"
                    mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"amount", state_amount)
                    mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"temperature", state_temp)
                    mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"tank", state_tank)
                    command_mode = self._select_options[state_mode]
                    coffee_mode = json.loads(command_mode)
                    mqtt.publish(self.hass, self.entity_description.mqttTopicCommand+"mode", coffee_mode[0]["mode"])
                    mqtt.publish(self.hass, f"{self.mqtt_root}/{self.device_prefix_topic}/state/error/code", "00")


        if POLARIS_DEVICE[int(self.device_type)]['class'] in ("cooker", "air_fryer"):
            if self.entity_description.key == "button_stop":
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, "[]")
            else:
                state_temp = self.hass.states.get(f"number.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_set_temperature").state
                state_time = self.hass.states.get(f"time.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_cooking_time").state
                state_time_obj = datetime.strptime(state_time, "%H:%M:%S")
                state_time_seconds = state_time_obj.hour * 3600 + state_time_obj.minute * 60 + state_time_obj.second
                state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}_select_mode_cooker").state
# multi mode command +
                command_mode = self._select_options[state_mode]
                cook_mode = json.loads(command_mode)[0]
                if isinstance(cook_mode, dict):
                    cook_mode = [cook_mode]
                    payload = "[{" + f'"mode":{cook_mode[0]["mode"]},"time":{state_time_seconds},"temperature":{state_temp}' + "}]"
                else:
                    payload = "[{"+f'"mode":{cook_mode[0]["mode"]},"time":{state_time_seconds},"temperature":{state_temp}' + "}," + ','.join(json.dumps(dat) for dat in cook_mode[1:]) + "]"
                mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, payload)
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "humidifier":
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, self.entity_description.payloads)
        if (self.device_type in POLARIS_CLIMATE_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, self.entity_description.payloads)
        if (self.device_type in POLARIS_AIRCLEANER_TYPE):
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommand, self.entity_description.payloads)
