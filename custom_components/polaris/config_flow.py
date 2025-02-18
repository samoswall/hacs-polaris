"""The Polaris IQ Home component."""
from __future__ import annotations


import logging
import time
import voluptuous as vol
from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import ConfigFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.components import mqtt

import homeassistant.helpers.config_validation as cv

from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import DEVICEID, DEVICETYPE, DOMAIN, MQTT_ROOT_TOPIC, MQTT_ROOT_TOPIC_DEFAULT, POLARIS_DEVICE
from homeassistant.helpers.service_info.mqtt import MqttServiceInfo

#_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)

class PolarisConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1
    
    def __init__(self) -> None:
        """Initialize flow."""
        self._serial_number = None
        self._topic_prefix = "polaris"
#        self._device_found = {"*":"0"}
        self._device_found = {}

    async def _get_devtypes_from_mqtt(self):
        await mqtt.async_subscribe(self.hass, "polaris/+/state/devtype", self._mqtt_message)

    @callback
    async def _mqtt_message(self, message: ReceiveMessage):
        topic = message.topic
        device_type = message.payload
        device_id = topic.split("/")[1]
        if device_id not in self._device_found:
            self._device_found[device_id] = device_type
        

    async def async_step_user(self, user_input=None):
        await self._get_devtypes_from_mqtt()
        await self.hass.async_add_executor_job(time.sleep, 2)

        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(MQTT_ROOT_TOPIC, default=MQTT_ROOT_TOPIC_DEFAULT): cv.string,
                        vol.Required(DEVICEID): SelectSelector(
                            SelectSelectorConfig(
                                options=[
                                    SelectOptionDict(
                                        value=dev_mac,
                                        label=f"{POLARIS_DEVICE[int(dev_type)]["model"]} (mac: {dev_mac})",
                                    )
                                    for dev_mac, dev_type in self._device_found.items()
                                ],
                                mode=SelectSelectorMode.DROPDOWN,
                                translation_key="config_selector_devicetype",
                            )
                        ),
                    }
                ),
                errors=errors,
            )
            
        user_input[DEVICETYPE] = self._device_found[user_input[DEVICEID]]
        
        if user_input[DEVICETYPE] == "0":
            for dev_mac, dev_type in self._device_found.items():
                if int(dev_type) > 0:
                    title = f"{POLARIS_DEVICE[int(dev_type)]['class']}-{POLARIS_DEVICE[int(dev_type)]['model']}-{dev_mac}"
                    user_input[DEVICETYPE] = dev_type
                    await self.async_set_unique_id(title)
                    # Create entities
                    return self.async_create_entry(
                        title=title,
                        data=user_input,
                    )
        else:
            title = f"{POLARIS_DEVICE[int(user_input[DEVICETYPE])]['class']}-{POLARIS_DEVICE[int(user_input[DEVICETYPE])]['model']}-{user_input[DEVICEID]}"
            await self.async_set_unique_id(title)
            self._abort_if_unique_id_configured(error="already_configured")
            # Create entities
            return self.async_create_entry(
                title=title,
                data=user_input,
            )
