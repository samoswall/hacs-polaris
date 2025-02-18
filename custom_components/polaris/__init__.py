"""The Polaris IQ Home component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# Import global values.
from .const import PLATFORMS

#_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Trigger the creation of sensors."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload all sensor entities and services if integration is removed via UI.
    No restart of home assistant is required.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
