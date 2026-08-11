"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.components.water_heater import DOMAIN, WaterHeaterEntity, WaterHeaterEntityFeature
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
    WATER_HEATERS,
    WATER_BOILERS,
    PolarisWaterHeaterEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_BOILER_TYPE,
    KETTLE_WITH_TEA_TIME_MODES,
    KETTLE_WITH_KEEP_WITH_WARM_MODES,
    POLARIS_KETTLE_WITH_TEA_TIME_MODE_TYPE,
    POLARIS_KETTLE_WITH_KEEP_WITH_WARM_MODE_TYPE,
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
    waterheaterList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create water heater for kettle devices
        WATER_HEATERS_LC = copy.deepcopy(WATER_HEATERS)
        for description in WATER_HEATERS_LC:
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicTargetTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicTargetTemperature}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.device_prefix_topic = device_prefix_topic
            waterheaterList.append(
                PolarisWaterHeater(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_BOILER_TYPE):
        # Create water boiler
        WATER_BOILERS_LC = copy.deepcopy(WATER_BOILERS)
        for description in WATER_BOILERS_LC:
            description.mqttTopicCommandTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandTemperature}"
            description.mqttTopicCurrentTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentTemperature}"
            description.mqttTopicTargetTemperature = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicTargetTemperature}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.device_prefix_topic = device_prefix_topic
            waterheaterList.append(
                PolarisWaterHeater(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(waterheaterList, update_before_add=True)

class PolarisWaterHeater(PolarisBaseEntity, WaterHeaterEntity):
    entity_description: PolarisWaterHeaterEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisWaterHeaterEntityDescription,
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
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device_type)]['model'].replace('-', '_').lower()}_{description.key}"
        self.payload_on = description.payload_on
        self.payload_off = description.payload_off
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

        self._attr_min_temp = description.min_temp
        self._attr_max_temp = description.max_temp
        self._attr_target_temperature_high = description.max_temp
        self._attr_target_temperature_low = description.min_temp
        self._attr_target_temperature = description.max_temp
        self._attr_target_temperature_step = 1.0

        self._attr_is_away_mode_on = None
        self._attr_is_on = True
        self._attr_supported_features = WaterHeaterEntityFeature.OPERATION_MODE | WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF

        self._attr_current_operation = description.mode
        self._modes = {}
        if (self.device_type in POLARIS_KETTLE_WITH_KEEP_WITH_WARM_MODE_TYPE):
            self._modes = KETTLE_WITH_KEEP_WITH_WARM_MODES
#            self._attr_operation_list = list(KETTLE_WITH_KEEP_WITH_WARM_MODES.keys())
        elif (self.device_type in POLARIS_KETTLE_WITH_TEA_TIME_MODE_TYPE):
            self._modes = KETTLE_WITH_TEA_TIME_MODES
#            self._attr_operation_list = list(KETTLE_WITH_TEA_TIME_MODES.keys())
        elif (self.device_type in {"802","844","877"}):
            self._modes = {"off": "0", "performance": "1", "electric": "2", "heat_pump": "3"}
        elif (self.device_type == "807"):
            self._modes = {"off": "0", "performance": "1", "electric": "2", "heat_pump": "3", "gas": "5"}
        elif (self.device_type == "833"):
            self._modes = {"off": "0", "performance": "1", "electric": "2", "heat_pump": "3", "eco": "7"}
        else:
            self._modes = description.operation_list
        self._attr_operation_list = list(self._modes.keys())

        #self.entity_picture = "https://images.cdn.polaris-iot.com/a/8c/aad08-4d13-489c-9b0f-028486297ac1/60.webp"
        self._attr_has_entity_name = True
        self._attr_available = False

#    _attr_precision: float
#    _attr_state: None = None



    async def async_added_to_hass(self):
        @callback
        def message_received_temp(message):
            self._attr_current_temperature = float(message.payload)
            self.async_write_ha_state()
        @callback
        def message_received_mode(message):
            self._attr_current_operation = list(self._modes.keys())[list(self._modes.values()).index(message.payload)]
            self.async_write_ha_state()
        @callback
        def message_received_targtemp(message):
            if float(message.payload) < self._attr_min_temp:
                self._attr_target_temperature = self._attr_min_temp
            else:
                self._attr_target_temperature = float(message.payload)
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentTemperature,
            message_received_temp,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentMode,
            message_received_mode,
            1,
        )
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicTargetTemperature,
            message_received_targtemp,
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


    def async_turn_on(self, **kwargs):
        self._attr_is_on = self.payload_on
        self.publishToMQTT()

    def async_turn_off(self, **kwargs):
        self._attr_is_on = self.payload_off
        self.publishToMQTT()

    def publishToMQTT(self):
        topic = f"{self.entity_description.mqttTopicCommandMode}"
        mqtt.publish(self.hass, topic, str(self._attr_is_on))

    def set_operation_mode(self, operation_mode):
        topic = f"{self.entity_description.mqttTopicCommandTemperature}"
        mqtt.publish(self.hass, topic, int(self._attr_target_temperature))
        topic = f"{self.entity_description.mqttTopicCommandMode}"
        self._attr_current_operation = operation_mode
        mqtt.publish(self.hass, topic, int(self._modes[operation_mode]))
        self.schedule_update_ha_state()

    def set_temperature(self, **kwargs):
        self._attr_target_temperature = kwargs.get(ATTR_TEMPERATURE)
        topic = f"{self.entity_description.mqttTopicCommandTemperature}"
        mqtt.publish(self.hass, topic, int(self._attr_target_temperature))
        self.schedule_update_ha_state()

    @property
    def state(self) -> str | None:
        return self.current_operation
        
    @property
    def operation_list(self) -> list[str] | None:
        return self._attr_operation_list

    @property
    def current_operation(self) -> str | None:
        return self._attr_current_operation
        
    @property
    def supported_features(self) -> WaterHeaterEntityFeature:
        return self._attr_supported_features

    @property
    def min_temp(self) -> float:
        return self._attr_min_temp

    @property
    def max_temp(self) -> float:
        return self._attr_max_temp
