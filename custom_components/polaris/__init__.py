"""The Polaris IQ Home component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

# Import global values.
from .const import PLATFORMS

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Trigger the creation of sensors."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Активация всех деактивированных устройств при загрузке
    await async_enable_disabled_devices(hass, entry)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload all sensor entities and services if integration is removed via UI.
    No restart of home assistant is required.
    """
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    return unload_ok
    
    
async def async_enable_disabled_devices(hass: HomeAssistant, entry: ConfigEntry):
    """Enable all disabled devices associated with this integration."""
    device_registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)

    for device in devices:
        if device.disabled:
            _LOGGER.debug("Enabling disabled device: %s (%s)", device.name, device.id)
            device_registry.async_update_device(device.id, disabled_by = None) # Убираем disabled
