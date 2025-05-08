"""The Polaris IQ Home component."""
from __future__ import annotations

import copy
import json
import logging
import struct

from homeassistant.components import mqtt
from homeassistant.components.sensor import DOMAIN, SensorEntity
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
    POLARIS_DEVICE,
    SENSORS_ALL_DEVICES,
    SENSORS_WEIGHT,
    SENSORS_HUMIDIFIER,
    SENSORS_COOKER,
    SENSORS_COFFEEMAKER,
    SENSORS_COFFEEMAKER_ROG,
    SENSORS_CLIMATE,
    SENSORS_AIRCLEANER,
    SENSORS_VACUUM,
    PolarisSensorEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
    POLARIS_VACUUM_TYPE,
    KETTLE_ERROR,
    HUMIDDIFIER_ERROR,
    COOKER_ERROR,
    COFFEEMAKER_ERROR,
    AIRCLEANER_ERROR,
    VACUUM_ERROR,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    integrationUniqueID = config.unique_id
    mqttRoot = config.data[MQTT_ROOT_TOPIC]
    deviceID = config.data["DEVICEID"]
    devicetype = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    if len(device_prefix_topic)>15:
        mqtt.publish(hass, f"{mqttRoot}/{device_prefix_topic}/state/devtype", devicetype, 0, True)
    sensorList = []
    #Kettle
    if (devicetype in POLARIS_KETTLE_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    #Kettle with weight
    if (devicetype in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_WEIGHT_CP = copy.deepcopy(SENSORS_WEIGHT)
        for description in SENSORS_WEIGHT_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    # Humidifier
    if (devicetype in POLARIS_HUMIDDIFIER_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_HUMIDIFIER_CP = copy.deepcopy(SENSORS_HUMIDIFIER)
        for description in SENSORS_HUMIDIFIER_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{deviceID}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    # Cooker
    if (devicetype in POLARIS_COOKER_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_COOKER_CP = copy.deepcopy(SENSORS_COOKER)
        for description in SENSORS_COOKER_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    # Coffeemaker
    if (devicetype in POLARIS_COFFEEMAKER_TYPE):
        # Create sensors for all devices 
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_COFFEEMAKER_CP = copy.deepcopy(SENSORS_COFFEEMAKER)
        for description in SENSORS_COFFEEMAKER_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    if (devicetype in POLARIS_COFFEEMAKER_ROG_TYPE):
        # Create sensors for coffeemaker 
        SENSORS_COFFEEMAKER_ROG_CP = copy.deepcopy(SENSORS_COFFEEMAKER_ROG)
        for description in SENSORS_COFFEEMAKER_ROG_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    if (devicetype in POLARIS_CLIMATE_TYPE):
        # Create sensors for climate 
        SENSORS_CLIMATE_CP = copy.deepcopy(SENSORS_CLIMATE)
        for description in SENSORS_CLIMATE_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
        SENSORS_ALL_DEVICES_CP = copy.deepcopy(SENSORS_ALL_DEVICES)
        for description in SENSORS_ALL_DEVICES_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    if (devicetype in POLARIS_AIRCLEANER_TYPE):
        SENSORS_AIRCLEANER_CP = copy.deepcopy(SENSORS_AIRCLEANER)
        for description in SENSORS_AIRCLEANER_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
                    description=description,
                    device_friendly_name=deviceID,
                    mqtt_root=mqttRoot,
                    device_type=devicetype,
                    device_id=deviceID,
                )
            )
    if (devicetype in POLARIS_VACUUM_TYPE):
        SENSORS_VACUUM_CP = copy.deepcopy(SENSORS_VACUUM)
        for description in SENSORS_VACUUM_CP:
            description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key}")
            description.device_prefix_topic = device_prefix_topic
            sensorList.append(
                PolarisSensor(
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
#        uniqueID: str | None,
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
        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class']}_{POLARIS_DEVICE[int(device_type)]['model']}_{description.name}"
        self._attr_has_entity_name = True
        self._attr_available = False


    def bytes_to_int16_array(self, byte_data, byteorder='little'):
        """
        Преобразует байтовую строку в массив int16.
        Аргументы:
            byte_data: Байтовая строка для преобразования (bytes).
            byteorder: Порядок байтов ('little' или 'big'), по умолчанию 'little'.
        Возвращает:
            Массив int16 значений (list of int).
        Вызывает исключение ValueError:
            Если длина byte_data нечетная.
            Если byteorder не является 'little' или 'big'.
        """
        if len(byte_data) % 2 != 0:
            raise ValueError("Длина байтовой строки должна быть четной для int16 преобразования.")
        if byteorder not in ('little', 'big'):
            raise ValueError("Неверный порядок байтов. Допустимые значения: 'little', 'big'.")
        endian_prefix = '<' if byteorder == 'little' else '>' # '<' - little-endian, '>' - big-endian
        format_string = endian_prefix + 'h' * (len(byte_data) // 2) # 'h' - signed short (2 bytes - int16)
        return list(struct.unpack(format_string, byte_data))








    async def async_added_to_hass(self):
        @callback
        def message_received(message):
            payload_message = message.payload
            if self.entity_description.name == "error":
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "cooker":
                    dev_error = COOKER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "kettle":
                    dev_error = KETTLE_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "humidifier":
                    dev_error = HUMIDDIFIER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                    dev_error = COFFEEMAKER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "air-cleaner":
                    dev_error = AIRCLEANER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "cleaner":
                    dev_error = VACUUM_ERROR[payload_message]
                payload_message = dev_error
            if self.entity_description.name == "filter_retain":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[0]
            if self.entity_description.name == "clean_retain":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[1]
            if self.entity_description.name == "mode":
                payload_message = self.entity_description.valueMap[payload_message]
            if self.entity_description.name == "power_state":
                payload_message = self.entity_description.valueMap[payload_message]
            if self.entity_description.name == "go_area":
#                _LOGGER.debug("go_area %s", payload_message)

                list_dubleint = self.bytes_to_int16_array(payload_message)
#                _LOGGER.debug("bytes_to_int16 %s",list_dubleint)
#                list_dubleint = self.bytes_to_int16_array(payload_message, byteorder='big')
#                _LOGGER.debug("list_integers %s",list_dubleint)

                
                payload_message = list_dubleint
                
            self._attr_native_value = payload_message
            self.async_write_ha_state()

        if self.entity_description.name == "go_area":
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                message_received,
                1,
                None,
            )
        else:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                message_received,
                1,
            )

        @callback
        async def entity_availability(message):
            if self.entity_description.name != "available":
                if str(message.payload).lower() in ("1", "true"):
                    self._attr_available = False
                else:
                    self._attr_available = True
                self.async_write_ha_state()
            
        await mqtt.async_subscribe(self.hass, f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/error/connection", entity_availability, 1)
