"""The Polaris IQ Home component."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import datetime
import json
from zoneinfo import ZoneInfo

import voluptuous as vol

from homeassistant.components.vacuum import (
    DOMAIN,
    ATTR_CLEANED_AREA,
    StateVacuumEntity,
#    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    ClimateEntityDescription,
    HVACMode,
)
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
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    UnitOfTime,
    UnitOfVolume,
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
    Platform.TIME,
    Platform.CLIMATE,
    Platform.VACUUM
]

# Global values
DOMAIN = "polaris"
MQTT_ROOT_TOPIC = "MQTT_ROOT_TOPIC"
MQTT_ROOT_TOPIC_DEFAULT = "polaris"
DEVICETYPE = "DEVICETYPE"
DEVICEID = "DEVICEID"
MANUFACTURER = "Polaris IQ Home"
CUSTOM_SELECT_FILE_PATH = "www/polaris/polaris_custom_select.js"

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
    69:  {"model": "Ballu-OneAir-ASP-100", "class": "air-cleaner"},
}

POLARIS_KETTLE_TYPE = ["2","6","8","29","36","37","38","51","52","53","54","56","57","58","59","60","61","62","63","67","82","83","84","85","86","97","105","117","121","139","165","175","176","189","194","196","205","209"]
POLARIS_KETTLE_WITH_WEIGHT_TYPE = ["98","106","164","177","185","188","208","223","244","245"]
POLARIS_KETTLE_WITH_NIGHT_TYPE = ["36","37","86","97","106","117","164","175","176","177","189","194","196","205","208","209","244"]
POLARIS_KETTLE_WITH_BACKLIGHT_TYPE = ["36","37","51","52","53","54","60","61","62","63","67","82","83","84","85","86","97","98","105","106","117","139","164","175","176","177","188","189","194","196","208","209","223","244","245"]
POLARIS_HUMIDDIFIER_TYPE = ["4","15","17","18","25","44","70","71","72","73","74","75","87","99","137","147","153","155","157","158"]
POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE = ["4","15","17","18","44","70","72","73","74","137","147","153","155","157","158"]
POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE = ["4","15","17","18","44","70","72","74","147","157","158"]
POLARIS_HUMIDDIFIER_LOW_FAN_TYPE = ["25","71","72","73","74","75","87","99","137","153","155","157","158"]
POLARIS_HUMIDDIFIER_7_MODE_TYPE = ["17","18","44","70"]
POLARIS_HUMIDDIFIER_5A_MODE_TYPE = ["4"]
POLARIS_HUMIDDIFIER_5B_MODE_TYPE = ["72","74","87","147","155"]
POLARIS_HUMIDDIFIER_4_MODE_TYPE = ["15","71","73","75","99"]
POLARIS_HUMIDDIFIER_3A_MODE_TYPE = ["25"]
POLARIS_HUMIDDIFIER_3B_MODE_TYPE = ["153","157","158"]
POLARIS_HUMIDDIFIER_1_MODE_TYPE = ["137"]
POLARIS_COOKER_TYPE = ["1","9","10","39","40","41","47","48","55","77","78","79","80","89","95","114","138","162","169","183","192","206","210","215","240"]
POLARIS_COOKER_WITH_LID_TYPE = ["9","39","40","41","47","48","55","77","78","79","80","89","95","114","138","162","169","183","192","206","210","215","240"]
POLARIS_COFFEEMAKER_TYPE = ["103", "166", "200"]
POLARIS_COFFEEMAKER_ROG_TYPE = ["45", "190", "207", "222", "235", "247"]
POLARIS_CLIMATE_TYPE = ["69"]
POLARIS_AIRCLEANER_TYPE = ["140", "151", "152", "172", "203", "204", "236", "238", "239", "250", "251"]
POLARIS_VACUUM_TYPE = ["7"]

HUMIDDIFIER_5A_AVAILABLE_MODES = {"auto": "1", "comfort": "2", "baby": "3", "sleep": "4", "boost": "5"}
HUMIDDIFIER_5B_AVAILABLE_MODES = {"auto": "1", "sleep": "4", "boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_4_AVAILABLE_MODES = {"auto": "1", "boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_3A_AVAILABLE_MODES = {"boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_3B_AVAILABLE_MODES = {"auto": "1", "boost": "5", "eco": "7"}
HUMIDDIFIER_1_AVAILABLE_MODES = {"boost": "5"}

KETTLE_ERROR = {
"00": "no_error",
"01": "low_water",
"02": "kettle_out_of_base",
"03": "temperature_sensor_failure",
"04": "temperature_sensor_failure",
"05": "child_lock",
"06": "recommended_to_change_water",
"07": "changed_water_for_long_time"
}
HUMIDDIFIER_ERROR = {
"00": "no_error",
"01": "low_water",
"02": "child_lock",
"03": "replace_filter",
"04": "maximum_schedules",
"05": "clean_tank"
}
COOKER_ERROR = {
"00": "no_error",
"01": "temperature_sensor_failure",
"02": "temperature_sensor_failure",
"06": "cup_not_present",
"07": "child_lock",
"08": "gesture_sensor_error"
}
COFFEEMAKER_ERROR = {
"00": "no_error",
"01": "side_door_open",
"02": "waste_container_not_installed",
"03": "drip_tray_not_installed",
"04": "the_brewing_unit_not_installed",
"05": "missing_water_tank",
"06": "waste_container_full",
"07": "not_enough_coffee_beans",
"08": "water_supply_blocked",
"09": "code_e001",
"10": "code_e002",
"11": "code_e003",
"12": "code_e004",
"13": "code_e005",
"14": "decalcification_required",
"15": "water_changed_for_long_time",
"16": "cleaning_milk_system",
"17": "cleaning_brewing_system",
"18": "decalcification_progress",
"19": "cleaning_hydraulic_system",
"20": "check_water_tank",
"98": "nothing_is_selected",
"99": "cappuccinator_false"
}

AIRCLEANER_ERROR = {
"00": "no_error",
"01": "replace_filter",
"02": "child_lock"
}

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
        name="RSSI",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
    ),
    PolarisSensorEntityDescription(
        key="error/code",
        name="error",
        translation_key="error",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
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
    PolarisSensorEntityDescription(
        key="expendables",
        name="filter_retain",
        translation_key="filter_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:filter",
    ),
    PolarisSensorEntityDescription(
        key="expendables",
        name="clean_retain",
        translation_key="clean_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:cup-water",
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

SENSORS_COFFEEMAKER = [
    PolarisSensorEntityDescription(
        key="mode",
        name="mode",
        translation_key="mode_sensor",
        valueMap={
            "0": "off",
            "1": "espresso",
            "2": "ristretto",
            "3": "long_espresso",
            "4": "americano",
            "5": "heating",
            "8": "cappuccino",
            "9": "latte",
            "10": "flat_white",
            "11": "cortado",
            "12": "double_espresso",
            "13": "double_cappuccino",
            "14": "double_latte",
            "15": "double_long_espresso",
            "16": "double_macchiato",
            "17": "milk_coffee",
            "18": "macchiato",
            "19": "latte_macchiato",
            "20": "hot_water",
            "21": "hot_milk foam",
            "22": "hot_milk"
        },
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:coffee-maker",
    ),
    PolarisSensorEntityDescription(
        key="program_data/5",
        name="power_state",
        translation_key="power_state",
        valueMap={
            "01": "power_on",
            "02": "power_off",
            "03": "turns_on",
            "04": "turns_off"
        },
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:power",
    ),
]

SENSORS_COFFEEMAKER_ROG = [
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
        name="RSSI",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
    ),
    PolarisSensorEntityDescription(
        key="error/code",
        name="error",
        translation_key="error",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
    ),
]

SENSORS_CLIMATE = [
    PolarisSensorEntityDescription(
        key="sensor/co2",
        name="CO2",
        translation_key="co2_sensor",
        device_class=None,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
#        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:molecule-co2",
    ),
    PolarisSensorEntityDescription(
        key="expendables",
        name="filter_retain",
        translation_key="filter_retain",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:filter",
    ),
]

SENSORS_AIRCLEANER = [
    PolarisSensorEntityDescription(
        key="sensor/pm2",
        name="PM2.5",
        translation_key="pm2_5_sensor",
        device_class=None,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:molecule",
    ),
    PolarisSensorEntityDescription(
        key="expendables",
        name="filter_retain",
        translation_key="filter_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:filter",
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
        name="RSSI",
        translation_key="rssi",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:wifi",
    ),
    PolarisSensorEntityDescription(
        key="error/code",
        name="error",
        translation_key="error",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:alert",
    ),
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
]

SWITCH_KETTLE_BACKLIGHT = [
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

SWITCH_HUMIDIFIER_BACKLIGHT = [
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

SWITCH_HUMIDIFIER_IONISER = [
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
]

SWITCH_HUMIDIFIER_WARM_STREAM = [
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

SWITCHES_COFFEEMAKER = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/program_data/5",
        mqttTopicCurrentValue="state/program_data/5",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="03",
        payload_off="04",
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
    ),
]

SWITCHES_COFFEEMAKER_ROG = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="5",
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
    ),
]

SWITCHES_CLIMATE = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="5",
        payload_off="0",
        icon="mdi:power-standby",
    ),
    PolarisSwitchEntityDescription(
        key="volume",
        translation_key="sound_switch",
        entity_category=EntityCategory.CONFIG,
        name="Volume",
        mqttTopicCommand="control/volume",
        mqttTopicCurrentValue="state/volume",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
    ),
    PolarisSwitchEntityDescription(
        key="backlight",
        translation_key="backlight_switch",
        entity_category=EntityCategory.CONFIG,
        name="Backlight",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
    ),
]

SWITCHES_AIRCLEANER = [
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
        key="ultraviolet",
        translation_key="ultraviolet_switch",
        entity_category=EntityCategory.CONFIG,
        name="Ultraviolet",
        mqttTopicCommand="control/warm_stream",
        mqttTopicCurrentValue="state/warm_stream",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:white-balance-sunny",
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
        mode="boost",
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
    native_value: int | None = None
    
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
        native_value=1,
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
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=True,
        native_max_value=160,
        native_min_value=20,
        native_step=1,
        native_value=115,
        mode="box",
    )
]

NUMBERS_COFFEEMAKER = [
    PolarisNumberEntityDescription(
        key="amount",
        name="amount",
        translation_key="amount",
        mqttTopicCurrent = "state/amount",
        mqttTopicCommand = "control/amount",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        entity_registry_enabled_default=True,
        native_max_value=250,
        native_min_value=20,
        native_step=5,
        native_value=40,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="weight",
        name="weight",
        translation_key="weight",
        mqttTopicCurrent = "state/weight",
        mqttTopicCommand = "control/weight",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        entity_registry_enabled_default=True,
        native_max_value=12,
        native_min_value=7,
        native_step=1,
        native_value=9,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="tank",
        name="tank",
        translation_key="tank",
        mqttTopicCurrent = "state/tank",
        mqttTopicCommand = "control/tank",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.WATER,
        native_unit_of_measurement=UnitOfVolume.MILLILITERS,
        entity_registry_enabled_default=True,
        native_max_value=250,
        native_min_value=50,
        native_step=5,
        native_value=100,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="pressure",
        name="pressure",
        translation_key="pressure",
        mqttTopicCurrent = "state/pressure",
        mqttTopicCommand = "control/pressure",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=True,
        native_max_value=100,
        native_min_value=0,
        native_step=5,
        native_value=40,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="speed",
        name="speed",
        translation_key="speed",
        mqttTopicCurrent = "state/speed",
        mqttTopicCommand = "control/speed",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=True,
        native_max_value=100,
        native_min_value=0,
        native_step=5,
        native_value=30,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="temperature",
        name="temperature",
        translation_key="temperature",
        mqttTopicCurrent = "state/temperature",
        mqttTopicCommand = "control/temperature",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=True,
        native_max_value=95,
        native_min_value=0,
        native_step=1,
        native_value=92,
        mode="slider",
    ),
]

NUMBERS_COFFEEMAKER_ROG = [
    PolarisNumberEntityDescription(
        key="display_time",
        name="display_time",
        translation_key="display_time",
        mqttTopicCurrent = "state/program_data/0",
        mqttTopicCommand = "control/program_data/0",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        entity_registry_enabled_default=True,
        native_max_value=30,
        native_min_value=10,
        native_step=5,
        native_value=10,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="amount",
        name="amount",
        translation_key="amount",
        mqttTopicCurrent = "state/amount",
        mqttTopicCommand = "control/amount",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        entity_registry_enabled_default=True,
        native_max_value=200,
        native_min_value=30,
        native_step=5,
        native_value=40,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="tank",
        name="tank",
        translation_key="speed",
        mqttTopicCurrent = "state/tank",
        mqttTopicCommand = "control/tank",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        entity_registry_enabled_default=True,
        native_max_value=40,
        native_min_value=1,
        native_step=1,
        native_value=15,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="temperature",
        name="temperature",
        translation_key="temperature",
        mqttTopicCurrent = "state/temperature",
        mqttTopicCommand = "control/temperature",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=True,
        native_max_value=105,
        native_min_value=95,
        native_step=5,
        native_value=95,
        mode="slider",
    ),
]

NUMBERS_AIRCLEANER = [
    PolarisNumberEntityDescription(
        key="time",
        name="time_timer",
        translation_key="time_timer",
        mqttTopicCurrent = "state/time",
        mqttTopicCommand = "control/time",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_registry_enabled_default=True,
        native_max_value=12,
        native_min_value=0,
        native_step=1,
        native_value=1,
        mode="slider",
    ),
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
            "my_recipe_plus": "[{\"mode\":1, \"time\":1200, \"temperature\":115}]",
            "reheat": "[{\"mode\":2, \"time\":1200, \"temperature\":115}]",
            "cake": "[{\"mode\":3, \"time\":3600, \"temperature\":130}]",
            "soaked_rice": "[{\"mode\":4, \"time\":2400, \"temperature\":115}]",
            "stew": "[{\"mode\":6, \"time\":7200, \"temperature\":93}]",
            "fry": "[{\"mode\":7, \"time\":300, \"temperature\":160}]",
            "pilaf": "[{\"mode\":9, \"time\":3600, \"temperature\":120}]",
            "yogurt": "[{\"mode\":12, \"time\":28800, \"temperature\":38}]",
            "oatmeal": "[{\"mode\":13, \"time\":300, \"temperature\":96}]",
            "milk_porridge": "[{\"mode\":17, \"time\":3600, \"temperature\":95}]",
            "soup": "[{\"mode\":18, \"time\":3600, \"temperature\":97}]",
            "meat": "[{\"mode\":24, \"time\":21600, \"temperature\":93}]",
            "cottage_cheese": "[{\"mode\":27, \"time\":2400, \"temperature\":80}]",
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:receipt-text",
        entity_registry_enabled_default=True,
    )
]

SELECT_COFFEEMAKER = [
    PolarisSelectEntityDescription(
        key="select_mode_cofeemaker",
        name="select_mode_cofeemaker",
        translation_key="select_mode_cofeemaker",
        mqttTopicCurrentMode="control/mode",                            # ??????
        mqttTopicCommandMode="control/mode",
        options={
        "not_selected": "[{\"mode\": 0, \"amount\": 0, \"weight\": 0, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 0}]",
        "espresso": "[{\"mode\": 1, \"amount\": 40, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "ristretto": "[{\"mode\": 2, \"amount\": 30, \"weight\": 11, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "long_espresso": "[{\"mode\": 3, \"amount\": 100, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "americano": "[{\"mode\": 4, \"amount\": 80, \"weight\": 9, \"tank\": 100, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "cappuccino": "[{\"mode\": 8, \"amount\": 50, \"weight\": 9, \"tank\": 0, \"pressure\": 35, \"speed\": 0, \"temperature\": 92}]",
        "latte": "[{\"mode\": 9, \"amount\": 40, \"weight\": 9, \"tank\": 0, \"pressure\": 15, \"speed\": 30, \"temperature\": 92}]",
        "flat_white": "[{\"mode\": 10, \"amount\": 80, \"weight\": 9, \"tank\": 0, \"pressure\": 5, \"speed\": 30, \"temperature\": 92}]",
        "cortado": "[{\"mode\": 11, \"amount\": 50, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 10, \"temperature\": 92}]",
        "double_espresso": "[{\"mode\": 12, \"amount\": 40, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "double_cappuccino": "[{\"mode\": 13, \"amount\": 80, \"weight\": 12, \"tank\": 0, \"pressure\": 50, \"speed\": 0, \"temperature\": 92}]",
        "double_latte": "[{\"mode\": 14, \"amount\": 60, \"weight\": 10, \"tank\": 0, \"pressure\": 20, \"speed\": 45, \"temperature\": 92}]",
        "double_long_espresso": "[{\"mode\": 15, \"amount\": 100, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 0, \"temperature\": 92}]",
        "double_macchiato": "[{\"mode\": 16, \"amount\": 60, \"weight\": 10, \"tank\": 0, \"pressure\": 60, \"speed\": 0, \"temperature\": 92}]",
        "milk_coffee": "[{\"mode\": 17, \"amount\": 50, \"weight\": 9, \"tank\": 0, \"pressure\": 0, \"speed\": 30, \"temperature\": 92}]",
        "macchiato": "[{\"mode\": 18, \"amount\": 40, \"weight\": 9, \"tank\": 0, \"pressure\": 40, \"speed\": 0, \"temperature\": 92}]",
        "latte_macchiato": "[{\"mode\": 19, \"amount\": 40, \"weight\": 9, \"tank\": 0, \"pressure\": 20, \"speed\": 25, \"temperature\": 92}]",
        "hot_water": "[{\"mode\": 20, \"amount\": 0, \"weight\": 0, \"tank\": 100, \"pressure\": 0, \"speed\": 0, \"temperature\": 0}]",
        "hot_milk_foam": "[{\"mode\": 21, \"amount\": 0, \"weight\": 0, \"tank\": 0, \"pressure\": 35, \"speed\": 0, \"temperature\": 0}]",
        "hot_milk": "[{\"mode\": 22, \"amount\": 0, \"weight\": 0, \"tank\": 0, \"pressure\": 0, \"speed\": 45, \"temperature\": 0}]"
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:receipt-text",
        entity_registry_enabled_default=True,
    )
]

SELECT_COFFEEMAKER_ROG = [
    PolarisSelectEntityDescription(
        key="select_mode_cofeemaker_rog",
        name="select_mode_cofeemaker",
        translation_key="select_mode_cofeemaker",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCommandMode="control/mode",
        options={
            "not_selected": "[{\"mode\": 0, \"amount\": 30, \"tank\": 0, \"temperature\": 95}]",
            "espresso": "[{\"mode\": 1, \"amount\": 65, \"tank\": 0, \"temperature\": 95}]",
            "doppio": "[{\"mode\": 1, \"amount\": 115, \"tank\": 0, \"temperature\": 95}]",
            "cappuccino": "[{\"mode\": 2, \"amount\": 50, \"tank\": 15, \"temperature\": 95}]",
            "double_cappuccino": "[{\"mode\": 2, \"amount\": 100, \"tank\": 25, \"temperature\": 95}]",
            "latte": "[{\"mode\": 3, \"amount\": 65, \"tank\": 32, \"temperature\": 95}]",
            "double_latte": "[{\"mode\": 3, \"amount\": 115, \"tank\": 40, \"temperature\": 95}]",
            "lungo": "[{\"mode\": 1, \"amount\": 120, \"tank\": 0, \"temperature\": 95}]",
            "flat_white": "[{\"mode\": 2, \"amount\": 70, \"tank\": 20, \"temperature\": 95}]",
            "clearing": "[{\"mode\": 4, \"amount\": 0, \"tank\": 0, \"temperature\": 95}]",
            "heating": "[{\"mode\": 5, \"amount\": 0, \"tank\": 0, \"temperature\": 95}]",
            "hot_milk": "[{\"mode\": 6, \"amount\": 0, \"tank\": 15, \"temperature\": 95}]",
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:receipt-text",
        entity_registry_enabled_default=True,
    )
]

SELECT_CLIMATE = [
    PolarisSelectEntityDescription(
        key="select_melody",
        name="Melody",
        translation_key="select_melody",
        mqttTopicCurrentMode="state/amount",
        mqttTopicCommandMode="control/amount",
        options={
          "mute": 0,
          "rainstorm": 1,
          "surf": 2,
          "forest": 3,
          "birdsong": 4,
          "bonfire": 5,
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:music-note",
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
        device_class=None,
        entity_registry_enabled_default=True,
    )
]

BINARYSENSOR_WATER_TANK = [
    PolarisBinarySensorEntityDescription(
        key="water_tank",
        name="water_tank",
        translation_key="water_tank_binary_sensor",
        mqttTopicStatus="state/error/water",
        device_class=None,
        entity_registry_enabled_default=True,
    )
]

BINARYSENSOR_CAPPUCCINATOR = [
    PolarisBinarySensorEntityDescription(
        key="cappuccinator",
        name="cappuccinator",
        translation_key="cappuccinator_binary_sensor",
        mqttTopicStatus="state/tank",
        device_class=None,
        entity_registry_enabled_default=True,
    )
]

BINARYSENSOR_AVAILABLE = [
    PolarisBinarySensorEntityDescription(
        key="available",
        name="available",
        translation_key="available_binary_sensor",
        mqttTopicStatus="state/error/connection",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=True,
    )
]

@dataclass
class PolarisButtonEntityDescription(ButtonEntityDescription):

    payloads: str | None = None
    mqttTopicCommand: str | None = None

BUTTON_HUMIDIFIER = [
    PolarisButtonEntityDescription(
        key="button_reset_filter",
        name="button_reset_filter",
        translation_key="button_reset_filter",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[0,0]",
        icon="mdi:filter",
    ),
        PolarisButtonEntityDescription(
        key="button_reset_tank",
        name="button_reset_tank",
        translation_key="button_reset_tank",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[1,0]",
        icon="mdi:cup-water",
    )
]

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
    ),
        PolarisButtonEntityDescription(
        key="button_start",
        name="button_start",
        translation_key="button_start",
        mqttTopicCommand="control/steps",
        device_class=None,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        payloads="[]",
    )
]

BUTTON_COFFEEMAKER = [
    PolarisButtonEntityDescription(
        key="button_stop",
        name="button_stop",
        translation_key="button_stop_coffee",
        mqttTopicCommand="control/",
        device_class=None,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        payloads="[]",
    ),
    PolarisButtonEntityDescription(
        key="button_start",
        name="button_start",
        translation_key="button_start_coffee",
        mqttTopicCommand="control/",
        device_class=None,
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        payloads="[]",
    )
]

BUTTON_CLIMATES = [
    PolarisButtonEntityDescription(
        key="button_reset_filter",
        name="button_reset_filter",
        translation_key="button_reset_filter",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[100]",
        icon="mdi:filter",
    )
]

BUTTON_AIRCLEANER = [
    PolarisButtonEntityDescription(
        key="button_reset_filter",
        name="button_reset_filter",
        translation_key="button_reset_filter",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[0]",
        icon="mdi:filter",
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

@dataclass
class PolarisClimateEntityDescription(ClimateEntityDescription):

    fan_mode: str | None = None
    fan_modes: str | None = None
    preset_mode: str | None = None
    preset_modes: str | None = None
    hvac_modes: list | None = None
    supported_features: int | None = None
    mqttTopicStateTemperature: str | None = None
    mqttTopicCommandTemperature: str | None = None
    mqttTopicCurrentTemperature: str | None = None
    mqttTopicStateFanMode: str | None = None
    mqttTopicCommandFanMode: str | None = None
    mqttTopicCommandPower: str | None = None
    mqttTopicCurrentPresetMode: str | None = None
    mqttTopicCommandPresetMode: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None
    min_temp: int | None = None
    max_temp: int | None = None
    temp_step: int | None = None


CLIMATES = [
    PolarisClimateEntityDescription(
        name = "Climate",
        key = "climate",
        translation_key = "climate",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7"},
        preset_mode = "passive",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4", "passive": "5"},
        hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        mqttTopicStateTemperature = "state/temperature",
        mqttTopicCommandTemperature = "control/temperature",
        mqttTopicCurrentTemperature = "state/sensor/temperature",
        mqttTopicStateFanMode = "state/speed",
        mqttTopicCommandFanMode = "control/speed",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        payload_on = "5",
        payload_off = "0",
        min_temp = 5,
        max_temp = 25,
        temp_step = 1,
        device_class = None,
    )
]

AIRCLEANER = [
    PolarisClimateEntityDescription(
        name = "Aircleaner",
        key = "aircleaner",
        translation_key = "aircleaner",
        fan_mode = "auto",
        fan_modes = {"auto": "0", "low": "1", "medium": "2", "high": "3"},
        preset_mode = "auto",
        preset_modes = {"auto": "1", "hands": "2", "night": "3"},
        hvac_modes = [HVACMode.OFF, HVACMode.DRY],
        supported_features = (
            ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        mqttTopicStateFanMode = "state/intensity",
        mqttTopicCommandFanMode = "control/intensity",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        payload_on = "1",
        payload_off = "0",
        device_class = None,
    )
]

@dataclass
class PolarisVacuumEntityDescription(ClimateEntityDescription):

    fan_mode: str | None = None
    fan_modes: str | None = None
    preset_mode: str | None = None
    preset_modes: str | None = None
    hvac_modes: list | None = None
    supported_features: int | None = None
    mqttTopicStateTemperature: str | None = None
    mqttTopicCommandTemperature: str | None = None
    mqttTopicCurrentTemperature: str | None = None
    mqttTopicStateFanMode: str | None = None
    mqttTopicCommandFanMode: str | None = None
    mqttTopicCommandPower: str | None = None
    mqttTopicCurrentPresetMode: str | None = None
    mqttTopicCommandPresetMode: str | None = None
    mqttTopicCommandMode: str | None = None
    mqttTopicCurrentMode: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None
    min_temp: int | None = None
    max_temp: int | None = None
    temp_step: int | None = None


VACUUM = [
    PolarisVacuumEntityDescription(
        name = "Vacuum",
        key = "vacuum",
        translation_key = "vacuum",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7"},
        preset_mode = "passive",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4", "passive": "5"},
        hvac_modes = [HVACMode.OFF, HVACMode.FAN_ONLY],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        mqttTopicCommandMode = "control/temperature",
        mqttTopicCurrentMode = "state/sensor/temperature",
        mqttTopicStateFanMode = "state/speed",
        mqttTopicCommandFanMode = "control/speed",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        payload_on = "5",
        payload_off = "0",
        min_temp = 5,
        max_temp = 25,
        temp_step = 1,
        device_class = None,
    )
]