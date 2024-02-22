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
from .const import DOMAIN, CONF_TOPIC_PREFIX, POLARIS_DEVICE, MQTT_DEVICE_FOUND
from homeassistant.const import (
    CONF_DEVICE_ID,
    ATTR_DEVICE_ID,
    SIGNAL_STRENGTH_DECIBELS,
    EntityCategory,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)


STATE_SENSORS_RSSI = [
    {
        "name": "RSSI",
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
        "name": "temperature",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit_of_measurement": "°C",
        "state_class": SensorStateClass.MEASUREMENT,
        "entity_category": None,
        "icon": "mdi:thermometer",
        "func": lambda js: js["temperature"],
    }
]
STATE_SENSORS_HUMIDITY = [
    {
        "name": "humidity",
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit_of_measurement": "%",
        "state_class": SensorStateClass.MEASUREMENT,
        "entity_category": None,
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
    device_found = {}
    deviceUpdateGroups = {}

    @callback
    async def mqtt_message_received(message: ReceiveMessage):
        """Handle received MQTT message."""
        topic = message.topic
        device_type = topic.split("/")[1]
        device_id = topic.split("/")[2]
        if device_mac == "+" or device_id == device_mac:
            updateGroups = await async_get_device_groups(
                hass,
                config_entry,
                device_found,
                deviceUpdateGroups,
                async_add_entities,
                device_id,
                device_type,
            )
            for updateGroup in updateGroups:
                updateGroup.process_update(message)

    data_topic = f"{topic_prefix}/#"

    await mqtt.async_subscribe(hass, data_topic, mqtt_message_received, 1)


async def async_get_device_groups(
    hass,
    config_entry,
    device_found,
    deviceUpdateGroups,
    async_add_entities,
    device_id,
    device_type,
):
    # add to update groups if not already there
    if device_id not in deviceUpdateGroups:
        _LOGGER.debug("New device found id: %s", device_id)
        _LOGGER.debug("New device found type: %s", device_type)
        _LOGGER.debug("New device old data: %s", hass.data[DOMAIN])
        _LOGGER.debug("old data: %s", config_entry.data)
        # Add New device to config integrations
        if device_type in device_found.keys():
            if device_id not in device_found[device_type]:
                device_found[device_type].append(device_id)
        else:
            device_found[device_type] = [device_id]
        hass.data[DOMAIN][config_entry.entry_id][MQTT_DEVICE_FOUND] = device_found
        _LOGGER.debug("New device new data: %s", hass.data[DOMAIN])

        new_data = config_entry.data.copy()


        new_data[MQTT_DEVICE_FOUND] = device_found
        _LOGGER.debug("new data: %s", new_data)
        hass.config_entries.async_update_entry(config_entry, data=new_data)

        # hass.data[DOMAIN][config_entry.entry_id].async_create_entry(
        #    title="",
        #    data={MQTT_DEVICE_FOUND: device_found} )

        # hass.data[DOMAIN][config_entry.entry_id].update()
        # hass.config_entries.async_update_entry(config_entry.entry_id)
        # hass.async_create_task(hass.config_entries.async_update_entry(config_entry.entry_id))
        # hass.config_entries.async_unload_platforms(config_entry, "switch")
        # hass.async_add_job

        hass.async_create_task(hass.config_entries.async_reload(config_entry))
        # {'61': ['2ad246f6f25e1877e7d09f6cbc137ad3'], '70': ['1dc47cb18aadbb06f073def3e31c97c3']}

        match device_type:
            case (
                "2"
                | "6"
                | "8"
                | "29"
                | "35"
                | "36"
                | "37"
                | "38"
                | "51"
                | "52"
                | "53"
                | "54"
                | "56"
                | "57"
                | "58"
                | "59"
                | "60"
                | "61"
                | "62"
                | "63"
                | "67"
                | "82"
                | "83"
                | "84"
                | "85"
                | "86"
                | "97"
                | "98"
                | "105"
                | "106"
                | "116"
                | "117"
                | "120"
            ):
                groups = [
                    PolarisSensorUpdateGroup(
                        device_id, device_type, "diag/rssi", STATE_SENSORS_RSSI
                    ),
                    PolarisSensorUpdateGroup(
                        device_id,
                        device_type,
                        "sensor/temperature",
                        STATE_SENSORS_TEMPERATURE,
                    ),
                ]
            case (
                "4"
                | "15"
                | "17"
                | "18"
                | "25"
                | "44"
                | "70"
                | "71"
                | "72"
                | "73"
                | "74"
                | "75"
                | "87"
                | "99"
                | "91"
            ):
                groups = [
                    PolarisSensorUpdateGroup(
                        device_id, device_type, "diag/rssi", STATE_SENSORS_RSSI
                    ),
                    PolarisSensorUpdateGroup(
                        device_id,
                        device_type,
                        "sensor/temperature",
                        STATE_SENSORS_TEMPERATURE,
                    ),
                    PolarisSensorUpdateGroup(
                        device_id,
                        device_type,
                        "sensor/humidity",
                        STATE_SENSORS_HUMIDITY,
                    ),
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

    def __init__(
        self, device_id: str, device_type: str, topic_regex: str, meters: Iterable
    ) -> None:
        """Initialize the sensor collection."""
        self._topic_regex = re.compile(topic_regex)
        self._sensors = [
            PolarisSensor(device_id=device_id, device_type=device_type, **meter)
            for meter in meters
        ]

    def process_update(self, message: ReceiveMessage) -> None:
        """Process an update from the MQTT broker."""
        topic = message.topic
        payload = message.payload
        if self._topic_regex.search(topic):
            parsed_data = json.dumps(
                {topic.split("/")[topic.count("/")]: json.loads(payload)}
            )
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
        self._attr_name = f"{POLARIS_DEVICE[int(device_type)]['class']} {POLARIS_DEVICE[int(device_type)]['model']} {name}"
        self._attr_unique_id = slugify(f"{device_id}_{name}")
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
            name=POLARIS_DEVICE[int(device_type)]["class"]
            + " "
            + POLARIS_DEVICE[int(device_type)]["model"],
        )
        self._attr_native_value = None

    def process_update(self, mqtt_data) -> None:
        """Update the state of the sensor."""
        _LOGGER.debug("mqtt_data: %s", mqtt_data)
        mqtt_data = json.loads(mqtt_data)
        new_value = self._func(mqtt_data)
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
