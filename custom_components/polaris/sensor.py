"""Support for Polaris sensors."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import DOMAIN, CONF_TOPIC_PREFIX, POLARIS_DEVICE
from homeassistant.const import (
    CONF_DEVICE_ID,
    ATTR_DEVICE_ID,
    SIGNAL_STRENGTH_DECIBELS,
    EntityCategory
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)
parsed_data = {}


STATE_SENSORS_RSSI = [
    {
        "name": "Polaris RSSI",
        "device_class": SensorDeviceClass.SIGNAL_STRENGTH,
        "unit_of_measurement": SIGNAL_STRENGTH_DECIBELS,
        "state_class": SensorStateClass.MEASUREMENT,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:wifi-strength-outline",
        "func": lambda js: js["rssi"],
    }
]
STATE_SENSORS_TEMPERATURE = [
    {
        "name": "Polaris temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit_of_measurement": "°C",
        "state_class": SensorStateClass.MEASUREMENT,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:thermometer",
        "func": lambda js: js["temperature"],
    }
]
STATE_SENSORS_HUMIDITY = [
    {
        "name": "Polaris humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit_of_measurement": "%",
        "state_class": SensorStateClass.MEASUREMENT,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "icon": "mdi:water-percent",
        "func": lambda js: js["humidity"],
    }
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Polaris sensors."""

    device_mac = hass.data[DOMAIN][config_entry.entry_id][CONF_DEVICE_ID]
    topic_prefix = (
        hass.data[DOMAIN][config_entry.entry_id][CONF_TOPIC_PREFIX] or "polaris"
    )

    deviceUpdateGroups = {}

    @callback
    async def mqtt_message_received(message: ReceiveMessage):
        """Handle received MQTT message."""
        topic = message.topic
        payload = message.payload
        cur_sens = message.subscribed_topic  # topic.split("/")[4]
        # _LOGGER.debug("cur_sens: %s", cur_sens)
        device_type = topic.split("/")[1]


        device_id = topic.split("/")[2]
        # _LOGGER.debug("message: %s", message)
        #_LOGGER.debug("Topic: %s", topic)
        # _LOGGER.debug("device_mac: %s", device_mac)
        # _LOGGER.debug("topic_prefix: %s", topic_prefix)
        #_LOGGER.debug("device_id: %s", device_id)
        # _LOGGER.debug("device_type: %s", device_type)
        # _LOGGER.debug("device_mac: %s", device_mac)
        if device_mac == "+" or device_id == device_mac:
            updateGroups = await async_get_device_groups(
                deviceUpdateGroups, async_add_entities, device_id, device_type
            )
            # _LOGGER.debug("Received message: %s", topic)
            # _LOGGER.debug("  Payload: %s", payload)
            for updateGroup in updateGroups:
                updateGroup.process_update(message)

    data_topic = f"{topic_prefix}/#"

    await mqtt.async_subscribe(hass, data_topic, mqtt_message_received, 1)


async def async_get_device_groups(
    deviceUpdateGroups, async_add_entities, device_id, device_type
):
    # add to update groups if not already there
    if device_id not in deviceUpdateGroups:
        _LOGGER.debug("New device found id: %s", device_id)
        _LOGGER.debug("New device found type: %s", device_type)
        match device_type:
            case "2"|"6"|"8"|"29"|"35"|"36"|"37"|"38"|"51"|"52"|"53"|"54"|"56"|"57"|"58"|"59"|"60"|"61"|"62"|"63"|"67"|"82"|"83"|"84"|"85"|"86"|"97"|"98"|"105"|"106"|"116"|"117"|"120":
                groups = [
                    PolarisSensorUpdateGroup(device_id, device_type, "diag/rssi", STATE_SENSORS_RSSI),
                    PolarisSensorUpdateGroup(device_id, device_type, "sensor/temperature", STATE_SENSORS_TEMPERATURE)
                ]
            case "4"|"15"|"17"|"18"|"25"|"44"|"70"|"71"|"72"|"73"|"74"|"75"|"87"|"99"|"91":
                groups = [
                    PolarisSensorUpdateGroup(device_id, device_type, "diag/rssi", STATE_SENSORS_RSSI),
                    PolarisSensorUpdateGroup(device_id, device_type, "sensor/temperature", STATE_SENSORS_TEMPERATURE),
                    PolarisSensorUpdateGroup(device_id, device_type, "sensor/humidity", STATE_SENSORS_HUMIDITY)
                ]
        async_add_entities(
            [
                sensorEntity
                for updateGroup in groups
                for sensorEntity in updateGroup.all_sensors
            ],
            # True
        )
        deviceUpdateGroups[device_id] = groups

    return deviceUpdateGroups[device_id]


class PolarisSensorUpdateGroup:
    """Representation of Polaris Sensors that all get updated together."""

    def __init__(self, device_id: str, device_type: str, topic_regex: str, meters: Iterable) -> None:
        """Initialize the sensor collection."""
        self._topic_regex = re.compile(topic_regex)
        _LOGGER.debug("topic_regex %s", self._topic_regex)
        self._sensors = [
            PolarisSensor(device_id=device_id, device_type=device_type, **meter) for meter in meters
        ]

    def process_update(self, message: ReceiveMessage) -> None:
        """Process an update from the MQTT broker."""
        topic = message.topic
        payload = message.payload
        if self._topic_regex.search(topic):
            down_topic = topic.split("/")[topic.count("/")]
            #if down_topic == "rssi" or down_topic == "humidity" or down_topic == "temperature":
            # _LOGGER.debug("Matched on %s", self._topic_regex.pattern)
            # _LOGGER.debug("topic non parsed %s", topic)
            # _LOGGER.debug("Payload non parsed %s", payload)
        #    arr_parsed_data = {}
        #    match topic.split("/")[topic.count("/")]:
        #        case "rssi":
        #            arr_parsed_data = {"rssi": str(json.loads(payload)), "temperature": 0, "humidity": 0}
        #        case "temperature":
        #            arr_parsed_data = {"rssi": 0, "temperature": str(json.loads(payload)), "humidity": 0}
        #        case "humidity":
        #            arr_parsed_data = {"rssi": 0, "temperature": 0, "humidity": str(json.loads(payload))}
            parsed_data = json.dumps({topic.split("/")[topic.count("/")]: json.loads(payload)})    # , "device_type": topic.split("/")[1]
            #_LOGGER.debug("Update group parsed_data: %s", parsed_data)
            for sensor in self._sensors:
                sensor.process_update(parsed_data)

    @property
    def all_sensors(self) -> Iterable[PolarisSensor]:
        """Return all meters."""
        return self._sensors


class PolarisSensor(SensorEntity):
    """Representation of a room sensor that is updated via MQTT."""

    def __init__(
        self,
        device_id,
        device_type,
        name,
        icon,
        device_class,
        unit_of_measurement,
        state_class,
        func,
        entity_category=EntityCategory.CONFIG,
        ignore_zero_values=False,
    ) -> None:
        """Initialize the sensor."""
        self._device_id = device_id
        self._ignore_zero_values = ignore_zero_values
        self._attr_name = name
        self._attr_unique_id = slugify(device_id + "_" + name)
        self._attr_icon = icon
        if device_class:
            self._attr_device_class = device_class
        if unit_of_measurement:
            self._attr_native_unit_of_measurement = unit_of_measurement
        if state_class:
            self._attr_state_class = state_class
        self._attr_entity_category = entity_category
        self._attr_should_poll = False

        self._func = func
        self._attr_device_info = DeviceInfo(
            connections={("ids", device_id)},
            manufacturer="Polaris IQ Home",
            model=POLARIS_DEVICE[int(device_type)]["model"],
            name=POLARIS_DEVICE[int(device_type)]["class"]+" "+POLARIS_DEVICE[int(device_type)]["model"],
        )
        self._attr_native_value = None

    def process_update(self, mqtt_data) -> None:
        """Update the state of the sensor."""
        _LOGGER.debug("mqtt_data: %s", mqtt_data)
        mqtt_data = json.loads(mqtt_data)
        new_value = self._func(mqtt_data)
        _LOGGER.debug("new_value: %s", new_value)
        if self._ignore_zero_values and new_value == 0:
            _LOGGER.debug(
                "Ignored new value of %s on %s.", new_value, self._attr_unique_id
            )
            return
        self._attr_native_value = new_value
        if (
            self.hass is not None
        ):  # this is a hack to get around the fact that the entity is not yet initialized at first
            self.async_schedule_update_ha_state()

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {ATTR_DEVICE_ID: self._device_id}
