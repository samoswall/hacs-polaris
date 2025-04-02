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
from homeassistant.components.vacuum import (
    DOMAIN,
    ATTR_CLEANED_AREA,
    StateVacuumEntity,
#    VacuumActivity,
    VacuumEntityFeature,
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
    VACUUM,
    PolarisSelectEntityDescription,
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
    vacuumList = []

    if (device_type in POLARIS_VACUUM_TYPE):
        VACUUM_LC = copy.deepcopy(VACUUM)
        for description in VACUUM_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            vacuumList.append(
                PolarisVacuum(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(vacuumList, update_before_add=True)


class PolarisVacuum(PolarisBaseEntity, StateVacuumEntity):

    entity_description: PolarisVacuumEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisVacuumEntityDescription,
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
        
        self._attr_fan_speed="min"
        self._attr_fan_speed_list = ["min", "medium", "high", "max"]
        self._attr_supported_features = (
              VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.RETURN_HOME
            | VacuumEntityFeature.CLEAN_SPOT
            | VacuumEntityFeature.STOP
            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.START
            | VacuumEntityFeature.LOCATE
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.SEND_COMMAND
            | VacuumEntityFeature.FAN_SPEED
        )
#        self._entity_component_unrecorded_attributes = frozenset({ATTR_FAN_SPEED_LIST})

        self._attr_battery_icon="mdi:vacuum"
        self._attr_battery_level=70
        
 #       self._attr_activity=
