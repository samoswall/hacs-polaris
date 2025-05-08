"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy
import datetime
import os

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
    CUSTOM_SELECT_FILE_PATH,
    SELECT_KETTLE,
    SELECT_COOKER,
    SELECT_COFFEEMAKER,
    SELECT_COFFEEMAKER_ROG,
    SELECT_CLIMATE,
    SELECT_VACUUM,
    PolarisSelectEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_VACUUM_TYPE,
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
    selectList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        SELECT_KETTLE_LC = copy.deepcopy(SELECT_KETTLE)
        for description in SELECT_KETTLE_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.device_prefix_topic = device_prefix_topic
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COOKER_TYPE):
        SELECT_COOKER_LC = copy.deepcopy(SELECT_COOKER)
        for description in SELECT_COOKER_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.device_prefix_topic = device_prefix_topic
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_TYPE):
        SELECT_COFFEEMAKER_LC = copy.deepcopy(SELECT_COFFEEMAKER)
        for description in SELECT_COFFEEMAKER_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.device_prefix_topic = device_prefix_topic
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
        SELECT_COFFEEMAKER_ROG_LC = copy.deepcopy(SELECT_COFFEEMAKER_ROG)
        for description in SELECT_COFFEEMAKER_ROG_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.device_prefix_topic = device_prefix_topic
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_CLIMATE_TYPE):
        SELECT_CLIMATE_LC = copy.deepcopy(SELECT_CLIMATE)
        for description in SELECT_CLIMATE_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.device_prefix_topic = device_prefix_topic
            selectList.append(
                PolarisSelect(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_VACUUM_TYPE):
        SELECT_VACUUM_LC = copy.deepcopy(SELECT_VACUUM)
        for description in SELECT_VACUUM_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.device_prefix_topic = device_prefix_topic
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
        self._attr_has_entity_name = True
        
        
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "kettle" or POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker" or POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker" or POLARIS_DEVICE[int(self.device_type)]['class'] == "cleaner":
            self._select_options = json.loads(json.dumps(SELECT_COFFEEMAKER[0].options))


        self._custom_data_select = self._read_file()
        if self._custom_data_select is not None:
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "kettle" and "SELECT_KETTLE_options" in self._custom_data_select:
#                self.entity_description.options = json.loads(json.dumps(self.entity_description.options))
                for key, value in self._custom_data_select["SELECT_KETTLE_options"].items():
                    self.entity_description.options[key] = value
#                _LOGGER.debug("kettle %s", self.entity_description.options)
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker" and "SELECT_COOKER_options" in self._custom_data_select:
#                self.entity_description.options = json.loads(json.dumps(self.entity_description.options))
                for key, value in self._custom_data_select["SELECT_COOKER_options"].items():
                    self.entity_description.options[key] = json.dumps([value])
#                _LOGGER.debug("cooker %s", self.entity_description.options)
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                if int(self.device_type) == 45 and "SELECT_COFFEEMAKER_ROG_options" in self._custom_data_select:
#                    self.entity_description.options = json.loads(json.dumps(self.entity_description.options))
                    for key, value in self._custom_data_select["SELECT_COFFEEMAKER_ROG_options"].items():
                        self.entity_description.options[key] = json.dumps([value])
#                    _LOGGER.debug("coffee_rog %s", self.entity_description.options)
                elif "SELECT_COFFEEMAKER_options" in self._custom_data_select:
#                    self.entity_description.options = json.loads(json.dumps(self.entity_description.options))
                    for key, value in self._custom_data_select["SELECT_COFFEEMAKER_options"].items():
                        self.entity_description.options[key] = json.dumps([value])
#                    _LOGGER.debug("coffee %s", self.entity_description.options)
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "cleaner" and "SELECT_VACUUM_rooms" in self._custom_data_select and self.entity_description.key == "select_room":
#                self.entity_description.options = json.loads(json.dumps(self.entity_description.options))
                for key, value in self._custom_data_select["SELECT_VACUUM_rooms"].items():
                    self.entity_description.options[key] = json.dumps([value])

        self._attr_options = list(self.entity_description.options.keys())
        self._attr_current_option = self._attr_options[0]
        self._attr_available = False

    def _read_file(self):
        file_path = CUSTOM_SELECT_FILE_PATH
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = json.loads(file.read())
        else:
            content = None
        return content

#    @property
#    def available(self):
#        return self._attr_current_option is not None

    def key_from_option(self, option: str):
        try:
            return next(
                key
                for key, value in self.entity_description.options.items()
                if json.loads(value)[0]["mode"] == option
            )
        except StopIteration:
            return None

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker":
            cook_time = json.loads(self.entity_description.options[option])
            service_data = {}
            service_data["entity_id"] = f"time.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_cooking_time"
            service_data["time"] = str(datetime.timedelta(seconds=cook_time[0]["time"]))
            await self.hass.services.async_call("time", "set_value", service_data)
            service_data = {}
            service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_set_temperature"
            service_data["value"] = cook_time[0]["temperature"]
            await self.hass.services.async_call("number", "set_value", service_data)
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "kettle":
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandTemperature, self.entity_description.options[option])
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, 3)
        if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
            if int(self.device_type) == 45:
                coffee_mode = json.loads(self.entity_description.options[option])
                
                service_data = {}
                service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_tank"
                if coffee_mode[0]["tank"] != 0:
                   service_data["value"] = str(coffee_mode[0]["tank"])
                else:
                   service_data["value"] = 7.777
                await self.hass.services.async_call("number", "set_value", service_data)
                
                service_data = {}
                service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_amount"
                if coffee_mode[0]["amount"] != 0:
                    service_data["value"] = str(coffee_mode[0]["amount"])
                else:
                    service_data["value"] = 100.777
                await self.hass.services.async_call("number", "set_value", service_data)
                
                service_data = {}
                service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_temperature"
                if coffee_mode[0]["temperature"] != 0:
                    service_data["value"] = str(coffee_mode[0]["temperature"])
                else:
                    service_data["value"] = 100.777
                await self.hass.services.async_call("number", "set_value", service_data)
                
            else:
                coffee_mode = json.loads(self.entity_description.options[option])
                for key, val in coffee_mode[0].items():
                    if key == "mode":
                        mode = val
                    elif val != 0:
                        service_data = {}
                        service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_{key}"
                        service_data["value"] = str(val)
                        await self.hass.services.async_call("number", "set_value", service_data)
                    else:
                        if key == "weight": 
                            val = "7.777"
                        else:
                            val = "55.777"
                        service_data = {}
                        service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_{key}"
                        service_data["value"] = val
                        await self.hass.services.async_call("number", "set_value", service_data)
        if int(self.device_type) == 69:
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, self.entity_description.options[option])

    async def async_added_to_hass(self):
        @callback
        def message_received_sel(message):
            payload = message.payload
            if payload in ("0", "[]"):
                self._attr_current_option = self._attr_options[0]
                self.async_write_ha_state()
            elif POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker":
                sel_mode = json.loads(payload)[0]["mode"]
          #      if int(sel_mode)>0:
          #          self.switch.set_available(True)
          #      else:
          #          self.switch.set_available(False)
                sel_opt = self.key_from_option(sel_mode)
                self._attr_current_option = sel_opt
                self.async_write_ha_state()
            elif int(self.device_type) == 45:
                sel_opt = self.key_from_option(int(payload))
                self._attr_current_option = sel_opt
                self.async_write_ha_state()
            elif int(self.device_type) == 69:
                self._attr_current_option = self._attr_options[int(payload)]
                self.async_write_ha_state()
        await mqtt.async_subscribe(self.hass, self.entity_description.mqttTopicCurrentMode, message_received_sel, 1)
        
        @callback
        async def entity_availability(message):
            if self.entity_description.name != "available":
                if str(message.payload).lower() in ("1", "true"):
                    self._attr_available = False
                else:
                    self._attr_available = True
                self.async_write_ha_state()
            
        await mqtt.async_subscribe(self.hass, f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/error/connection", entity_availability, 1)

