"""The Polaris IQ Home component."""

import logging

from homeassistant.helpers.device_registry import DeviceInfo
from .const import DOMAIN, MANUFACTURER, POLARIS_DEVICE

#_LOGGER = logging.getLogger(__name__)
#_LOGGER.setLevel(logging.DEBUG)

class PolarisBaseEntity:

    deviceID: str | None = None

    def __init__(
        self,
        device_friendly_name: str,
        mqtt_root: str,
        device_type: str,
        device_id: str
    ) -> None:
        self.device_friendly_name = device_friendly_name
        self.mqtt_root = mqtt_root
        self.device_type=device_type
        self.device_id=device_id


    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            name=POLARIS_DEVICE[int(self.device_type)]["class"]+" "+ POLARIS_DEVICE[int(self.device_type)]["model"],
            identifiers={(DOMAIN, self.device_id, self.mqtt_root)},
            manufacturer=MANUFACTURER,
            model=POLARIS_DEVICE[int(self.device_type)]["class"]+" - "+ POLARIS_DEVICE[int(self.device_type)]["model"],
        )
