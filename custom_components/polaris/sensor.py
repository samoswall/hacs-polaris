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
    SENSORS_RUSCLIMATE_HUMIDIFIER,
    SENSORS_COOKER,
    SENSORS_COFFEEMAKER,
    SENSORS_COFFEEMAKER_ROG,
    SENSORS_CLIMATE,
    SENSORS_CLIMATE_200,
    SENSORS_AIRCLEANER,
    SENSORS_AIRCLEANER_EAP,
    SENSORS_VACUUM,
    SENSORS_WINDOWCLEANER,
    SENSORS_WATER_BOILER,
    SENSORS_IRRIGATOR,
    SENSORS_HEATER,
    SENSORS_AIRCONDITIONER,
    SENSORS_THERMOSTAT,
    SENSOR_VACUUM_EXPENDABLE_MOP,
    SENSOR_VACUUM_EXPENDABLE_DUST,
    SENSORS_FAN,
    PolarisSensorEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
    POLARIS_AIRCLEANER_EAP_TYPE,
    POLARIS_VACUUM_TYPE,
    POLARIS_VACUUM_EXPENDABLE_DUST,
    POLARIS_VACUUM_EXPENDABLE_MOP,
    POLARIS_VACUUM_SENSORS_01_PROGR_DATA,
    POLARIS_VACUUM_SENSORS_02_PROGR_DATA,
    POLARIS_VACUUM_SENSORS_03_PROGR_DATA,
    SENSORS_VACUUM_TOTAL_CLEAN,
    POLARIS_BOILER_TYPE,
    POLARIS_IRRIGATOR_TYPE,
    POLARIS_HEATER_TYPE,
    POLARIS_AIRCONDITIONER_TYPE,
    POLARIS_THERMOSTAT_TYPE,
    POLARIS_FAN_TYPE,
    POLARIS_WINDOWCLEANER_TYPE,
    KETTLE_ERROR,
    HUMIDDIFIER_ERROR,
    COOKER_ERROR,
    COFFEEMAKER_ERROR,
    AIRCLEANER_ERROR,
    WINDOWCLEANER_ERROR,
    POLARIS_VACUUM_01_ERROR_CODE,
    POLARIS_VACUUM_02_ERROR_CODE,
    POLARIS_VACUUM_03_ERROR_CODE,
    POLARIS_VACUUM_04_ERROR_CODE,
    POLARIS_VACUUM_05_ERROR_CODE,
    POLARIS_VACUUM_06_ERROR_CODE,
    POLARIS_VACUUM_07_ERROR_CODE,
    POLARIS_VACUUM_08_ERROR_CODE,
    POLARIS_VACUUM_09_ERROR_CODE,
    POLARIS_VACUUM_10_ERROR_CODE,
    POLARIS_VACUUM_11_ERROR_CODE,
    VACUUM_01_ERROR,
    VACUUM_02_ERROR,
    VACUUM_03_ERROR,
    VACUUM_04_ERROR,
    VACUUM_05_ERROR,
    VACUUM_06_ERROR,
    VACUUM_07_ERROR,
    VACUUM_08_ERROR,
    VACUUM_09_ERROR,
    VACUUM_10_ERROR,
    VACUUM_11_ERROR,
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
        if devicetype == "177":
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
      if devicetype == "881":
        SENSORS_RUSCLIMATE_HUMIDIFIER_CP = copy.deepcopy(SENSORS_RUSCLIMATE_HUMIDIFIER)
        for description in SENSORS_RUSCLIMATE_HUMIDIFIER_CP:
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
      else:
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
          if (devicetype != "835" or description.translation_key != "clean_retain"):
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
        # Create sensors for climate asp-200 or asp-100
        if (devicetype == "859"):
            SENSORS_CLIMATE_CP = copy.deepcopy(SENSORS_CLIMATE_200)
        else:
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
        if (devicetype in ("140","172")):  # PAW-0804
            SENSORS_COOKER_CP = copy.deepcopy(SENSORS_COOKER) # оставшееся время
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
            SENSORS_RUSCLIMATE_HUMIDIFIER_CP = copy.deepcopy(SENSORS_RUSCLIMATE_HUMIDIFIER)
            for description in SENSORS_RUSCLIMATE_HUMIDIFIER_CP:
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
        else:
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
    if (devicetype in POLARIS_AIRCLEANER_EAP_TYPE):
        SENSORS_AIRCLEANER_EAP_CP = copy.deepcopy(SENSORS_AIRCLEANER_EAP)
        for description in SENSORS_AIRCLEANER_EAP_CP:
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
    if (int(devicetype) in POLARIS_VACUUM_EXPENDABLE_DUST):
        SENSOR_VACUUM_EXPENDABLE_DUST_CP = copy.deepcopy(SENSOR_VACUUM_EXPENDABLE_DUST)
        for description in SENSOR_VACUUM_EXPENDABLE_DUST_CP:
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
    if (int(devicetype) in POLARIS_VACUUM_EXPENDABLE_MOP):
        SENSOR_VACUUM_EXPENDABLE_MOP_CP = copy.deepcopy(SENSOR_VACUUM_EXPENDABLE_MOP)
        for description in SENSOR_VACUUM_EXPENDABLE_MOP_CP:
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
    if (int(devicetype) in POLARIS_VACUUM_SENSORS_01_PROGR_DATA or int(devicetype) in POLARIS_VACUUM_SENSORS_02_PROGR_DATA or int(devicetype) in POLARIS_VACUUM_SENSORS_03_PROGR_DATA):
        SENSORS_VACUUM_TOTAL_CLEAN_CP = copy.deepcopy(SENSORS_VACUUM_TOTAL_CLEAN)
        for description in SENSORS_VACUUM_TOTAL_CLEAN_CP:
            if int(devicetype) in POLARIS_VACUUM_SENSORS_02_PROGR_DATA:
                description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key[:-1]}2")
            elif int(devicetype) in POLARIS_VACUUM_SENSORS_03_PROGR_DATA:
                description.mqttTopicCurrentValue = (f"{mqttRoot}/{device_prefix_topic}/state/{description.key[:-1]}3")
            else:
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
    if (devicetype in POLARIS_BOILER_TYPE):
        SENSORS_WATER_BOILER_CP = copy.deepcopy(SENSORS_WATER_BOILER)
        for description in SENSORS_WATER_BOILER_CP:
            if (devicetype not in {"833","807","802"} or description.translation_key != "anode_retain"):
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
    if (devicetype in POLARIS_IRRIGATOR_TYPE):
        SENSORS_IRRIGATOR_CP = copy.deepcopy(SENSORS_IRRIGATOR)
        for description in SENSORS_IRRIGATOR_CP:
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
    if (devicetype in POLARIS_HEATER_TYPE):
        SENSORS_HEATER_CP = copy.deepcopy(SENSORS_HEATER)
        for description in SENSORS_HEATER_CP:
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
    if (devicetype in POLARIS_AIRCONDITIONER_TYPE):
        SENSORS_AIRCONDITIONER_CP = copy.deepcopy(SENSORS_AIRCONDITIONER)
        for description in SENSORS_AIRCONDITIONER_CP:
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
    if (devicetype in POLARIS_THERMOSTAT_TYPE):
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
        SENSORS_THERMOSTAT_CP = copy.deepcopy(SENSORS_THERMOSTAT)
        for description in SENSORS_THERMOSTAT_CP:
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
    if (devicetype in POLARIS_FAN_TYPE):
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
        SENSORS_FAN_CP = copy.deepcopy(SENSORS_FAN)
        for description in SENSORS_FAN_CP:
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
    if (devicetype in POLARIS_WINDOWCLEANER_TYPE):
        for description in copy.deepcopy(SENSORS_WINDOWCLEANER):
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
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device_type)]['model'].replace('-', '_').lower()}_{description.name.replace(' ', '_').lower()}"
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
                    payload_message = COOKER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "kettle":
                    payload_message = KETTLE_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "humidifier":
                    payload_message = HUMIDDIFIER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                    payload_message = COFFEEMAKER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "air_cleaner":
                    payload_message = AIRCLEANER_ERROR[payload_message]
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "window_cleaner":
                    payload_message = WINDOWCLEANER_ERROR.get(payload_message, payload_message)
                if POLARIS_DEVICE[int(self.device_type)]['class'] == "cleaner":
                    if int(self.device_type) in POLARIS_VACUUM_01_ERROR_CODE:
                        payload_message = VACUUM_01_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_02_ERROR_CODE:
                        payload_message = VACUUM_02_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_03_ERROR_CODE:
                        payload_message = VACUUM_03_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_04_ERROR_CODE:
                        payload_message = VACUUM_04_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_05_ERROR_CODE:
                        payload_message = VACUUM_05_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_06_ERROR_CODE:
                        payload_message = VACUUM_06_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_07_ERROR_CODE:
                        payload_message = VACUUM_07_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_08_ERROR_CODE:
                        payload_message = VACUUM_08_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_09_ERROR_CODE:
                        payload_message = VACUUM_09_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_10_ERROR_CODE:
                        payload_message = VACUUM_10_ERROR[str(int(payload_message,16))]
                    if int(self.device_type) in POLARIS_VACUUM_11_ERROR_CODE:
                        payload_message = VACUUM_11_ERROR[str(int(payload_message,16))]
            if self.entity_description.name == "filter_retain":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[0]
            if self.entity_description.name == "pre_filter_retain":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[1]
            if self.entity_description.name == "anode_retain":
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
            if self.entity_description.name == "quality":
                payload_message = str( int(payload_message) / 100 )
            if self.entity_description.name == "current_power":
                if self.device_type in ("806","847"):
                    payload_message = str( int(payload_message[:2],16) * 20 )
                else:
                    payload_message = str( int(payload_message[:2],16) * 10 )
            if self.entity_description.name == "side_brush":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[0]
            if self.entity_description.name == "main_brush":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[1]
            if self.entity_description.name == "filter":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[2]
            if self.entity_description.name == "mop":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[3]
            if self.entity_description.name == "dust_container":
                payload_message = payload_message.replace("[","",1).replace("]","",1).split(",")[3]
            if self.entity_description.name == "last_clean_time":
                payload_message = str(int(payload_message)/60)
            if self.entity_description.name == "last_clean_area":
                payload_message = str(int(payload_message)/10000)
            if self.entity_description.name == "total_clean_time":
                payload_message = str((int(payload_message[18:20], 16) *256 + int(payload_message[16:18], 16))/60)
            if self.entity_description.name == "clean_count":
                payload_message = str(int(payload_message[10:12],16) * 256 + int(payload_message[8:10],16))
            if self.entity_description.name == "total_clean_area":
                payload_message = str(int(payload_message[2:4], 16) * 256 + int(payload_message[:2], 16))

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
