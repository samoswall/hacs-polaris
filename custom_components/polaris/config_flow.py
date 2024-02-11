"""Config flow for Polaris."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import DOMAIN, CONF_TOPIC_PREFIX

_LOGGER = logging.getLogger(__name__)


class PolarisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DEVICE_ID, default="+"): str,
                        vol.Required(CONF_TOPIC_PREFIX, default="polaris"): str,
                    }
                ),
                errors=errors,
            )

        device_id = user_input[CONF_DEVICE_ID]
        topic_prefix = user_input[CONF_TOPIC_PREFIX]

        await self.async_set_unique_id("{}_{}".format(DOMAIN, device_id))
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="Polaris IQ Home",
            data={
                CONF_DEVICE_ID: device_id,
                CONF_TOPIC_PREFIX: topic_prefix,
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PolarisOptionsFlowHandler(config_entry)


class PolarisOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Polaris."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="qwerty", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE_ID,
                    default=self.config_entry.options.get(CONF_DEVICE_ID, "+"),
                ): str,
                vol.Required(
                    CONF_TOPIC_PREFIX,
                    default=self.config_entry.options.get(CONF_TOPIC_PREFIX, "polaris"),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
