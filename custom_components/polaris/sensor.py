"""The Polaris IQ Home component."""
from __future__ import annotations

import copy
import json
import logging

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .common import PolarisBaseEntity

# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    SENSORS_ALL_DEVICES,
    SENSORS_HUMIDIFIER,
    PolarisSensorEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
)

#_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    deviceID = config.data["DEVICEID"]
    devicetype = config.data[DEVICETYPE]
    sensorList = []

    #Kettle
    if (devicetype in POLARIS_KETTLE_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{deviceID}/state/{description.key}")
            sensorList.append(
                PolarisSensor(
                    uniqueID=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    #Kettle with weight
    elif (devicetype in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{deviceID}/state/{description.key}")
            sensorList.append(
                PolarisSensor(
                    uniqueID=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_WEIGHT_CP = copy.deepcopy(SENSORS_WEIGHT)
        for description in SENSORS_WEIGHT_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{deviceID}/state/{description.key}")
            sensorList.append(
                PolarisSensor(
                    uniqueID=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    # Humidifier
    elif (devicetype in POLARIS_HUMIDDIFIER_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{deviceID}/state/{description.key}")
            sensorList.append(
                PolarisSensor(
                    uniqueID=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_HUMIDIFIER_CP = copy.deepcopy(SENSORS_HUMIDIFIER)
        for description in SENSORS_HUMIDIFIER_CP:
            description.mqttTopicCurrentValue = (
                f"{mqttRoot}/{deviceID}/state/{description.key}"
            )
            sensorList.append(
                PolarisSensor(
                    uniqueID=f"{integrationUniqueID}",
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    async_add_entities(sensorList)


class PolarisSensor(PolarisBaseEntity, SensorEntity):

    entity_description: PolarisSensorEntityDescription

    def __init__(
        self,
        uniqueID: str | None,
        device_friendly_name: str,
        mqtt_root: str,
        description: PolarisSensorEntityDescription,
        device_type: str,
        device_id: str,
    ) -> None:
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id,
        )
        self.entity_description = description
        self._attr_unique_id = slugify(f"{uniqueID}-{description.name}")
        self.entity_id = f"sensor.{uniqueID}-{description.name}"
        self._attr_has_entity_name = True

    async def async_added_to_hass(self):
        @callback
        def message_received(message):
            self._attr_native_value = message.payload

            # Convert data if a conversion function is defined
            if self.entity_description.value_fn is not None:
                self._attr_native_value = self.entity_description.value_fn(
                    self._attr_native_value
                )

            # Map values as defined in the value map dict.
            # First try to map integer values, then string values.
            # If no value can be mapped, use original value without conversion.
            if self.entity_description.valueMap is not None:
                try:
                    self._attr_native_value = self.entity_description.valueMap.get(
                        int(self._attr_native_value)
                    )
                except ValueError:
                    self._attr_native_value = self.entity_description.valueMap.get(
                        self._attr_native_value, self._attr_native_value
                    )
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

