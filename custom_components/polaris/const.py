"""The Polaris IQ Home component."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import datetime
import json
from zoneinfo import ZoneInfo

import voluptuous as vol

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberDeviceClass, NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntityDescription,
)
from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityEntityDescription
from homeassistant.components.humidifier import HumidifierEntity, HumidifierEntityDescription, HumidifierDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfMass,
    SIGNAL_STRENGTH_DECIBELS,
    Platform,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

PLATFORMS = [
    Platform.SELECT,
    Platform.SENSOR,
    Platform.HUMIDIFIER,
    Platform.WATER_HEATER,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.LIGHT,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.TIME
]

# Global values
DOMAIN = "polaris"
MQTT_ROOT_TOPIC = "MQTT_ROOT_TOPIC"
MQTT_ROOT_TOPIC_DEFAULT = "polaris"
DEVICETYPE = "DEVICETYPE"
DEVICEID = "DEVICEID"
MANUFACTURER = "Polaris IQ Home"

POLARIS_DEVICE = {
    0: {"model": "All devices", "class": "All"},
    34: {"model": "PHB-1551WIFI", "class": "Blender"},
    93: {"model": "PHB-1350WIFI", "class": "Blender"},
    11: {"model": "PWH-IDF06", "class": "Boiler"},
    30: {"model": "SIGMA-WI-FI", "class": "Boiler"},
    31: {"model": "ENIGMA-WI-FI", "class": "Boiler"},
    7: {"model": "PVCR-3200", "class": "Cleaner"},
    12: {"model": "PVCR-3300", "class": "Cleaner"},
    19: {"model": "PVCR-0833", "class": "Cleaner"},
    21: {"model": "PVCR-0735", "class": "Cleaner"},
    22: {"model": "PVCR-1050", "class": "Cleaner"},
    23: {"model": "PVCR-1028", "class": "Cleaner"},
    24: {"model": "PVCR-1229", "class": "Cleaner"},
    43: {"model": "PVCR-0833", "class": "Cleaner"},
    66: {"model": "PVCR-3900", "class": "Cleaner"},
    68: {"model": "PVCR-3100", "class": "Cleaner"},
    76: {"model": "PVCR-3200", "class": "Cleaner"},
    81: {"model": "PVCR-3400", "class": "Cleaner"},
    88: {"model": "PVCR-3800", "class": "Cleaner"},
    90: {"model": "PVCS-2090", "class": "Cleaner"},
    100: {"model": "PVCR-Wave-15", "class": "Cleaner"},
    101: {"model": "PVCR-0726-Aqua", "class": "Cleaner"},
    102: {"model": "PVCR-1226-Aqua", "class": "Cleaner"},
    104: {"model": "PVCR-0905", "class": "Cleaner"},
    107: {"model": "PVCR-0926", "class": "Cleaner"},
    108: {"model": "PVCR-0726-GYRO", "class": "Cleaner"},
    109: {"model": "PVCR-1226-GYRO", "class": "Cleaner"},
    110: {"model": "PVCR-4105", "class": "Cleaner"},
    111: {"model": "PVCS-1150", "class": "Cleaner"},
    112: {"model": "PVCR-3700", "class": "Cleaner"},
    113: {"model": "PVCR-4000", "class": "Cleaner"},
    115: {"model": "PVCR-3200", "class": "Cleaner"},
    119: {"model": "PVCR-5001", "class": "Cleaner"},
    123: {"model": "PVCR-6001", "class": "Cleaner"},
    124: {"model": "PVCRDC-5002", "class": "Cleaner"},
    125: {"model": "PVCRDC-6002", "class": "Cleaner"},
    45: {"model": "PCM-1540WIFI", "class": "Coffeemaker"},
    103: {"model": "PACM-2080AC", "class": "Coffeemaker"},
    1: {"model": "EVO-0225", "class": "Cooker"},
    9: {"model": "PMC-0526WIFI", "class": "Cooker"},
    10: {"model": "PMC-0521WIFI", "class": "Cooker"},
    32: {"model": "PMC-0524WIFI", "class": "Cooker"},
    33: {"model": "PMC-0530WIFI", "class": "Cooker"},
    39: {"model": "PMC-0528WIFI", "class": "Cooker"},
    40: {"model": "PMC-0526WIFI", "class": "Cooker"},
    41: {"model": "PMC-0521WIFI", "class": "Cooker"},
    47: {"model": "PMC-0530WIFI", "class": "Cooker"},
    48: {"model": "PMC-0528WIFI", "class": "Cooker"},
    55: {"model": "PMC-0524WIFI", "class": "Cooker"},
    77: {"model": "PMC-5040WIFI", "class": "Cooker"},
    78: {"model": "PMC-5050WIFI", "class": "Cooker"},
    79: {"model": "PMC-5017WIFI", "class": "Cooker"},
    80: {"model": "PMC-5020WIFI", "class": "Cooker"},
    89: {"model": "PMC-5055WIFI", "class": "Cooker"},
    95: {"model": "PMC-00000", "class": "Cooker"},
    114: {"model": "PMC-0526WIFI-G", "class": "Cooker"},
    3: {"model": "PWS1886/1892", "class": "Floor-scales"},
    5: {"model": "PWS1830/1883", "class": "Floor-scales"},
    96: {"model": "PGP-4001", "class": "Grill"},
    122: {"model": "PGP-4001-DEV", "class": "Grill"},
    16: {"model": "PHV-1401", "class": "Heater"},
    46: {"model": "PCH-0320WIFI", "class": "Heater"},
    49: {"model": "PMH-21XX", "class": "Heater"},
    64: {"model": "PMH-21XX", "class": "Heater"},
    65: {"model": "PCH-0320WIFI", "class": "Heater"},
    4: {"model": "PUH-9105", "class": "Humidifier"},
    15: {"model": "PUH-7406", "class": "Humidifier"},
    17: {"model": "PUH-9105", "class": "Humidifier"},
    18: {"model": "PUH-9105", "class": "Humidifier"},
    25: {"model": "PUH-6090", "class": "Humidifier"},
    44: {"model": "PUH-9105", "class": "Humidifier"},
    70: {"model": "PUH-9105", "class": "Humidifier"},
    71: {"model": "PUH-1010", "class": "Humidifier"},
    72: {"model": "PUH-2300", "class": "Humidifier"},
    73: {"model": "PUH-3030", "class": "Humidifier"},
    74: {"model": "PUH-9009", "class": "Humidifier"},
    75: {"model": "PUH-4040", "class": "Humidifier"},
    87: {"model": "PUH-8080", "class": "Humidifier"},
    99: {"model": "PUH-4040", "class": "Humidifier"},
    91: {"model": "PIR-2624AK-3m", "class": "Iron"},
    2: {"model": "PWK-1775CGLD", "class": "Kettle"},
    6: {"model": "PWK-1725CGLD", "class": "Kettle"},
    8: {"model": "PWK-1755CAD", "class": "Kettle"},
    29: {"model": "PWK-1712CGLD", "class": "Kettle"},
    35: {"model": "PWK-1775CGLD", "class": "Kettle"},
    36: {"model": "PWK-1725CGLD", "class": "Kettle"},
    37: {"model": "PWK-1755CAD", "class": "Kettle"},
    38: {"model": "PWK-1712CGLD", "class": "Kettle"},
    51: {"model": "PWK-1775CGLD", "class": "Kettle"},
    52: {"model": "PWK-1725CGLD", "class": "Kettle"},
    53: {"model": "PWK-1755CAD", "class": "Kettle"},
    54: {"model": "PWK-1712CGLD", "class": "Kettle"},
    56: {"model": "PWK-1775CGLD", "class": "Kettle"},
    57: {"model": "PWK-1725CGLD", "class": "Kettle"},
    58: {"model": "PWK-1755CAD", "class": "Kettle"},
    59: {"model": "PWK-1712CGLD", "class": "Kettle"},
    60: {"model": "PWK-1775CGLD", "class": "Kettle"},
    61: {"model": "PWK-1725CGLD", "class": "Kettle"},
    62: {"model": "PWK-1755CAD", "class": "Kettle"},
    63: {"model": "PWK-1712CGLD", "class": "Kettle"},
    67: {"model": "PWK-1720CGLD", "class": "Kettle"},
    82: {"model": "PWK-1725CGLD", "class": "Kettle"},
    83: {"model": "PWK-1712CGLD-RGB", "class": "Kettle"},
    84: {"model": "PWK-1720CGLD-RGB", "class": "Kettle"},
    85: {"model": "PWK-1775CGLD-SMART", "class": "Kettle"},
    86: {"model": "PWK-1725CGLD", "class": "Kettle"},
    97: {"model": "PWK-1712CGLD", "class": "Kettle"},
    98: {"model": "PWK-1775CGLD-SCALES", "class": "Kettle"},
    105: {"model": "PWK-1725CGLD", "class": "Kettle"},
    106: {"model": "PWK-1725CGLD-SCALES", "class": "Kettle"},
    116: {"model": "Smart-Lid", "class": "Lid"},
    117: {"model": "PWK-1712CGLD", "class": "Kettle"},
    120: {"model": "HAIR-DRYER", "class": "Dryer"},
    92: {"model": "PGS-1450CWIFI", "class": "Steamer"},
    94: {"model": "PSS-7070KWIFI", "class": "Steamer"},
    26: {"model": "PTB-RMST201811", "class": "Toothbrush"},
    27: {"model": "PTB-RMST201908", "class": "Toothbrush"},
    28: {"model": "PTB-RMST201906", "class": "Toothbrush"},
    50: {"model": "PETB-0202TC", "class": "Toothbrush"},
}

POLARIS_KETTLE_TYPE = ["2","6","8","29","35","36","37","38","51","52","53","54","56","57","58","59","60","61","62","63","67","82","83","84","85","86","97","105","117","139","165"]
POLARIS_KETTLE_WITH_WEIGHT_TYPE = ["98","106","164","177"]
POLARIS_HUMIDDIFIER_TYPE = ["4","15","17","18","25","44","70","71","72","73","74","75","87","99","147","155","157","158"]

@dataclass
class PolarisSensorEntityDescription(SensorEntityDescription):

    value_fn: Callable | None = None
    valueMap: dict | None = None
    mqttTopicCurrentValue: str | None = None

SENSORS_ALL_DEVICES = [
    PolarisSensorEntityDescription(
        key="sensor/temperature",
        name="Temperature",
        translation_key="temperature_sensor",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:thermometer",
    ),
    PolarisSensorEntityDescription(
        key="firmware",
        name="Firmware Version",
        translation_key="firmware_sensor",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_registry_enabled_default=True,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:information-outline",
    ),
    PolarisSensorEntityDescription(
        key="devtype",
        name="Device Type",
        translation_key="type_sensor",
        device_class=None,
        native_unit_of_measurement=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:information-outline",
    ),
    PolarisSensorEntityDescription(
        key="diag/rssi",
        name="rssi",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
    ),
]

SENSORS_HUMIDIFIER = [
    PolarisSensorEntityDescription(
        key="sensor/humidity",
        name="Humidity",
        translation_key="humidity_sensor",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:water-percent",
    ),
]

SENSORS_WEIGHT = [
    PolarisSensorEntityDescription(
        key="weight",
        name="weight",
        translation_key="weight_sensor",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:weight-gram",
    ),
]

@dataclass
class PolarisSwitchEntityDescription(SwitchEntityDescription):

    mqttTopicCommand: str | None = None
    mqttTopicCurrentValue: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None

SWITCHES_ALL_DEVICES = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power-standby",
    ),
    PolarisSwitchEntityDescription(
        key="sound",
        translation_key="sound_switch",
        entity_category=EntityCategory.CONFIG,
        name="Sound",
        mqttTopicCommand="control/sound",
        mqttTopicCurrentValue="state/sound",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
#        icon="mdi:volume-high",
    ),
    PolarisSwitchEntityDescription(
        key="child_lock",
        translation_key="child_lock_switch",
        entity_category=EntityCategory.CONFIG,
        name="Child lock",
        mqttTopicCommand="control/child_lock",
        mqttTopicCurrentValue="state/child_lock",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
#        icon="mdi:lock",
    ),
    PolarisSwitchEntityDescription(
        key="backlight",
        translation_key="backlight_switch",
        entity_category=EntityCategory.CONFIG,
        name="Backlight",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
#        icon="mdi:alarm-light",
    ),
]

SWITCHES_HUMIDIFIER = [
    PolarisSwitchEntityDescription(
        key="ioniser",
        translation_key="ioniser_switch",
        entity_category=EntityCategory.CONFIG,
        name="Ioniser",
        mqttTopicCommand="control/ioniser",
        mqttTopicCurrentValue="state/ioniser",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:atom-variant",
    ),
    PolarisSwitchEntityDescription(
        key="warm_stream",
        translation_key="warm_stream_switch",
        entity_category=EntityCategory.CONFIG,
        name="Warm stream",
        mqttTopicCommand="control/warm_stream",
        mqttTopicCurrentValue="state/warm_stream",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:heat-wave",
    ),
]

@dataclass
class PolarisWaterHeaterEntityDescription(WaterHeaterEntityEntityDescription): # breaks_in_ha_version="2026.1"

    mqttTopicCurrentMode: str | None = None
    mqttTopicCommandMode: str | None = None
    mqttTopicCurrentTemperature: str | None = None
    mqttTopicCommandTemperature: str | None = None
    mqttTopicTargetTemperature: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None
    min_temp: float | None = None
    max_temp: float | None = None
    operation_list: str | None = None
    mode: str | None = None

WATER_HEATERS = [
    PolarisWaterHeaterEntityDescription(
        key="water_heater",
        translation_key="water_heater",
        entity_category=EntityCategory.CONFIG,
        name="water_heater",
        mqttTopicCommandMode="control/mode",
        mqttTopicCommandTemperature="control/temperature",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCurrentTemperature="state/sensor/temperature",
        mqttTopicTargetTemperature="state/temperature",
        payload_on="1",
        payload_off="0",
#        icon="mdi:kettle",
        min_temp=30,
        max_temp=100,
        mode="off",
        operation_list = {"off": "0", "performance": "1", "electric": "3", "heat_pump": "4", "eco": "5"}
    )
]

@dataclass
class PolarisHumidifierEntityDescription(HumidifierEntityDescription):

    mqttTopicCurrentState: str | None = None
    mqttTopicCommandState: str | None = None
    mqttTopicCurrentMode: str | None = None
    mqttTopicCommandMode: str | None = None
    mqttTopicCurrentHumidity: str | None = None
    mqttTopicCurrentTargetHumidity: str | None = None
    mqttTopicCommandTargetHumidity: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None
    min_humidity: int | None = None
    max_humidity: int | None = None
    mode: str | None = None
    available_modes: str | None = None

HUMIDIFIERS = [
    PolarisHumidifierEntityDescription(
        name="Humidifier",
        key="humidifier",
        translation_key="humidifier",
        mode="auto",
        available_modes={"auto": "1", "comfort": "2", "baby": "3", "sleep": "4", "boost": "5", "home": "6", "eco": "7"},
        mqttTopicCurrentState = "state/mode",
        mqttTopicCommandState = "control/mode",
        mqttTopicCurrentMode = "state/mode",
        mqttTopicCommandMode = "control/mode",
        mqttTopicCurrentHumidity = "state/sensor/humidity",
        mqttTopicCurrentTargetHumidity = "state/humidity",
        mqttTopicCommandTargetHumidity = "control/humidity",
        payload_on = "1",
        payload_off = "0",
        min_humidity = 30,
        max_humidity = 75,
        device_class=HumidifierDeviceClass.HUMIDIFIER,
        icon="mdi:air-humidifier",
    )
]

@dataclass
class PolarisNumberEntityDescription(NumberEntityDescription):

    mqttTopicCurrentIntensity: str | None = None
    mqttTopicCommandIntensity: str | None = None
    
NUMBERS = [
    PolarisNumberEntityDescription(
        key="intensity",
        name="intensity",
        translation_key="intensity",
        mqttTopicCurrentIntensity = "state/intensity",
        mqttTopicCommandIntensity = "control/intensity",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None,
        entity_registry_enabled_default=True,
        native_max_value=7,
        native_min_value=0,
        native_step=1,
    )
]

@dataclass
class PolarisSelectEntityDescription(SelectEntityDescription):

    options: dict[str, str] | None = None
    mqttTopicCurrentMode: str | None = None
    mqttTopicCommandMode: str | None = None
    mqttTopicCommandTemperature: str | None = None
    mqttTopicTargetTemperature: str | None = None

SELECTS = [
    PolarisSelectEntityDescription(
        key="select_mode_kettle",
        name="select_mode_kettle",
        translation_key="select_mode_kettle",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCommandMode="control/mode",
        mqttTopicCommandTemperature="control/temperature",
        mqttTopicTargetTemperature="state/temperature",
        options={
            "not_selected": 0,
            "black_tea": 100,
            "baby_bottle": 40,
            "instant_coffee": 95,
            "green_tea": 80,
            "flower_tea": 80,
            "tea_bag": 100,
            "red_tea": 90,
            "puerh_tea": 95,
            "oolong_tea": 90,
            "white_tea": 65,
            "herbal_tea": 90,
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:receipt-text",
        entity_registry_enabled_default=True,
    )
]

@dataclass
class PolarisLightEntityDescription(SelectEntityDescription):

    mqttTopicCurrentColor: str | None = None
    mqttTopicCommandColor: str | None = None
    mqttTopicCurrentState: str | None = None
    mqttTopicCommandState: str | None = None

LIGHTS = [
    PolarisLightEntityDescription(
        key="night",
        name="night",
        translation_key="night_light",
        mqttTopicCurrentColor="state/program_data/0",
        mqttTopicCommandColor="control/program_data/0",
        mqttTopicCurrentState="state/night",
        mqttTopicCommandState="control/night",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
    )
]

@dataclass
class PolarisBinarySensorEntityDescription(BinarySensorEntityDescription):

    mqttTopicBaseStatus: str | None = None

BINARYSENSOR_KETTLE = [
    PolarisBinarySensorEntityDescription(
        key="base",
        name="base",
        translation_key="base_binary_sensor",
        mqttTopicBaseStatus="state/error/empty_base",
        device_class=None,     #BinarySensorDeviceClass.PLUG,
        entity_registry_enabled_default=True,
    )
]

@dataclass
class PolarisButtonEntityDescription(ButtonEntityDescription):

    actions: str | None = None

BUTTON_COOKER = [
    PolarisButtonEntityDescription(
        key="button_stop",
        name="button_stop",
        translation_key="button_stop",
        device_class=None,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        actions={"press"},
    )
]

@dataclass
class PolarisTimeEntityDescription(TimeEntityDescription):

    actions: str | None = None

TIME_INPUT = [
    PolarisTimeEntityDescription(
        key="time_stop",
        name="time_stop",
        translation_key="time_stop",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        actions={"press"},
    )
]

