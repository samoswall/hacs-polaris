"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

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
from .common import PolarisBaseEntity

# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    BINARYSENSOR_KETTLE,
    PolarisBinarySensorEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
)

#_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:

    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    binarysensorList = []
    
    if (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create kettle with base
            BINARYSENSOR_KETTLE_LC = copy.deepcopy(BINARYSENSOR_KETTLE)
            for description in BINARYSENSOR_KETTLE_LC:
                description.mqttTopicBaseStatus = f"{mqtt_root}/{device_id}/{description.mqttTopicBaseStatus}"
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

    async def async_added_to_hass(self):
        @callback
        def message_received_base(message):
            if str(message.payload).lower() in ("1", "true"):
                self._attr_is_on = True
            elif str(message.payload).lower() in ("0", "false"):
                self._attr_is_on = False
#            else:
#                self._attr_is_on = None
#                self._attr_state = None
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicBaseStatus,
            message_received_base,
            1,
        )

#    def is_on(self) -> bool | None:
#        """Return true if the binary sensor is on."""
#        return self._attr_is_on

#    def state(self) -> Literal["on", "off"] | None:
#        """Return the state of the binary sensor."""
#        if (is_on := self._attr_is_on) is None:
#            return None
#        return STATE_ON if is_on else STATE_OFF