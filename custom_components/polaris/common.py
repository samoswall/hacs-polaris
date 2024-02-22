"""The openwbmqtt component for controlling the openWB wallbox via home assistant / MQTT."""
from homeassistant.helpers.entity import DeviceInfo

from .const import POLARIS_DEVICE


class OpenWBBaseEntity:
    """Openwallbox entity base class."""

    def __init__(
        self,
        device_friendly_name: str,
        mqtt_root: str,
        device_type: str,
        device_id: str
    ) -> None:
        """Init device info class."""
        self.device_friendly_name = device_friendly_name
        self.mqtt_root = mqtt_root
        self.device_type=device_type
        self.device_id=device_id
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            DeviceInfo(
            connections={("ids", self.device_id)},
            manufacturer="Polaris IQ Home",
            model=POLARIS_DEVICE[int(self.device_type)]["model"],
            name=POLARIS_DEVICE[int(self.device_type)]["class"]+" "+ POLARIS_DEVICE[int(self.device_type)]["model"],
        )
        #self._attr_native_value = None
        )
