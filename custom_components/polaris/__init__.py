"""The Polaris component."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_DEVICE_ID,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_TOPIC_PREFIX

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Polaris integration."""

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.debug("Setting up Polaris integration")

    if entry.entry_id not in hass.data[DOMAIN]:
        hass.data[DOMAIN][entry.entry_id] = {}

    hass.data[DOMAIN][entry.entry_id][CONF_DEVICE_ID] = entry.data[CONF_DEVICE_ID].strip().upper().replace(":", "").replace(" ", "")
    hass.data[DOMAIN][entry.entry_id][CONF_TOPIC_PREFIX] = entry.data.get(CONF_TOPIC_PREFIX, "polaris").strip().replace("#", "").replace(" ", "")

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component))

    _LOGGER.debug("Finished setting up Polaris integration")
    return True
