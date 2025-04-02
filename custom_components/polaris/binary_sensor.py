"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable, List
import copy
from datetime import datetime

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.binary_sensor import (
    DOMAIN,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# Device
from homeassistant.helpers.device_registry import DeviceEntry, DeviceEntryDisabler
from homeassistant.helpers import device_registry as dev_reg
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_UNAVAILABLE

from .common import PolarisBaseEntity

# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    BINARYSENSOR_KETTLE,
    BINARYSENSOR_LID,
    BINARYSENSOR_WATER_TANK,
    BINARYSENSOR_CAPPUCCINATOR,
    BINARYSENSOR_AVAILABLE,
    PolarisBinarySensorEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COOKER_WITH_LID_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:

    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    binarysensorList = []
    
    if (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
            BINARYSENSOR_KETTLE_LC = copy.deepcopy(BINARYSENSOR_KETTLE)
            for description in BINARYSENSOR_KETTLE_LC:
                description.mqttTopicStatus = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStatus}"
                binarysensorList.append(
                    PolarisBinarySensor(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_COOKER_WITH_LID_TYPE):
            BINARYSENSOR_LID_LC = copy.deepcopy(BINARYSENSOR_LID)
            for description in BINARYSENSOR_LID_LC:
                description.mqttTopicStatus = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStatus}"
                binarysensorList.append(
                    PolarisBinarySensor(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_HUMIDDIFIER_TYPE):
            BINARYSENSOR_WATER_TANK_LC = copy.deepcopy(BINARYSENSOR_WATER_TANK)
            for description in BINARYSENSOR_WATER_TANK_LC:
                description.mqttTopicStatus = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStatus}"
                binarysensorList.append(
                    PolarisBinarySensor(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
            BINARYSENSOR_CAPPUCCINATOR_LC = copy.deepcopy(BINARYSENSOR_CAPPUCCINATOR)
            for description in BINARYSENSOR_CAPPUCCINATOR_LC:
                description.mqttTopicStatus = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStatus}"
                binarysensorList.append(
                    PolarisBinarySensor(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_KETTLE_TYPE or
        device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE or
        device_type in POLARIS_HUMIDDIFIER_TYPE or
        device_type in POLARIS_COOKER_WITH_LID_TYPE or
        device_type in POLARIS_COFFEEMAKER_ROG_TYPE or
        device_type in POLARIS_COFFEEMAKER_TYPE or
        device_type in POLARIS_CLIMATE_TYPE or
        device_type in POLARIS_AIRCLEANER_TYPE):
            BINARYSENSOR_AVAILABLE_LC = copy.deepcopy(BINARYSENSOR_AVAILABLE)
            for description in BINARYSENSOR_AVAILABLE_LC:
                description.mqttTopicStatus = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStatus}"
                binarysensorList.append(
                    PolarisBinarySensor(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    
    async_add_entities(binarysensorList, update_before_add=True)


class PolarisBinarySensor(PolarisBaseEntity, BinarySensorEntity):

    entity_description: PolarisBinarySensorEntityDescription

    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisBinarySensorEntityDescription,
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
        self._attr_is_on = True
        self.device_entities = []

    async def async_added_to_hass(self):
        @callback
        async def message_received_base(message):
            if int(self.device_type) == 45:
                if int(message.payload) == 255:
                    self._attr_is_on = False
                    service_data = {}
                    service_data["entity_id"] = f"number.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_tank"
                    service_data["value"] = 7.777
                    await self.hass.services.async_call("number", "set_value", service_data)
                else:
                    self._attr_is_on = True
            elif str(message.payload).lower() in ("1", "true"):
                if self.entity_description.name == "available":
                    self._attr_is_on = False
                    await self.update_device_availability(False)
                else:
                    self._attr_is_on = True
            elif str(message.payload).lower() in ("0", "false"):
                if self.entity_description.name == "available":
                    self._attr_is_on = True
                    await self.update_device_availability(True)
                else:
                    self._attr_is_on = False
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicStatus,
            message_received_base,
            1,
        )


    async def get_device_entities(self) -> List[Entity]:
        """Return a list of entities that belong to the same device as this binary sensor"""
        entities = []
        for entity in self.hass.entities:
            dev_find = f"{POLARIS_DEVICE[int(self.device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_').lower()}"
            if dev_find in entity.entity_id:
                entities.append(entity.entity_id)
        return entities




    async def update_device_availability(self, available: bool):
        """Обновляет статус устройства в Device Registry."""
        dev_registry = dev_reg.async_get(self.hass)
        device = dev_registry.async_get_device(self.device_info["identifiers"])
        
        if device:
            for entry in self.hass.config_entries.async_entries():
                if entry.domain == "polaris" and entry.unique_id == f"{POLARIS_DEVICE[int(self.device_type)]['class']}-{POLARIS_DEVICE[int(self.device_type)]['model']}-{self.device_id}":
                    config_entries = entry
            if available:
                dev_registry.async_update_device(device.id, disabled_by = None)
                state = self.hass.states.get(self.entity_id)
                if state == None:
                    delta_time = 1000
                else:
                    self._new_time_available = datetime.now().timestamp()
                    delta_time = self._new_time_available - state.last_changed.timestamp()
                if delta_time > 5:
                    await self.hass.config_entries.async_reload(config_entries.entry_id)
            else:
                dev_registry.async_update_device(device.id, disabled_by = DeviceEntryDisabler.INTEGRATION)

