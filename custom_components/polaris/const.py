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
    UnitOfTime,
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
    0:   {"model": "All devices", "class": "All"},
    140: {"model": "PAW-0804(c3-test)", "class": "air-cleaner"},
    151: {"model": "PPA-2025", "class": "air-cleaner"},
    152: {"model": "PPA-4050", "class": "air-cleaner"},
    172: {"model": "PAW-0804", "class": "air-cleaner"},
    203: {"model": "PPA-2025", "class": "air-cleaner"},
    204: {"model": "PPA-4050", "class": "air-cleaner"},
    236: {"model": "PPAT-02A", "class": "air-cleaner"},
    238: {"model": "PPAT-80P", "class": "air-cleaner"},
    239: {"model": "PPAT-90GDi", "class": "air-cleaner"},
    250: {"model": "PPA-2025", "class": "air-cleaner"},
    251: {"model": "PPA-4050", "class": "air-cleaner"},
    34:  {"model": "PHB-1551-WIFI", "class": "blender"},
    35:  {"model": "PHB-1503-WIFI-(old)", "class": "blender"},
    93:  {"model": "PHB-1350-WIFI", "class": "blender"},
    11:  {"model": "PWH-IDF06", "class": "boiler"},
    30:  {"model": "SIGMA-WI-FI", "class": "boiler"},
    31:  {"model": "ENIGMA-WI-FI", "class": "boiler"},
    249: {"model": "RZBE", "class": "boiler"},
    7:   {"model": "PVCR-3200", "class": "cleaner"},
    12:  {"model": "PVCR-3300", "class": "cleaner"},
    19:  {"model": "PVCR-0833", "class": "cleaner"},
    21:  {"model": "PVCR-0735", "class": "cleaner"},
    22:  {"model": "PVCR-1050", "class": "cleaner"},
    23:  {"model": "PVCR-1028", "class": "cleaner"},
    24:  {"model": "PVCR-1229", "class": "cleaner"},
    43:  {"model": "PVCR-0833", "class": "cleaner"},
    66:  {"model": "PVCR-3900", "class": "cleaner"},
    68:  {"model": "PVCR-3100", "class": "cleaner"},
    76:  {"model": "PVCR-3200", "class": "cleaner"},
    81:  {"model": "PVCR-3400", "class": "cleaner"},
    88:  {"model": "PVCR-3800", "class": "cleaner"},
    100: {"model": "PVCR-Wave-15", "class": "cleaner"},
    101: {"model": "PVCR-0726-Aqua", "class": "cleaner"},
    102: {"model": "PVCR-1226-Aqua", "class": "cleaner"},
    104: {"model": "PVCR-0905", "class": "cleaner"},
    107: {"model": "PVCR-0926", "class": "cleaner"},
    108: {"model": "PVCR-0726-GYRO", "class": "cleaner"},
    109: {"model": "PVCR-1226-GYRO", "class": "cleaner"},
    110: {"model": "PVCR-4105", "class": "cleaner"},
    112: {"model": "PVCR-3700", "class": "cleaner"},
    113: {"model": "PVCR-4000", "class": "cleaner"},
    115: {"model": "PVCR-3200", "class": "cleaner"},
    119: {"model": "PVCR-5001", "class": "cleaner"},
    122: {"model": "PVCR-G2-3600", "class": "cleaner"},
    123: {"model": "PVCR-6001", "class": "cleaner"},
    124: {"model": "PVCRDC-5002", "class": "cleaner"},
    125: {"model": "PVCRDC-6002", "class": "cleaner"},
    126: {"model": "PVCRDC-0101", "class": "cleaner"},
    127: {"model": "PVCR-4105", "class": "cleaner"},
    128: {"model": "PVCRAC-7050", "class": "cleaner"},
    129: {"model": "PVCR-G2-3200", "class": "cleaner"},
    130: {"model": "PVCR-3600", "class": "cleaner"},
    131: {"model": "PVCR-3900", "class": "cleaner"},
    133: {"model": "PVCR-G2-0726W", "class": "cleaner"},
    134: {"model": "PVCR-G2-0926W", "class": "cleaner"},
    135: {"model": "PVCR-G2-1226", "class": "cleaner"},
    142: {"model": "PVCR-4500", "class": "cleaner"},
    146: {"model": "PVCR-5001", "class": "cleaner"},
    148: {"model": "PVCR-6001", "class": "cleaner"},
    149: {"model": "PVCRDC-5002", "class": "cleaner"},
    150: {"model": "PVCRDC-6002", "class": "cleaner"},
    154: {"model": "PVCR-5001", "class": "cleaner"},
    156: {"model": "PVCR-0905", "class": "cleaner"},
    160: {"model": "PVCRDC-0101", "class": "cleaner"},
    163: {"model": "PVCR-0735", "class": "cleaner"},
    178: {"model": "PVCRAC-7750", "class": "cleaner"},
    181: {"model": "PVCRDC-5006", "class": "cleaner"},
    186: {"model": "PVCRDC-6004", "class": "cleaner"},
    187: {"model": "PVCR-6003", "class": "cleaner"},
    193: {"model": "PVCR-G2-0826", "class": "cleaner"},
    195: {"model": "PVCR-4500", "class": "cleaner"},
    197: {"model": "PVCR-4000", "class": "cleaner"},
    198: {"model": "PVCRAC-7790", "class": "cleaner"},
    199: {"model": "PVCR-4250", "class": "cleaner"},
    201: {"model": "PVCR-5003", "class": "cleaner"},
    202: {"model": "PVCRDC-5004", "class": "cleaner"},
    211: {"model": "PVCR-4260", "class": "cleaner"},
    212: {"model": "PVCRAC-7290", "class": "cleaner"},
    213: {"model": "PVCRDC-5002", "class": "cleaner"},
    217: {"model": "PVCRDC-G2-5002", "class": "cleaner"},
    218: {"model": "PVCRDC-G2-6002", "class": "cleaner"},
    219: {"model": "PVCR-G2-5001", "class": "cleaner"},
    220: {"model": "PVCR-G2-6001", "class": "cleaner"},
    221: {"model": "PVCR-6001", "class": "cleaner"},
    241: {"model": "PVCR-4250", "class": "cleaner"},
    242: {"model": "PVCR-5005", "class": "cleaner"},
    246: {"model": "PRWC-3001", "class": "cleaner"},
    45:  {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    103: {"model": "PACM-2080AC", "class": "coffeemaker"},
    166: {"model": "PACM-2085GC", "class": "coffeemaker"},
    190: {"model": "PCM-1560", "class": "coffeemaker"},
    200: {"model": "PACM-2081AC", "class": "coffeemaker"},
    207: {"model": "PCM-2070CG", "class": "coffeemaker"},
    222: {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    235: {"model": "AM7310-(test)", "class": "coffeemaker"},
    247: {"model": "PCM-1255", "class": "coffeemaker"},
    1:   {"model": "EVO-0225", "class": "cooker"},
    9:   {"model": "PMC-0526WIFI", "class": "cooker"},
    10:  {"model": "PMC-0521WIFI", "class": "cooker"},
    39:  {"model": "PMC-0528WIFI", "class": "cooker"},
    40:  {"model": "PMC-0526WIFI", "class": "cooker"},
    41:  {"model": "PMC-0521WIFI", "class": "cooker"},
    47:  {"model": "PMC-0530WIFI", "class": "cooker"},
    48:  {"model": "PMC-0528WIFI", "class": "cooker"},
    55:  {"model": "PMC-0524WIFI", "class": "cooker"},
    77:  {"model": "PMC-5040WIFI", "class": "cooker"},
    78:  {"model": "PMC-5050WIFI", "class": "cooker"},
    79:  {"model": "PMC-5017WIFI", "class": "cooker"},
    80:  {"model": "PMC-5020WIFI", "class": "cooker"},
    89:  {"model": "PMC-5055WIFI", "class": "cooker"},
    95:  {"model": "PMC-00000", "class": "cooker"},
    114: {"model": "PMC-5060 Smart Motion", "class": "cooker"},
    138: {"model": "PMC-0526WIFI", "class": "cooker"},
    162: {"model": "PMC-5063WIFI", "class": "cooker"},
    169: {"model": "PPC-1505 Wi-FI", "class": "cooker"},
    183: {"model": "PPC-1505 Wi-FI*", "class": "cooker"},
    192: {"model": "PMC-5017WIFI", "class": "cooker"},
    206: {"model": "PMC-0524WIFI", "class": "cooker"},
    210: {"model": "PMC-0590AD", "class": "cooker"},
    215: {"model": "PMC-5001WIFI", "class": "cooker"},
    240: {"model": "PMC-5060 Smart Motion*", "class": "cooker"},
    90:  {"model": "PVCS-2090", "class": "cordless_cleaner"},
    111: {"model": "PVCS-1150", "class": "cordless_cleaner"},
    136: {"model": "PVCS-4070", "class": "cordless_cleaner"},
    229: {"model": "PVCS-4070", "class": "cordless_cleaner"},
    230: {"model": "PVCS-8200", "class": "cordless_cleaner"},
    232: {"model": "PVCS-6020", "class": "cordless_cleaner"},
    233: {"model": "PVCSDC-3005", "class": "cordless_cleaner"},
    234: {"model": "PVCSDC-3000", "class": "cordless_cleaner"},
    180: {"model": "PSF-3315", "class": "fan"},
    248: {"model": "PSF-4025", "class": "fan"},
    96:  {"model": "PGP-4001", "class": "grill"},
    179: {"model": "PGP-3010-SMOKELESS", "class": "grill"},
    120: {"model": "PHD-4000", "class": "hair_care"},
    145: {"model": "PHSC-1234", "class": "hair_care"},
    171: {"model": "PHSB-5000DF", "class": "hair_care"},
    184: {"model": "PHS-1300", "class": "hair_care"},
    16:  {"model": "PHV-1401", "class": "heater"},
    46:  {"model": "PCH-0320WIFI", "class": "heater"},
    49:  {"model": "PMH-21XX", "class": "heater"},
    64:  {"model": "PMH-21XX", "class": "heater"},
    65:  {"model": "PCH-0320WIFI", "class": "heater"},
    4:   {"model": "PUH-9105/PUH-2709", "class": "humidifier"},
    15:  {"model": "PUH-7406", "class": "humidifier"},
    17:  {"model": "PUH-9105/PUH-2709", "class": "humidifier"},
    18:  {"model": "PUH-9105/PUH-2709", "class": "humidifier"},
    25:  {"model": "PUH-6090", "class": "humidifier"},
    44:  {"model": "PUH-9105/PUH-2709", "class": "humidifier"},
    70:  {"model": "PUH-9105/PUH-2709", "class": "humidifier"},
    71:  {"model": "PUH-1010", "class": "humidifier"},
    72:  {"model": "PUH-2300", "class": "humidifier"},
    73:  {"model": "PUH-3030", "class": "humidifier"},
    74:  {"model": "PUH-9009", "class": "humidifier"},
    75:  {"model": "PUH-4040", "class": "humidifier"},
    87:  {"model": "PUH-8080/PUH-4606", "class": "humidifier"},
    99:  {"model": "PUH-4040", "class": "humidifier"},
    137: {"model": "PUH-4066", "class": "humidifier"},
    147: {"model": "PUH-0205", "class": "humidifier"},
    153: {"model": "PUH-4055", "class": "humidifier"},
    155: {"model": "PUH-8802", "class": "humidifier"},
    157: {"model": "PUH-4550", "class": "humidifier"},
    158: {"model": "PUH-6060", "class": "humidifier"},
    91:  {"model": "PIR-2624AK-3m", "class": "iron"},
    159: {"model": "PSS-9090K", "class": "iron"},
    161: {"model": "PIR-3074SG", "class": "iron"},
    173: {"model": "PIR-3210AK-3m", "class": "iron"},
    174: {"model": "PIR-3225AK-3m", "class": "iron"},
    191: {"model": "PSS-2002K", "class": "iron"},
    132: {"model": "PWF-2005", "class": "irrigator"},
    252: {"model": "PWF-2005", "class": "irrigator"},
    2:   {"model": "PWK-1775CGLD", "class": "kettle"},
    6:   {"model": "PWK-1725CGLD", "class": "kettle"},
    8:   {"model": "PWK-1755CAD", "class": "kettle"},
    29:  {"model": "PWK-1712CGLD", "class": "kettle"},
    36:  {"model": "PWK-17107CGLD-WIFI-(old)", "class": "kettle"},
    37:  {"model": "PWK-7111CGLD-WIFI-(old)", "class": "kettle"},
    38:  {"model": "PWK-1712CGLD", "class": "kettle"},
    51:  {"model": "PWK-1775CGLD", "class": "kettle"},
    52:  {"model": "PWK-1725CGLD", "class": "kettle"},
    53:  {"model": "PWK-1755CAD", "class": "kettle"},
    54:  {"model": "PWK-1712CGLD", "class": "kettle"},
    56:  {"model": "PWK-1775CGLD", "class": "kettle"},
    57:  {"model": "PWK-1725CGLD", "class": "kettle"},
    58:  {"model": "PWK-1755CAD", "class": "kettle"},
    59:  {"model": "PWK-1712CGLD", "class": "kettle"},
    60:  {"model": "PWK-1775CGLD", "class": "kettle"},
    61:  {"model": "PWK-1725CGLD", "class": "kettle"},
    62:  {"model": "PWK-1755CAD", "class": "kettle"},
    63:  {"model": "PWK-1712CGLD", "class": "kettle"},
    67:  {"model": "PWK-1720CGLD", "class": "kettle"},
    82:  {"model": "PWK-725CGLD", "class": "kettle"},
    83:  {"model": "PWK-1712CGLD-RGB", "class": "kettle"},
    84:  {"model": "PWK-1720CGLD-RGB", "class": "kettle"},
    85:  {"model": "PWK-1775CGLD-SMART", "class": "kettle"},
    86:  {"model": "PWK-1725CGLD", "class": "kettle"},
    97:  {"model": "PWK-1712CGLD", "class": "kettle"},
    98:  {"model": "PWK-1775CGLD", "class": "kettle"},
    105: {"model": "PWK-1725CGLD", "class": "kettle"},
    106: {"model": "PWK-1725CGLD", "class": "kettle"},
    117: {"model": "PWK-1712CGLD", "class": "kettle"},
    121: {"model": "PWK-1774CAD", "class": "kettle"},
    139: {"model": "PWK-1775CGLD-VOICE", "class": "kettle"},
    164: {"model": "PWK-1728CGLDA", "class": "kettle"},
    165: {"model": "PWK-1755CAD-VOICE", "class": "kettle"},
    175: {"model": "PWK-1823CGLD", "class": "kettle"},
    176: {"model": "PWK-1841CGLD", "class": "kettle"},
    177: {"model": "PWK-1725CGLD", "class": "kettle"},
    185: {"model": "PWK-1755CAD", "class": "kettle"},
    188: {"model": "PWK-1775CGLD", "class": "kettle"},
    189: {"model": "PWK-1746CA", "class": "kettle"},
    194: {"model": "PWK-1725CGLD", "class": "kettle"},
    196: {"model": "PWK-1725CGLD", "class": "kettle"},
    205: {"model": "PWK-1538CC", "class": "kettle"},
    208: {"model": "PWK-1712CGLD", "class": "kettle"},
    209: {"model": "PWK-1729CAD", "class": "kettle"},
    223: {"model": "PWK-1775CGLD", "class": "kettle"},
    244: {"model": "PWK-1716CGLD", "class": "kettle"},
    245: {"model": "PWK-0105", "class": "kettle"},
    32:  {"model": "PMG-2580", "class": "meat_grinder"},
    216: {"model": "PMG-3060", "class": "meat_grinder"},
    237: {"model": "SM-8095", "class": "multicooker"},
    116: {"model": "Smart-Lid", "class": "other"},
    92:  {"model": "PGS-1450CWIFI", "class": "steamer"},
    94:  {"model": "PSS-7070KWIFI", "class": "steamer"},
    50:  {"model": "PETB-0202TC", "class": "toothbrush"},
}

POLARIS_KETTLE_TYPE = ["2","6","8","29","36","37","38","51","52","53","54","56","57","58","59","60","61","62","63","67","82","83","84","85","86","97","105","117","121","139","165","175","176","189","194","196","205","209"]
POLARIS_KETTLE_WITH_WEIGHT_TYPE = ["98","106","164","177","185","188","208","223","244","245"]
POLARIS_HUMIDDIFIER_TYPE = ["4","15","17","18","25","44","70","71","72","73","74","75","87","99","137","147","153","155","157","158"]
POLARIS_COOKER_TYPE = ["1","9","10","39","40","41","47","48","55","77","78","79","80","89","95","114","138","162","169","183","192","206","210","215","240"]

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

SENSORS_COOKER = [
    PolarisSensorEntityDescription(
        key="time",
        name="time_to_end",
        translation_key="time_to_end_sensor",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:timer",
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

SWITCHES_COOKER = [
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
        key="keepwarm",
        translation_key="keepwarm_switch",
        entity_category=EntityCategory.CONFIG,
        name="Keepwarm",
        mqttTopicCommand="control/keepwarm",
        mqttTopicCurrentValue="state/keepwarm",
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

    mqttTopicCurrent: str | None = None
    mqttTopicCommand: str | None = None
    
NUMBER_HUMIDIFIER = [
    PolarisNumberEntityDescription(
        key="intensity",
        name="intensity",
        translation_key="intensity",
        mqttTopicCurrent = "state/intensity",
        mqttTopicCommand = "control/intensity",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None,
        entity_registry_enabled_default=True,
        native_max_value=7,
        native_min_value=0,
        native_step=1,
    )
]

NUMBER_COOKER = [
    PolarisNumberEntityDescription(
        key="set_temperature",
        name="set_temperature",
        translation_key="set_temperature",
        mqttTopicCurrent = "control/set_temperature",
        mqttTopicCommand = "control/set_temperature",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None,
        entity_registry_enabled_default=True,
        native_max_value=160,
        native_min_value=20,
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

SELECT_KETTLE = [
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

SELECT_COOKER = [
    PolarisSelectEntityDescription(
        key="select_mode_cooker",
        name="select_mode_cooker",
        translation_key="select_mode_cooker",
        mqttTopicCurrentMode="state/steps",
        mqttTopicCommandMode="control/steps",
        options={
            "not_selected":  "[]",
            "Мой рецепт +":  "[{\"mode\":1,   \"time\":1200,  \"temperature\":115}]",
            "Разогрев":      "[{\"mode\":2,   \"time\":1200,  \"temperature\":115}]",
            "Выпечка":       "[{\"mode\":3,   \"time\":3600,  \"temperature\":130}]",
            "Крупа":         "[{\"mode\":4,   \"time\":2400,  \"temperature\":115}]",
            "Тушение":       "[{\"mode\":6,   \"time\":7200,  \"temperature\":93}]",
            "Жарка":         "[{\"mode\":7,   \"time\":300,   \"temperature\":160}]",
            "Плов":          "[{\"mode\":9,   \"time\":3600,  \"temperature\":120}]",
            "Йогурт":        "[{\"mode\":12,  \"time\":28800, \"temperature\":38}]",
            "Овсянка":       "[{\"mode\":13,  \"time\":300,   \"temperature\":96}]",
            "Варка":         "[{\"mode\":15,  \"time\":1800,  \"temperature\":115}]",
            "Молочная каша": "[{\"mode\":17,  \"time\":3600,  \"temperature\":95}]",
            "Суп":           "[{\"mode\":18,  \"time\":3600,  \"temperature\":97}]",
            "Холодец":       "[{\"mode\":24,  \"time\":21600, \"temperature\":93}]",
            "Творог":        "[{\"mode\":27,  \"time\":2400,  \"temperature\":80}]",
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

    mqttTopicStatus: str | None = None

BINARYSENSOR_KETTLE = [
    PolarisBinarySensorEntityDescription(
        key="base",
        name="base",
        translation_key="base_binary_sensor",
        mqttTopicStatus="state/error/empty_base",
        device_class=None,     #BinarySensorDeviceClass.PLUG,
        entity_registry_enabled_default=True,
    )
]

BINARYSENSOR_LID = [
    PolarisBinarySensorEntityDescription(
        key="lid",
        name="lid",
        translation_key="lid_binary_sensor",
        mqttTopicStatus="state/lid_open",
        device_class=None,     #BinarySensorDeviceClass.PLUG,
        entity_registry_enabled_default=True,
    )
]

@dataclass
class PolarisButtonEntityDescription(ButtonEntityDescription):

    payloads: str | None = None
    mqttTopicCommand: str | None = None

BUTTON_COOKER = [
    PolarisButtonEntityDescription(
        key="button_stop",
        name="button_stop",
        translation_key="button_stop",
        mqttTopicCommand="control/steps",
        device_class=None,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        payloads="[]",
    )
]

@dataclass
class PolarisTimeEntityDescription(TimeEntityDescription):

        min_time: int | None = None
        max_time: int | None = None
        default_time: int | None = None
        mqttTopicCurrentTime: str | None = None
        mqttTopicCommandTime: str | None = None

TIME_COOKER = [
    PolarisTimeEntityDescription(
        key="delay_start",
        name="delay_start",
        translation_key="delay_start",
        mqttTopicCurrentTime="state/delay_start",
        mqttTopicCommandTime="control/delay_start",
        min_time=1,
        max_time=720,
        default_time=0,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
    ),
    PolarisTimeEntityDescription(
        key="cooking_time",
        name="cooking_time",
        translation_key="cooking_time",
        mqttTopicCurrentTime="control/cooking_time",
        mqttTopicCommandTime="control/cooking_time",
        min_time=1,
        max_time=720,
        default_time=20,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
    )
]

