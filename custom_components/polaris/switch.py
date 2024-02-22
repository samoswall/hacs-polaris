"""Support for Polaris switchs."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.switch import DOMAIN, SwitchEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import (DOMAIN, CONF_TOPIC_PREFIX, MQTT_DEVICE_FOUND, POLARIS_DEVICE, SWITCHES_PER_LP, openwbSwitchEntityDescription)
from homeassistant.const import (
    CONF_DEVICE_ID,
    ATTR_DEVICE_ID,
    SIGNAL_STRENGTH_DECIBELS,
    EntityCategory
)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import OpenWBBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Return switch entities."""
#    integrationUniqueID = config_entry.unique_id   # polaris_+
#    mqttRoot = config_entry.data[CONF_TOPIC_PREFIX]    # polaris
#    nChargePoints = config_entry.data["device_id"]     # +

    device_mac = hass.data[DOMAIN][config_entry.entry_id][CONF_DEVICE_ID]    # +
    topic_prefix = (
        hass.data[DOMAIN][config_entry.entry_id][CONF_TOPIC_PREFIX] or "polaris"   # polaris
    )
    device_found = hass.data[DOMAIN][config_entry.entry_id][MQTT_DEVICE_FOUND]
    #device_found = {'61': ['2ad246f6f25e1877e7d09f6cbc137ad3'], '70': ['1dc47cb18aadbb06f073def3e31c97c3']}
    #device_found = {'70': ['1dc47cb18aadbb06f073def3e31c97c3']}

    _LOGGER.debug("Start Switch: %s", device_found)

    #if device_found=={}:
    #    _LOGGER.debug("Switch Return: %s", device_found)
    #    return False



    _LOGGER.debug("Switch device_mac: %s", device_mac)    # +
    _LOGGER.debug("Switch topic_prefix: %s", topic_prefix)    # polaris
    _LOGGER.debug("Switch device_found: %s", device_found)

    switchList = []

    for device_type in device_found:
        _LOGGER.debug("Switch device_type: %s", device_type)
        localSwitchesPerLP = copy.deepcopy(SWITCHES_PER_LP)
        for device_id in device_found[device_type]:
            _LOGGER.debug("Switch device_id: %s", device_id)
            for description in localSwitchesPerLP:
                description.mqttTopicCommand = f"{topic_prefix}/{device_type}/{device_id}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{topic_prefix}/{device_type}/{device_id}/{description.mqttTopicCurrentValue}"
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=topic_prefix,
                        device_type=device_type,
                        device_id=device_id
                    )
                )

    async_add_entities(switchList, update_before_add=True)



class PolarisSwitch(OpenWBBaseEntity, SwitchEntity):
    """Entity representing the inverter operation mode."""

    entity_description: openwbSwitchEntityDescription

    def __init__(
        self,
        device_friendly_name: str,
        description: openwbSwitchEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None
    ) -> None:
        """Initialize the sensor and the openWB device."""
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id
        )
        # Initialize the inverter operation mode setting entity
        self.entity_description = description

        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{device_id}-{description.name}"
        self._attr_name = f"{POLARIS_DEVICE[int(device_type)]['class']} {POLARIS_DEVICE[int(device_type)]['model']} {description.name}"

    async def async_added_to_hass(self):
        """Subscribe to MQTT events."""

        @callback
        def message_received(message):
            if int(message.payload) == 1:
                self._attr_is_on = True
            elif int(message.payload) == 0:
                self._attr_is_on = False
            else:
                self._attr_is_on = None

            self.async_write_ha_state()

        # Subscribe to MQTT topic and connect callack message
        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )

    def turn_on(self, **kwargs):
        """Turn the switch on.

        After turn_on --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self._attr_is_on = True
        self.publishToMQTT()
        # self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off.

        After turn_off --> the result is published to MQTT.
        But the HA sensor shall only change when the MQTT message on the /get/ topic is received.
        Only then, openWB has changed the setting as well.
        """
        self._attr_is_on = False
        self.publishToMQTT()
        # self.schedule_update_ha_state()

    def publishToMQTT(self):
        """Publish data to MQTT."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        self.hass.components.mqtt.publish(self.hass, topic, str(self._attr_is_on))
