"""
The Polaris IQ Home component.
v1.1.4-alpha.3
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import datetime
import json
from zoneinfo import ZoneInfo

import voluptuous as vol

from homeassistant.components.image import Image, ImageEntityDescription
from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.components.vacuum import (
    DOMAIN,
    ATTR_CLEANED_AREA,
    StateVacuumEntity,
    VacuumActivity,
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
from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityDescription
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
    UnitOfEnergy,
    UnitOfPower,
    UnitOfArea,
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
    Platform.VACUUM,
    Platform.FAN
#    Platform.IMAGE
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
    0:   {"model": "Unknown", "class": "all"},
    37:  {"model": "PWK-7111CGLD-WIFI", "class": "kettle"},
    245: {"model": "PWK-0105", "class": "kettle"},
    205: {"model": "PWK-1538CC", "class": "kettle"},
    271: {"model": "PWK-1701CGLD", "class": "kettle"},
    36:  {"model": "PWK-17107CGLD-WIFI", "class": "kettle"},
    29:  {"model": "PWK-1712CGLD", "class": "kettle"},
    38:  {"model": "PWK-1712CGLD", "class": "kettle"},
    54:  {"model": "PWK-1712CGLD", "class": "kettle"},
    59:  {"model": "PWK-1712CGLD", "class": "kettle"},
    63:  {"model": "PWK-1712CGLD", "class": "kettle"},
    97:  {"model": "PWK-1712CGLD", "class": "kettle"},
    117: {"model": "PWK-1712CGLD", "class": "kettle"},
    208: {"model": "PWK-1712CGLD", "class": "kettle"},
    83:  {"model": "PWK-1712CGLD-RGB", "class": "kettle"},
    253: {"model": "PWK-1715", "class": "kettle"},
    244: {"model": "PWK-1716CGLD", "class": "kettle"},
    67:  {"model": "PWK-1720CGLD", "class": "kettle"},
    84:  {"model": "PWK-1720CGLD-RGB", "class": "kettle"},
    6:   {"model": "PWK-1725CGLD", "class": "kettle"},
    52:  {"model": "PWK-1725CGLD", "class": "kettle"},
    57:  {"model": "PWK-1725CGLD", "class": "kettle"},
    61:  {"model": "PWK-1725CGLD", "class": "kettle"},
    82:  {"model": "PWK-1725CGLD", "class": "kettle"},
    86:  {"model": "PWK-1725CGLD", "class": "kettle"},
    105: {"model": "PWK-1725CGLD", "class": "kettle"},
    106: {"model": "PWK-1725CGLD", "class": "kettle"},
    177: {"model": "PWK-1725CGLD", "class": "kettle"},
    194: {"model": "PWK-1725CGLD", "class": "kettle"},
    196: {"model": "PWK-1725CGLD", "class": "kettle"},
    164: {"model": "PWK-1728CGLDA", "class": "kettle"},
    209: {"model": "PWK-1729CAD", "class": "kettle"},
    189: {"model": "PWK-1746CA", "class": "kettle"},
    260: {"model": "PWK-1746CA", "class": "kettle"},
    308: {"model": "PWK-1746CA", "class": "kettle"},
    8:   {"model": "PWK-1755CAD", "class": "kettle"},
    53:  {"model": "PWK-1755CAD", "class": "kettle"},
    58:  {"model": "PWK-1755CAD", "class": "kettle"},
    62:  {"model": "PWK-1755CAD", "class": "kettle"},
    185: {"model": "PWK-1755CAD", "class": "kettle"},
    165: {"model": "PWK-1755CAD-VOICE", "class": "kettle"},
    121: {"model": "PWK-1774CAD", "class": "kettle"},
    2:   {"model": "PWK-1775CGLD", "class": "kettle"},
    51:  {"model": "PWK-1775CGLD", "class": "kettle"},
    56:  {"model": "PWK-1775CGLD", "class": "kettle"},
    60:  {"model": "PWK-1775CGLD", "class": "kettle"},
    98:  {"model": "PWK-1775CGLD", "class": "kettle"},
    188: {"model": "PWK-1775CGLD", "class": "kettle"},
    223: {"model": "PWK-1775CGLD", "class": "kettle"},
    262: {"model": "PWK-1775CGLD", "class": "kettle"},
    263: {"model": "PWK-1775CGLD", "class": "kettle"},
    275: {"model": "PWK-1775CGLD", "class": "kettle"},
    294: {"model": "PWK-1775CGLD", "class": "kettle"},
    85:  {"model": "PWK-1775CGLD-SMART", "class": "kettle"},
    139: {"model": "PWK-1775CGLD-VOICE", "class": "kettle"},
    175: {"model": "PWK-1823CGLD", "class": "kettle"},
    254: {"model": "PWK-1823CGLD", "class": "kettle"},
    176: {"model": "PWK-1841CGLD", "class": "kettle"},
    255: {"model": "PWK-1841CGLD", "class": "kettle"},
    147: {"model": "PUH-0205", "class": "humidifier"},
    71:  {"model": "PUH-1010", "class": "humidifier"},
    72:  {"model": "PUH-2300", "class": "humidifier"},
    73:  {"model": "PUH-3030", "class": "humidifier"},
    75:  {"model": "PUH-4040", "class": "humidifier"},
    99:  {"model": "PUH-4040", "class": "humidifier"},
    153: {"model": "PUH-4055", "class": "humidifier"},
    137: {"model": "PUH-4066", "class": "humidifier"},
    157: {"model": "PUH-4550", "class": "humidifier"},
    158: {"model": "PUH-6060", "class": "humidifier"},
    25:  {"model": "PUH-6090", "class": "humidifier"},
    15:  {"model": "PUH-7406", "class": "humidifier"},
    87:  {"model": "PUH-8080_PUH-4606", "class": "humidifier"},
    155: {"model": "PUH-8802", "class": "humidifier"},
    74:  {"model": "PUH-9009", "class": "humidifier"},
    4:   {"model": "PUH-9105_PUH-2709", "class": "humidifier"},
    17:  {"model": "PUH-9105_PUH-2709", "class": "humidifier"},
    18:  {"model": "PUH-9105_PUH-2709", "class": "humidifier"},
    44:  {"model": "PUH-9105_PUH-2709", "class": "humidifier"},
    70:  {"model": "PUH-9105_PUH-2709", "class": "humidifier"},
    1:   {"model": "EVO-0225", "class": "cooker"},
    95:  {"model": "PMC-00000", "class": "cooker"},
    303: {"model": "PMC-0510", "class": "cooker"},
    301: {"model": "PMC-0515", "class": "cooker"},
    10:  {"model": "PMC-0521WIFI", "class": "cooker"},
    41:  {"model": "PMC-0521WIFI", "class": "cooker"},
    267: {"model": "PMC-0521WIFI", "class": "cooker"},
    55:  {"model": "PMC-0524WIFI", "class": "cooker"},
    206: {"model": "PMC-0524WIFI", "class": "cooker"},
    9:   {"model": "PMC-0526WIFI", "class": "cooker"},
    40:  {"model": "PMC-0526WIFI", "class": "cooker"},
    138: {"model": "PMC-0526WIFI", "class": "cooker"},
    39:  {"model": "PMC-0528WIFI", "class": "cooker"},
    48:  {"model": "PMC-0528WIFI", "class": "cooker"},
    268: {"model": "PMC-0528WIFI", "class": "cooker"},
    47:  {"model": "PMC-0530WIFI", "class": "cooker"},
    270: {"model": "PMC-0530WIFI", "class": "cooker"},
    210: {"model": "PMC-0590AD", "class": "cooker"},
    302: {"model": "PMC-0597", "class": "cooker"},
    215: {"model": "PMC-5001WIFI", "class": "cooker"},
    79:  {"model": "PMC-5017WIFI", "class": "cooker"},
    192: {"model": "PMC-5017WIFI", "class": "cooker"},
    80:  {"model": "PMC-5020WIFI", "class": "cooker"},
    266: {"model": "PMC-5020WIFI", "class": "cooker"},
    77:  {"model": "PMC-5040WIFI", "class": "cooker"},
    78:  {"model": "PMC-5050WIFI", "class": "cooker"},
    89:  {"model": "PMC-5055WIFI", "class": "cooker"},
    114: {"model": "PMC-5060-Smart-Motion", "class": "cooker"},
    240: {"model": "PMC-5060-Smart-Motion", "class": "cooker"},
    162: {"model": "PMC-5063WIFI", "class": "cooker"},
    169: {"model": "PPC-1505-WiFI", "class": "cooker"},
    183: {"model": "PPC-1505-WiFI", "class": "cooker"},
    235: {"model": "AM7310", "class": "coffeemaker"},
    305: {"model": "PACM-2072", "class": "coffeemaker"},
    103: {"model": "PACM-2080AC", "class": "coffeemaker"},
    261: {"model": "PACM-2080AC", "class": "coffeemaker"},
    276: {"model": "PACM-2080AC", "class": "coffeemaker"},
    277: {"model": "PACM-2080AC", "class": "coffeemaker"},
    200: {"model": "PACM-2081AC", "class": "coffeemaker"},
    265: {"model": "PACM-2081AC", "class": "coffeemaker"},
    280: {"model": "PACM-2081AC", "class": "coffeemaker"},
    166: {"model": "PACM-2085GC", "class": "coffeemaker"},
    278: {"model": "PACM-2085GC", "class": "coffeemaker"},
    247: {"model": "PCM-1255", "class": "coffeemaker"},
    45:  {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    222: {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    274: {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    279: {"model": "PCM-1540WIFI", "class": "coffeemaker"},
    190: {"model": "PCM-1560", "class": "coffeemaker"},
    207: {"model": "PCM-2070CG", "class": "coffeemaker"},
    172: {"model": "PAW-0804", "class": "air_cleaner"},
    140: {"model": "PAW-0804", "class": "air_cleaner"},
    151: {"model": "PPA-2025", "class": "air_cleaner"},
    203: {"model": "PPA-2025", "class": "air_cleaner"},
    250: {"model": "PPA-2025", "class": "air_cleaner"},
    152: {"model": "PPA-4050", "class": "air_cleaner"},
    204: {"model": "PPA-4050", "class": "air_cleaner"},
    251: {"model": "PPA-4050", "class": "air_cleaner"},
    236: {"model": "PPAT-02A", "class": "air_cleaner"},
    238: {"model": "PPAT-80P", "class": "air_cleaner"},
    239: {"model": "PPAT-90GDi", "class": "air_cleaner"},
    132: {"model": "PWF-2005", "class": "irrigator"},
    252: {"model": "PWF-2005", "class": "irrigator"},
    273: {"model": "PAF-4001WIFI", "class": "air_fryer"},
    290: {"model": "PAF-6003WIFI", "class": "air_fryer"},
    291: {"model": "PAF-8003WIFI", "class": "air_fryer"},
    292: {"model": "PAF-8005WIFI", "class": "air_fryer"},
    31:  {"model": "ENIGMA-WI-FI", "class": "boiler"},
    11:  {"model": "PWH-IDF06", "class": "boiler"},
    30:  {"model": "SIGMA-WIFI", "class": "boiler"},
    249: {"model": "VEKTOR-WIFI", "class": "boiler"},
    46:  {"model": "PCH-0320WIFI", "class": "heater"},
    65:  {"model": "PCH-0320WIFI", "class": "heater"},
    16:  {"model": "PHV-1401", "class": "heater"},
    49:  {"model": "PMH-21XX", "class": "heater"},
    64:  {"model": "PMH-21XX", "class": "heater"},
    101: {"model": "PVCR-0726-Aqua", "class": "cleaner"},
    108: {"model": "PVCR-0726-GYRO", "class": "cleaner"},
    21:  {"model": "PVCR-0735", "class": "cleaner"},
    163: {"model": "PVCR-0735", "class": "cleaner"},
    19:  {"model": "PVCR-0833", "class": "cleaner"},
    43:  {"model": "PVCR-0833", "class": "cleaner"},
    104: {"model": "PVCR-0905", "class": "cleaner"},
    156: {"model": "PVCR-0905", "class": "cleaner"},
    107: {"model": "PVCR-0926", "class": "cleaner"},
    23:  {"model": "PVCR-1028", "class": "cleaner"},
    22:  {"model": "PVCR-1050", "class": "cleaner"},
    102: {"model": "PVCR-1226-Aqua", "class": "cleaner"},
    109: {"model": "PVCR-1226-GYRO", "class": "cleaner"},
    24:  {"model": "PVCR-1229", "class": "cleaner"},
    68:  {"model": "PVCR-3100", "class": "cleaner"},
    7:   {"model": "PVCR-3200", "class": "cleaner"},
    76:  {"model": "PVCR-3200", "class": "cleaner"},
    115: {"model": "PVCR-3200", "class": "cleaner"},
    12:  {"model": "PVCR-3300", "class": "cleaner"},
    81:  {"model": "PVCR-3400", "class": "cleaner"},
    130: {"model": "PVCR-3600", "class": "cleaner"},
    112: {"model": "PVCR-3700", "class": "cleaner"},
    88:  {"model": "PVCR-3800", "class": "cleaner"},
    66:  {"model": "PVCR-3900", "class": "cleaner"},
    131: {"model": "PVCR-3900", "class": "cleaner"},
    113: {"model": "PVCR-4000", "class": "cleaner"},
    197: {"model": "PVCR-4000", "class": "cleaner"},
    110: {"model": "PVCR-4105", "class": "cleaner"},
    127: {"model": "PVCR-4105", "class": "cleaner"},
    199: {"model": "PVCR-4250", "class": "cleaner"},
    241: {"model": "PVCR-4250", "class": "cleaner"},
    211: {"model": "PVCR-4260", "class": "cleaner"},
    269: {"model": "PVCR-4260", "class": "cleaner"},
    142: {"model": "PVCR-4500", "class": "cleaner"},
    195: {"model": "PVCR-4500", "class": "cleaner"},
    307: {"model": "PVCR-4750", "class": "cleaner"},
    119: {"model": "PVCR-5001", "class": "cleaner"},
    146: {"model": "PVCR-5001", "class": "cleaner"},
    154: {"model": "PVCR-5001", "class": "cleaner"},
    201: {"model": "PVCR-5003", "class": "cleaner"},
    242: {"model": "PVCR-5005", "class": "cleaner"},
    123: {"model": "PVCR-6001", "class": "cleaner"},
    148: {"model": "PVCR-6001", "class": "cleaner"},
    221: {"model": "PVCR-6001", "class": "cleaner"},
    187: {"model": "PVCR-6003", "class": "cleaner"},
    256: {"model": "PVCR-7026", "class": "cleaner"},
    128: {"model": "PVCRAC-7050", "class": "cleaner"},
    212: {"model": "PVCRAC-7290", "class": "cleaner"},
    178: {"model": "PVCRAC-7750", "class": "cleaner"},
    198: {"model": "PVCRAC-7790", "class": "cleaner"},
    264: {"model": "PVCRAC-7790", "class": "cleaner"},
    126: {"model": "PVCRDC-0101", "class": "cleaner"},
    160: {"model": "PVCRDC-0101", "class": "cleaner"},
    124: {"model": "PVCRDC-5002", "class": "cleaner"},
    149: {"model": "PVCRDC-5002", "class": "cleaner"},
    213: {"model": "PVCRDC-5002", "class": "cleaner"},
    202: {"model": "PVCRDC-5004", "class": "cleaner"},
    181: {"model": "PVCRDC-5006", "class": "cleaner"},
    125: {"model": "PVCRDC-6002", "class": "cleaner"},
    150: {"model": "PVCRDC-6002", "class": "cleaner"},
    186: {"model": "PVCRDC-6004", "class": "cleaner"},
    257: {"model": "PVCRDC-7028", "class": "cleaner"},
    217: {"model": "PVCRDC-G2-5002", "class": "cleaner"},
    218: {"model": "PVCRDC-G2-6002", "class": "cleaner"},
    133: {"model": "PVCR-G2-0726W", "class": "cleaner"},
    193: {"model": "PVCR-G2-0826", "class": "cleaner"},
    134: {"model": "PVCR-G2-0926W", "class": "cleaner"},
    135: {"model": "PVCR-G2-1226", "class": "cleaner"},
    129: {"model": "PVCR-G2-3200", "class": "cleaner"},
    122: {"model": "PVCR-G2-3600", "class": "cleaner"},
    219: {"model": "PVCR-G2-5001", "class": "cleaner"},
    220: {"model": "PVCR-G2-6001", "class": "cleaner"},
    100: {"model": "PVCR-Wave-15", "class": "cleaner"},
    246: {"model": "PRWC-3001", "class": "window_cleaner"},
    93:  {"model": "PHB-1350-WIFI", "class": "blender"},
    35:  {"model": "PHB-1503-WIFI", "class": "blender"},
    34:  {"model": "PHB-1551-WIFI", "class": "blender"},
    282: {"model": "induction-hob", "class": "cooktop"},
    286: {"model": "XFC302I-B3SF", "class": "cooktop"},
    288: {"model": "XFC302T-B1D", "class": "cooktop"},
    285: {"model": "XFC604I", "class": "cooktop"},
    304: {"model": "XFC604I-(test)", "class": "cooktop"},
    284: {"model": "XFC604I-B8F", "class": "cooktop"},
    287: {"model": "XFC604T-B7D", "class": "cooktop"},
    289: {"model": "XFG640F-B3P", "class": "cooktop"},
    111: {"model": "PVCS-1150", "class": "cordless_cleaner"},
    90:  {"model": "PVCS-2090", "class": "cordless_cleaner"},
    136: {"model": "PVCS-4070", "class": "cordless_cleaner"},
    229: {"model": "PVCS-4070", "class": "cordless_cleaner"},
    232: {"model": "PVCS-6020", "class": "cordless_cleaner"},
    281: {"model": "PVCS-6020", "class": "cordless_cleaner"},
    230: {"model": "PVCS-8200", "class": "cordless_cleaner"},
    234: {"model": "PVCSDC-3000", "class": "cordless_cleaner"},
    233: {"model": "PVCSDC-3005", "class": "cordless_cleaner"},
    306: {"model": "PVCSDC-3005", "class": "cordless_cleaner"},
    180: {"model": "PSF-3315", "class": "fan"},
    248: {"model": "PSF-4025", "class": "fan"},
    179: {"model": "PGP-3010-SMOKELESS", "class": "grill"},
    96:  {"model": "PGP-4001", "class": "grill"},
    120: {"model": "PHD-4000", "class": "hair_care"},
    184: {"model": "PHS-1300", "class": "hair_care"},
    171: {"model": "PHSB-5000DF", "class": "hair_care"},
    145: {"model": "PHSC-1234", "class": "hair_care"},
    297: {"model": "8006", "class": "hood"},
    296: {"model": "8029", "class": "hood"},
    295: {"model": "6065A-600", "class": "hood"},
    283: {"model": "PGS-2250VA", "class": "iron"},
    91:  {"model": "PIR-2624AK-3m", "class": "iron"},
    161: {"model": "PIR-3074SG", "class": "iron"},
    173: {"model": "PIR-3210AK-3m", "class": "iron"},
    174: {"model": "PIR-3225AK-3m", "class": "iron"},
    191: {"model": "PSS-2002K", "class": "iron"},
    259: {"model": "PSS-8010K", "class": "iron"},
    159: {"model": "PSS-9090K", "class": "iron"},
    237: {"model": "SM-8095", "class": "kitchen_machine"},
    272: {"model": "SM-8095", "class": "kitchen_machine"},
    32:  {"model": "PMG-2580", "class": "meat_grinder"},
    216: {"model": "PMG-3060", "class": "meat_grinder"},
    116: {"model": "Smart-Lid", "class": "other"},
    299: {"model": "xbcook55", "class": "oven"},
    300: {"model": "xbcook56", "class": "oven"},
    298: {"model": "xbcook62", "class": "oven"},
    92:  {"model": "PGS-1450CWIFI", "class": "steamer"},
    94:  {"model": "PSS-7070KWIFI", "class": "steamer"},
    50:  {"model": "PETB-0202TC", "class": "toothbrush"},
    69:  {"model": "Ballu-OneAir-ASP-100", "class": "air_cleaner"}, # совместимость с <= v1.0.8
    869: {"model": "Ballu-OneAir-ASP-100", "class": "air_cleaner"},
    859: {"model": "Ballu-OneAir-ASP-200", "class": "air_cleaner"},
    826: {"model": "Electrolux-EAP-2050D_2075D", "class": "air_cleaner"},
    876: {"model": "Electrolux-Royal-Flash_Centurio-IQ-Inverter", "class": "boiler"},
    833: {"model": "Electrolux-Centurio-IQ-3", "class": "boiler"},
    802: {"model": "SmartInverter", "class": "boiler"},
    844: {"model": "Royal-Thermo-Aqua-Inverter_Royal-Thermo-Aqua-Inox-Inverter", "class": "boiler"},
    807: {"model": "Zanussi-Artendo_Azurro-PRO", "class": "boiler"},
    877: {"model": "Royal-Thermo-Major-Inverter_Smalto-Inverter", "class": "boiler"},
    806: {"model": "Transformer-DI-3", "class": "heater"},
    846: {"model": "Transformer-DI-4", "class": "heater"},
    847: {"model": "Wi-Fi-Convection-Heater", "class": "heater"},
    849: {"model": "Transformer-4", "class": "heater"},
    814: {"model": "Transformer-DI", "class": "heater"},
    808: {"model": "Electrolux-Atrium-DC_Zanussi-Siena-DC_Ballu-Lagoon", "class": "air_conditioner"},
    815: {"model": "Electrolux-Viking-DC_Zanussi-Perfecto-DC_Ballu-Greenland-DC", "class": "air_conditioner"},
    820: {"model": "Ballu-Platinum-Evol-DC_Olympio-Legend", "class": "air_conditioner"},
    813: {"model": "Electrolux-Smartline_Ballu-Eco-Smart_Ice-Peak", "class": "air_conditioner"},
    882: {"model": "Goldstar-GSAC_GSACI", "class": "air_conditioner"},
    868: {"model": "Electrolux-Loft-DC_Ballu-Platinum-Black-DC", "class": "air_conditioner"},
    851: {"model": "Zanussi-Massimo-Solar-2023", "class": "air_conditioner"},
    821: {"model": "Zanussi-Moderno-DC_Electrolux-Loft-DC", "class": "air_conditioner"},
    857: {"model": "Shuft-Berg_MBO-M1", "class": "air_conditioner"},
    860: {"model": "Ballu-Discovery-DC", "class": "air_conditioner"},
    856: {"model": "Toshiba", "class": "air_conditioner"},
    881: {"model": "UHB-960-ET", "class": "humidifier"},
    835: {"model": "Electrolux-YOGAhealthline-2", "class": "humidifier"},
    878: {"model": "Electrolux_Royal-Thermo", "class": "thermostat"},
    867: {"model": "Electrolux_Royal-Thermo", "class": "thermostat"},
    829: {"model": "Electrolux_Royal-Thermo", "class": "thermostat"},
}

POLARIS_KETTLE_TYPE = ["2","6","8","29","36","37","38","51","52","53","54","56","57","58","59","60","61","62","63","67","82","83","84","85","86","97","105","106","117","121","139","165","175","176","177","189","194","196","205","209","253","254","255","260","271","308"]
POLARIS_KETTLE_WITH_WEIGHT_TYPE = ["98","164","185","188","208","223","244","245","262","263","275","294"]
POLARIS_KETTLE_WITH_NIGHT_TYPE = ["36","37","86","97","106","117","164","175","176","177","189","194","196","205","208","209","244","253","254","255","260","271","308"]
POLARIS_KETTLE_WITH_BACKLIGHT_TYPE = ["36","37","51","52","53","54","60","61","62","63","67","82","83","84","85","86","97","98","105","106","117","139","164","175","176","177","188","189","194","196","208","209","223","244","245","253","254","255","260","262","263","271","275","294","308"]
POLARIS_KETTLE_WITH_TEA_TIME_MODE_TYPE = ["2","8","51","53","56","58","60","62","85","98","139","165","185","188","205","223","262","263","275","294"]
POLARIS_KETTLE_WITH_KEEP_WITH_WARM_MODE_TYPE = ["205","262","294"]
POLARIS_HUMIDDIFIER_TYPE = ["4","15","17","18","25","44","70","71","72","73","74","75","87","99","137","147","153","155","157","158","835","881"]
POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE = ["4","15","17","18","44","70","72","73","74","137","147","153","155","157","158","835"]
POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE = ["4","15","17","18","44","70","72","74","147","157","158","835","881"]
POLARIS_HUMIDDIFIER_LOW_FAN_TYPE = ["25","71","72","73","74","75","87","99","137","153","155","157","158"]
POLARIS_HUMIDDIFIER_7_MODE_TYPE = ["17","18","44","70"]
POLARIS_HUMIDDIFIER_5A_MODE_TYPE = ["4"]
POLARIS_HUMIDDIFIER_5B_MODE_TYPE = ["72","74","87","147","155"]
POLARIS_HUMIDDIFIER_4_MODE_TYPE = ["15","71","73","75","99"]
POLARIS_HUMIDDIFIER_3A_MODE_TYPE = ["25"]
POLARIS_HUMIDDIFIER_3B_MODE_TYPE = ["153","157","158"]
POLARIS_HUMIDDIFIER_2_MODE_TYPE = ["881"]
POLARIS_HUMIDDIFIER_1_MODE_TYPE = ["137"]
POLARIS_HUMIDDIFIER_11_MODE_TYPE = ["835"]
POLARIS_COOKER_TYPE = ["1","9","10","39","40","41","47","48","55","77","78","79","80","89","95","114","138","162","169","183","192","206","210","215","240","266","267","268","270","301","302","303","290","291","292"]
POLARIS_COOKER_WITH_LID_TYPE = ["9","39","40","41","47","48","55","77","78","79","80","89","95","114","138","162","169","183","192","206","210","215","240","266","267","268","270","301","302","303","290","291","292"]
POLARIS_COFFEEMAKER_TYPE = ["103", "166", "200","261","265","276","277","278","280","305"]
POLARIS_COFFEEMAKER_ROG_TYPE = ["45", "190", "207", "222", "235", "247", "274", "279"] 
POLARIS_CLIMATE_TYPE = ["69", "869", "859"]
POLARIS_AIRCLEANER_TYPE = ["140", "151", "152", "172", "203", "204", "236", "238", "239", "250", "251"]
POLARIS_AIRCLEANER_EAP_TYPE = ["826"]
POLARIS_VACUUM_TYPE = ["7","12","19","21","22","23","24","43","66","68","76","81","88","100","101","102","104","107","108","109","110","112","113","115","119","122","123","124","125","126","127","128","129","130","131","133","134","135","142","146","148","149","150","154","156","160","163","178","181","186","187","193","195","197","198","199","201","202","211","212","213","217","218","219","220","221","241","242","256","257","264","269","307"]
POLARIS_BOILER_TYPE = ["802","807","833","844","876","877"]
POLARIS_IRRIGATOR_TYPE = ["132", "252"]
POLARIS_HEATER_TYPE = ["806","846","847","849","814"]
POLARIS_AIRCONDITIONER_TYPE = ["813","820","882","808","815","868","851","821","857","860","856"]
POLARIS_THERMOSTAT_TYPE = ["878","867","829"]
POLARIS_FAN_TYPE = ["180","248"]
POLARIS_WINDOWCLEANER_TYPE = ["246"]

KETTLE_WITH_TEA_TIME_MODES = {"off": "0", "performance": "1", "electric": "3", "heat_pump": "4", "eco": "5", "gas": "6"}
KETTLE_WITH_KEEP_WITH_WARM_MODES = {"off": "0", "performance": "1", "high_demand": "2", "electric": "3", "heat_pump": "4", "eco": "5", "gas": "6"}
HUMIDDIFIER_5A_AVAILABLE_MODES = {"auto": "1", "comfort": "2", "baby": "3", "sleep": "4", "boost": "5"}
HUMIDDIFIER_5B_AVAILABLE_MODES = {"auto": "1", "sleep": "4", "boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_4_AVAILABLE_MODES = {"auto": "1", "boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_3A_AVAILABLE_MODES = {"boost": "5", "home": "6", "eco": "7"}
HUMIDDIFIER_3B_AVAILABLE_MODES = {"auto": "1", "boost": "5", "eco": "7"}
HUMIDDIFIER_2_AVAILABLE_MODES = {"home": "1", "auto": "2"}
HUMIDDIFIER_1_AVAILABLE_MODES = {"boost": "5"}
HUMIDDIFIER_11_AVAILABLE_MODES = {"home": "1", "auto": "2", "sleep": "3", "baby": "4", "comfort": "5", "fitnes": "6", "yoga": "7", "meditation": "8", "prana_hand": "9", "prana_auto": "10", "aroma": "11"}
AIRFRYER_1_MODES = {
            "my_recipe_plus": "[{\"mode\":1, \"time\":300, \"temperature\":100}]",
            "french_fries": "[{\"mode\":2, \"time\":1320, \"temperature\":190}]",
            "chicken": "[{\"mode\":3, \"time\":1800, \"temperature\":190}]",
            "steak": "[{\"mode\":4, \"time\":600, \"temperature\":200}]",
            "vegetables": "[{\"mode\":5, \"time\":1200, \"temperature\":180}]",
            "pie": "[{\"mode\":6, \"time\":1500, \"temperature\":170}]",
            "fish": "[{\"mode\":9, \"time\":900, \"temperature\":180}]",
            "dehydrate": "[{\"mode\":12, \"time\":18000, \"temperature\":80}]",
            "nuggets": "[{\"mode\":13, \"time\":600, \"temperature\":190}]",
        }
AIRFRYER_2_MODES = {
            "my_recipe_plus": "[{\"mode\":1, \"time\":300, \"temperature\":100}]",
            "french_fries": "[{\"mode\":2, \"time\":1320, \"temperature\":190}]",
            "chicken": "[{\"mode\":3, \"time\":2700, \"temperature\":190}]",
            "steak": "[{\"mode\":4, \"time\":600, \"temperature\":200}]",
            "vegetables": "[{\"mode\":5, \"time\":1200, \"temperature\":180}]",
            "pie": "[{\"mode\":6, \"time\":1500, \"temperature\":170}]",
            "fish": "[{\"mode\":9, \"time\":900, \"temperature\":180}]",
            "chicken_wings": "[{\"mode\":10, \"time\":1800, \"temperature\":190}]",
            "pizza": "[{\"mode\":11, \"time\":720, \"temperature\":180}]",
            "dehydrate": "[{\"mode\":12, \"time\":18000, \"temperature\":80}]",
            "nuggets": "[{\"mode\":13, \"time\":600, \"temperature\":190}]",
            "bacon": "[{\"mode\":14, \"time\":420, \"temperature\":180}]",
            "shrimps": "[{\"mode\":15, \"time\":840, \"temperature\":190}]",
        }

POLARIS_VACUUM_01_MODE_TYPE = [7,22,23,24,81,88,100,101,102,107,108,109,110,112]
POLARIS_VACUUM_02_MODE_TYPE = [12]
POLARIS_VACUUM_03_MODE_TYPE = [19,43]
POLARIS_VACUUM_04_MODE_TYPE = [21,68,122,130,133,134,135,163,193]
POLARIS_VACUUM_05_MODE_TYPE = [66,113,131,142,195,197]
POLARIS_VACUUM_06_MODE_TYPE = [76,115]
POLARIS_VACUUM_07_MODE_TYPE = [104,126]
POLARIS_VACUUM_08_MODE_TYPE = [119,123,124,125]
POLARIS_VACUUM_09_MODE_TYPE = [127]
POLARIS_VACUUM_10_MODE_TYPE = [128]
POLARIS_VACUUM_11_MODE_TYPE = [129]
POLARIS_VACUUM_12_MODE_TYPE = [146,148,149,150,154,201,202,213,217,218,219,220,221]
POLARIS_VACUUM_13_MODE_TYPE = [156,160]
POLARIS_VACUUM_14_MODE_TYPE = [178]
POLARIS_VACUUM_15_MODE_TYPE = [181,242,307]
POLARIS_VACUUM_16_MODE_TYPE = [186,187,256,257]
POLARIS_VACUUM_17_MODE_TYPE = [198,264]
POLARIS_VACUUM_18_MODE_TYPE = [199,211,212,241,269]

VACUUM_01_MODE = {"off": "0","random": "1","auto": "2","wall": "3","spiral": "4","recharge": "5"}
VACUUM_02_MODE = {"off": "0","wall": "1","spot": "2","auto": "3","recharge": "4","wet_cleaning": "5"}
VACUUM_03_MODE = {"off": "0","auto": "3","edge": "4","spot": "5","recharge": "8"}
VACUUM_04_MODE = {"off": "0","auto": "3","edge": "4","spot": "5","classic": "6","recharge": "8"}
VACUUM_05_MODE = {"off": "0","auto": "3","edge": "4","spot": "5","recharge": "8","intensive_cleaning_area": "13","create_map": "22","mapmaking_and_cleaning": "23","scheduled_room_cleaning": "24"}
VACUUM_06_MODE = {"off": "0","random": "1","auto": "2","wall": "3","spiral": "4","recharge": "5"}
VACUUM_07_MODE = {"off": "0","auto": "1","recharge": "2","area_cleaning": "3"}
VACUUM_08_MODE = {"off": "0","auto": "1","spot": "2","recharge": "3","area_cleaning": "4"}
VACUUM_09_MODE = {"off": "0","random": "1","auto": "2","wall": "3","spiral": "4","recharge": "5","y_shaped_wet_cleaning": "6","double_cleaning": "7"}
VACUUM_10_MODE = {"off": "0","auto": "1","recharge": "2","area_cleaning": "3","create_map": "4","cleaning_the_rag": "5","scheduled_room_cleaning": "6","spot": "7"}
VACUUM_11_MODE = {"off": "0","auto": "2","wall": "3","spiral": "4","recharge": "5"}
VACUUM_12_MODE = {"off": "0","auto": "1","spot": "2","recharge": "3","area_cleaning": "4","scheduled_room_cleaning": "5"}
VACUUM_13_MODE = {"off": "0","auto": "1","recharge": "2","area_cleaning": "3","scheduled_room_cleaning": "6"}
VACUUM_14_MODE = {"off": "0","auto": "1","spot": "2","recharge": "3","area_cleaning": "4","scheduled_room_cleaning": "5","mop_cleaning": "6","mop_drying": "7","self_cleaning": "8","create_map": "9","quick_cleaning": "10","thorough_cleaning": "11"}
VACUUM_15_MODE = {"off": "0","auto": "1","spot": "2","recharge": "3","area_cleaning": "4","scheduled_room_cleaning": "5","create_map": "6","thorough_cleaning": "7","quick_cleaning": "8"}
VACUUM_16_MODE = {"off": "0","edge": "4","spot": "5","auto": "6","recharge": "8","intensive_cleaning_area": "13","area_cleaning": "19","create_map": "22","mapmaking_and_cleaning": "23","scheduled_room_cleaning": "24","quick_cleaning": "25","thorough_cleaning": "26"}
VACUUM_17_MODE = {"off": "0","auto": "1","sweep": "2","sweep_mop": "3","mop": "4","recharge": "5","create_map": "7","scheduled_room_cleaning": "8","mop_cleaning": "9","mop_drying": "10","wall": "11","cut_hair": "12"}
VACUUM_18_MODE = {"off": "0","auto": "1","sweep": "2","sweep_mop": "3","mop": "4","recharge": "5","create_map": "7","scheduled_room_cleaning": "8"}

POLARIS_VACUUM_01_SPEED_TYPE = [12,19,21,43,68,163]
POLARIS_VACUUM_02_SPEED_TYPE = [7,22,23,24,66,76,113,115,122,130,131,133,134,135,142,193,197]
POLARIS_VACUUM_03_SPEED_TYPE = [195,212]
POLARIS_VACUUM_04_SPEED_TYPE = [186,187,256,257,264]
POLARIS_VACUUM_05_SPEED_TYPE = [81,88,100,101,102,107,108,109,110,112,127]
POLARIS_VACUUM_06_SPEED_TYPE = [104,119,123,124,125,126,128,129,146,148,149,150,154,156,160,178,181,198,199,201,202,211,213,217,218,219,220,221,241,242,269,307]

VACUUM_01_SPEED = {"low": "0", "high": "1"}
VACUUM_02_SPEED = {"low": "0", "medium": "1", "high": "2"}
VACUUM_03_SPEED = {"low": "0", "medium": "1", "high": "2", "max": "3"}
VACUUM_04_SPEED = {"min": "0", "low": "1", "medium": "2", "high": "3", "max": "4"}
VACUUM_05_SPEED = {"low": "1", "medium": "2", "high": "3"}
VACUUM_06_SPEED = {"low": "1", "medium": "2", "high": "3", "max": "4"}

POLARIS_VACUUM_NOT_WATER_TYPE = [19,23,43]
POLARIS_VACUUM_01_WATER_TYPE = [22,24]
POLARIS_VACUUM_02_WATER_TYPE = [7,76,115,199,211,212,241,269]
POLARIS_VACUUM_03_WATER_TYPE = [12,21,66,68,81,88,100,101,102,104,107,108,109,110,112,113,119,122,123,124,125,126,127,128,129,130,131,133,134,135,142,146,148,149,150,154,156,160,163,178,181,193,197,198,201,202,213,217,218,219,220,221,242,264,307]
POLARIS_VACUUM_04_WATER_TYPE = [186,187,195,256,257]

VACUUM_01_WATER = {"low": "0", "high": "1"}
VACUUM_02_WATER = {"low": "0", "medium": "1", "high": "2"}
VACUUM_03_WATER = {"low": "1", "medium": "2", "high": "3"}
VACUUM_04_WATER = {"low": "0", "medium": "1", "high": "2", "max": "3"}

POLARIS_VACUUM_SWITCH_CHILD_LOCK = [7,12,22,23,24,76,81,88,100,101,102,107,108,109,110,112,115,127,129,241,256,257,269]
POLARIS_VACUUM_SWITCH_VOLUME = [12,66,104,113,119,123,124,125,126,128,129,131,142,146,148,149,150,154,156,160,178,181,186,187,195,197,198,199,201,202,211,212,213,217,218,219,220,221,241,242,256,257,264,269,307]
POLARIS_VACUUM_SWITCH_TURBO = [81,88,100,101,102,104,107,108,109,110,112,119,123,124,125,126,127,128,129,142,146,148,149,150,154,156,160,178,181,186,187,195,198,199,201,202,211,212,213,217,218,219,220,221,241,242,256,257,264,269,307]
POLARIS_VACUUM_SWITCH_IONISER = [104,126,128,156,160,178,181,186,198,199,211,212,241,242,257,264,269,307]
POLARIS_VACUUM_SWITCH_STREAM_WARM = [178,181,186,187,199,211,241,242,256,257,269,307]
POLARIS_VACUUM_SWITCH_BACKLIGHT = [186,187,256,257]

POLARIS_VACUUM_EXPENDABLE_DUST = [7,12,19,21,22,23,24,43,66,68,76,81,88,100,101,102,107,108,109,110,112,113,115,122,127,130,131,133,134,135,163,193,197]
POLARIS_VACUUM_EXPENDABLE_MOP = [104,119,123,124,125,126,128,129,146,148,149,150,154,156,160,178,181,186,187,195,198,199,201,202,211,212,213,217,218,219,220,221,241,242,256,257,264,269,307]

POLARIS_VACUUM_SENSORS_01_PROGR_DATA = [104,119,123,124,125,126,128,146,148,149,150,154,156,160,178,181,201,202,213,217,218,219,220,221,242,307]
POLARIS_VACUUM_SENSORS_02_PROGR_DATA = [129,142,186,187,195,256,257]
POLARIS_VACUUM_SENSORS_03_PROGR_DATA = [198,212,241,264,269]

VACUUM_SWITCH_01_TURBO = [81,88,100,101,102,107,108,109,110,112,127]
VACUUM_SWITCH_02_TURBO = [104,126]
VACUUM_SWITCH_03_TURBO = [119,123,124,125,128,129,142,146,148,149,150,154,156,160,178,181,186,187,195,198,199,201,202,211,212,213,217,218,219,220,221,241,242,256,257,264,269,307]


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

WINDOWCLEANER_ERROR = {
"00": "no_error",
"02": "pressure_sensor",
"05": "low_water",
}
POLARIS_VACUUM_01_ERROR_CODE = [7,22,23,24,76,81,88,100,101,102,107,108,109,110,112,115,127]
POLARIS_VACUUM_02_ERROR_CODE = [12,19,21,43,66,68,113,122,130,131,133,134,135,142,163,193,195,197]
POLARIS_VACUUM_03_ERROR_CODE = [119,123,124,125,146,148,149,150,154,201,202,213,217,218,219,220,221]
POLARIS_VACUUM_04_ERROR_CODE = [104,126,128,156,160]
POLARIS_VACUUM_05_ERROR_CODE = [181,242]
POLARIS_VACUUM_06_ERROR_CODE = [178]
POLARIS_VACUUM_07_ERROR_CODE = [198,199,211,241,264,269]
POLARIS_VACUUM_08_ERROR_CODE = [212]
POLARIS_VACUUM_09_ERROR_CODE = [186,187,256,257]
POLARIS_VACUUM_10_ERROR_CODE = [129]
POLARIS_VACUUM_11_ERROR_CODE = [307]


VACUUM_01_ERROR = {
  "0":"no_error",
  "1":"v01_error_1",
  "2":"v01_error_2",
  "4":"v01_error_4",
  "8":"v01_error_8",
  "10":"v01_error_10",
  "11":"v01_error_11",
  "12":"v01_error_12",
  "13":"v01_error_13",
  "16":"v01_error_16",
  "22":"v01_error_22",
  "32":"v01_error_32",
  "64":"v01_error_64",
  "128":"v01_error_128"
}
VACUUM_02_ERROR = { 
  "0":"no_error", 
  "2":"v02_error_2",
  "4":"v02_error_4",
  "5":"v02_error_5",
  "6":"v02_error_6",
  "7":"v02_error_7",
  "9":"v02_error_9",
  "10":"v02_error_10",
  "11":"v02_error_11",
  "12":"v02_error_12",
  "13":"v02_error_13",
  "21":"v02_error_21",
  "22":"v02_error_22",
  "23":"v02_error_23",
  "30":"v02_error_30",
  "31":"v02_error_31",
  "32":"v02_error_32",
  "33":"v02_error_33",
  "40":"v02_error_40"
}
VACUUM_03_ERROR = {
  "0":"no_error",
  "2":"v03_error_2",
  "3":"v03_error_3",
  "4":"v03_error_4",
  "6":"v03_error_6",
  "7":"v03_error_7",
  "8":"v03_error_8",
  "9":"v03_error_9",
  "10":"v03_error_10",
  "12":"v03_error_12",
  "13":"v03_error_13",
  "14":"v03_error_14",
  "15":"v03_error_15",
  "16":"v03_error_16",
  "18":"v03_error_18",
  "19":"v03_error_19",
  "20":"v03_error_20",
  "22":"v03_error_22",
  "24":"v03_error_24",
  "25":"v03_error_25",
  "26":"v03_error_26",
  "27":"v03_error_27",
  "28":"v03_error_28",
  "31":"v03_error_31",
  "32":"v03_error_32",
  "33":"v03_error_33",
  "34":"v03_error_34",
  "35":"v03_error_35",
  "36":"v03_error_36",
  "37":"v03_error_37",
  "38":"v03_error_38",
  "39":"v03_error_39",
  "40":"v03_error_40",
  "41":"v03_error_41",
  "42":"v03_error_42",
  "44":"v03_error_44",
  "45":"v03_error_45",
  "46":"v03_error_46",
  "47":"v03_error_47",
  "48":"v03_error_48",
  "53":"v03_error_53"
}
VACUUM_04_ERROR = {
  "0":"no_error",
  "1":"v04_error_1",
  "2":"v04_error_2",
  "3":"v04_error_3",
  "4":"v04_error_4",
  "5":"v04_error_5",
  "6":"v04_error_6",
  "8":"v04_error_8",
  "9":"v04_error_9",
  "10":"v04_error_10",
  "11":"v04_error_11",
  "12":"v04_error_12",
  "13":"v04_error_13",
  "14":"v04_error_14",
  "15":"v04_error_15",
  "16":"v04_error_16",
  "17":"v04_error_17",
  "21":"v04_error_21",
  "22":"v04_error_22",
  "23":"v04_error_23",
  "24":"v04_error_24",
  "25":"v04_error_25",
  "26":"v04_error_26",
  "27":"v04_error_27",
  "28":"v04_error_28",
  "29":"v04_error_29",
  "30":"v04_error_30",
  "31":"v04_error_31",
  "32":"v04_error_32",
  "40":"v04_error_40",
  "41":"v04_error_41",
  "42":"v04_error_42",
  "43":"v04_error_43",
  "51":"v04_error_51",
  "52":"v04_error_52",
  "53":"v04_error_53",
  "54":"v04_error_54",
  "55":"v04_error_55",
  "56":"v04_error_56",
  "57":"v04_error_57",
  "58":"v04_error_58",
  "59":"v04_error_59",
  "60":"v04_error_60",
  "61":"v04_error_61",
  "62":"v04_error_62",
  "63":"v04_error_63",
  "64":"v04_error_64",
  "65":"v04_error_65",
  "66":"v04_error_66",
  "67":"v04_error_67"
}
VACUUM_05_ERROR = {
  "0":"no_error",
  "1":"v05_error_1",
  "2":"v05_error_2",
  "4":"v05_error_4",
  "6":"v05_error_6",
  "7":"v05_error_7",
  "8":"v05_error_8",
  "9":"v05_error_9",
  "10":"v05_error_10",
  "12":"v05_error_12",
  "13":"v05_error_13",
  "14":"v05_error_14",
  "15":"v05_error_15",
  "16":"v05_error_16",
  "17":"v05_error_17",
  "18":"v05_error_18",
  "19":"v05_error_19",
  "21":"v05_error_21",
  "22":"v05_error_22",
  "23":"v05_error_23",
  "24":"v05_error_24",
  "25":"v05_error_25",
  "26":"v05_error_26",
  "41":"v05_error_41",
  "42":"v05_error_42",
  "43":"v05_error_43",
  "44":"v05_error_44",
  "45":"v05_error_45",
  "46":"v05_error_46",
  "47":"v05_error_47",
  "48":"v05_error_48",
  "49":"v05_error_49",
  "50":"v05_error_50",
  "51":"v05_error_51",
  "52":"v05_error_52",
  "53":"v05_error_53",
  "54":"v05_error_54",
  "55":"v05_error_55",
  "57":"v05_error_57",
  "69":"v05_error_69",
  "70":"v05_error_70"
}
VACUUM_06_ERROR = {
  "0":"no_error",
  "1":"v06_error_1",
  "2":"v06_error_2",
  "3":"v06_error_3",
  "4":"v06_error_4",
  "5":"v06_error_5",
  "6":"v06_error_6",
  "7":"v06_error_7",
  "8":"v06_error_8",
  "9":"v06_error_9",
  "10":"v06_error_10",
  "11":"v06_error_11",
  "12":"v06_error_12",
  "13":"v06_error_13",
  "14":"v06_error_14",
  "15":"v06_error_15",
  "16":"v06_error_16",
  "17":"v06_error_17",
  "18":"v06_error_18",
  "19":"v06_error_19",
  "20":"v06_error_20",
  "21":"v06_error_21",
  "22":"v06_error_22",
  "23":"v06_error_23",
  "24":"v06_error_24",
  "25":"v06_error_25",
  "26":"v06_error_26",
  "27":"v06_error_27",
  "28":"v06_error_28",
  "29":"v06_error_29",
  "30":"v06_error_30",
  "31":"v06_error_31",
  "32":"v06_error_32",
  "33":"v06_error_33",
  "34":"v06_error_34",
  "35":"v06_error_35",
  "36":"v06_error_36",
  "37":"v06_error_37",
  "38":"v06_error_38",
  "39":"v06_error_39",
  "47":"v06_error_47",
  "48":"v06_error_48",
  "52":"v06_error_52",
  "53":"v06_error_53",
  "55":"v06_error_55",
  "58":"v06_error_58",
  "59":"v06_error_59",
  "60":"v06_error_60",
  "61":"v06_error_61",
  "62":"v06_error_62",
  "63":"v06_error_63",
  "64":"v06_error_64",
  "65":"v06_error_65",
  "66":"v06_error_66",
  "67":"v06_error_67",
  "68":"v06_error_68",
  "69":"v06_error_69",
  "70":"v06_error_70",
  "73":"v06_error_73",
  "74":"v06_error_74",
  "75":"v06_error_75",
  "76":"v06_error_76",
  "77":"v06_error_77",
  "78":"v06_error_78",
  "79":"v06_error_79",
  "80":"v06_error_80",
  "81":"v06_error_81",
  "82":"v06_error_82",
  "83":"v06_error_83",
  "84":"v06_error_84",
  "86":"v06_error_86",
  "87":"v06_error_87",
  "88":"v06_error_88",
  "89":"v06_error_89",
  "90":"v06_error_90",
  "91":"v06_error_91",
  "92":"v06_error_92",
  "93":"v06_error_93",
  "94":"v06_error_94",
  "95":"v06_error_95",
  "96":"v06_error_96",
  "97":"v06_error_97",
  "101":"v06_error_101",
  "102":"v06_error_102",
  "103":"v06_error_103",
  "104":"v06_error_104",
  "105":"v06_error_105",
  "106":"v06_error_106",
  "121":"v06_error_121",
  "122":"v06_error_122",
  "131":"v06_error_131"
}  
VACUUM_07_ERROR = {
  "0":"no_error",
  "1":"v07_error_1",
  "2":"v07_error_2",
  "3":"v07_error_3",
  "4":"v07_error_4",
  "5":"v07_error_5",
  "6":"v07_error_6",
  "7":"v07_error_7",
  "8":"v07_error_8",
  "9":"v07_error_9",
  "10":"v07_error_10",
  "11":"v07_error_11",
  "12":"v07_error_12",
  "13":"v07_error_13",
  "14":"v07_error_14",
  "15":"v07_error_15",
  "16":"v07_error_16",
  "17":"v07_error_17",
  "18":"v07_error_18",
  "19":"v07_error_19",
  "20":"v07_error_20",
  "21":"v07_error_21",
  "22":"v07_error_22",
  "23":"v07_error_23",
  "24":"v07_error_24",
  "25":"v07_error_25",
  "26":"v07_error_26",
  "27":"v07_error_27",
  "28":"v07_error_28",
  "29":"v07_error_29",
  "30":"v07_error_30",
  "31":"v07_error_31",
  "32":"v07_error_32",
  "33":"v07_error_33",
  "34":"v07_error_34",
  "35":"v07_error_35"
}  
VACUUM_08_ERROR = {
  "0":"no_error",
  "1":"v08_error_1",
  "2":"v08_error_2",
  "3":"v08_error_3",
  "4":"v08_error_4",
  "5":"v08_error_5",
  "6":"v08_error_6",
  "7":"v08_error_7",
  "8":"v08_error_8",
  "9":"v08_error_9",
  "10":"v08_error_10",
  "11":"v08_error_11",
  "12":"v08_error_12",
  "13":"v08_error_13",
  "14":"v08_error_14",
  "15":"v08_error_15",
  "16":"v08_error_16",
  "17":"v08_error_17",
  "18":"v08_error_18",
  "19":"v08_error_19",
  "20":"v08_error_20",
  "21":"v08_error_21",
  "22":"v08_error_22",
  "23":"v08_error_23",
  "24":"v08_error_24",
  "25":"v08_error_25",
  "26":"v08_error_26",
  "27":"v08_error_27",
  "28":"v08_error_28",
  "29":"v08_error_29",
  "30":"v08_error_30",
  "31":"v08_error_31",
  "32":"v08_error_32",
  "33":"v08_error_33",
  "34":"v08_error_34",
  "35":"v08_error_35",
  "36":"v08_error_36",
  "37":"v08_error_37",
  "38":"v08_error_38",
  "39":"v08_error_39",
  "40":"v08_error_40",
  "50":"v08_error_50"
}  
VACUUM_09_ERROR = {
  "0":"no_error",
  "1":"v09_error_1",
  "4":"v09_error_4",
  "5":"v09_error_5",
  "9":"v09_error_9",
  "10":"v09_error_10",
  "11":"v09_error_11",
  "12":"v09_error_12",
  "13":"v09_error_13",
  "16":"v09_error_16",
  "20":"v09_error_20",
  "21":"v09_error_21",
  "23":"v09_error_23",
  "30":"v09_error_30",
  "31":"v09_error_31",
  "32":"v09_error_32",
  "33":"v09_error_33",
  "100":"v09_error_100",
  "200":"v09_error_200"
} 
VACUUM_10_ERROR = {
  "0":"no_error",
  "1":"v10_error_1",
  "2":"v10_error_2",
  "3":"v10_error_3",
  "4":"v10_error_4",
  "5":"v10_error_5",
  "6":"v10_error_6",
  "7":"v10_error_7",
  "8":"v10_error_8",
  "9":"v10_error_9",
  "10":"v10_error_10",
  "11":"v10_error_11",
  "12":"v10_error_12",
  "13":"v10_error_13",
  "14":"v10_error_14",
  "15":"v10_error_15",
  "16":"v10_error_16",
  "17":"v10_error_17",
  "18":"v10_error_18",
  "19":"v10_error_19",
  "20":"v10_error_20",
  "21":"v10_error_21",
  "22":"v10_error_22",
  "23":"v10_error_23",
  "24":"v10_error_24",
  "25":"v10_error_25",
  "50":"v10_error_50",
  "51":"v10_error_51",
  "52":"v10_error_52",
  "53":"v10_error_53",
  "54":"v10_error_54",
  "55":"v10_error_55",
  "56":"v10_error_56"
} 
VACUUM_11_ERROR = {
  "0":"no_error",
  "2":"v11_error_2",
  "3":"v11_error_3",
  "4":"v11_error_4",
  "5":"v11_error_5",
  "7":"v11_error_7",
  "8":"v11_error_8",
  "9":"v11_error_9",
  "10":"v11_error_10",
  "11":"v11_error_11",
  "12":"v11_error_12",
  "13":"v11_error_13",
  "14":"v11_error_14",
  "15":"v11_error_15",
  "18":"v11_error_18",
  "19":"v11_error_19",
  "20":"v11_error_20",
  "21":"v11_error_21",
  "40":"v11_error_40",
  "41":"v11_error_41",
  "42":"v11_error_42",
  "43":"v11_error_43",
  "45":"v11_error_45",
  "47":"v11_error_47",
  "52":"v11_error_52",
  "55":"v11_error_55",
  "59":"v11_error_59",
  "61":"v11_error_61",
  "62":"v11_error_62",
  "63":"v11_error_63",
  "64":"v11_error_64",
  "65":"v11_error_65",
  "81":"v11_error_81",
  "82":"v11_error_82",
  "83":"v11_error_83",
  "84":"v11_error_84",
  "85":"v11_error_85",
  "88":"v11_error_88",
  "91":"v11_error_91",
  "94":"v11_error_94"
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

SENSORS_RUSCLIMATE_HUMIDIFIER = [
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
        device_class=SensorDeviceClass.CO2,
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

SENSORS_CLIMATE_200 = [
    PolarisSensorEntityDescription(
        key="sensor/pm2",
        name="pm_2_5",
        translation_key="pm2_5_sensor",
        device_class=None,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:molecule",
    ),
    PolarisSensorEntityDescription(
        key="sensor/co2",
        name="CO2",
        translation_key="co2_sensor",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
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
    PolarisSensorEntityDescription(
        key="expendables",
        name="pre_filter_retain",
        translation_key="pre_filter_retain",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:filter",
    ),
    PolarisSensorEntityDescription(
        key="time",
        name="time_to_end",
        translation_key="time_to_end_sensor_turbo",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:timer",
    ),
]

SENSORS_AIRCLEANER = [
    PolarisSensorEntityDescription(
        key="sensor/pm2",
        name="pm_2_5",
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

SENSORS_AIRCLEANER_EAP = [
    PolarisSensorEntityDescription(
        key="sensor/pm2",
        name="pm_2_5",
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
        native_unit_of_measurement=PERCENTAGE,
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
]

SENSORS_VACUUM = [
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
        key="go_area",
        name="go_area",
        translation_key="go_area",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:map-marker-radius",
    ),
    PolarisSensorEntityDescription(
        key="location_current",
        name="current_id_room",
        translation_key="current_id_room",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:map-marker-radius",
    ),
    PolarisSensorEntityDescription(
        key="battery",
        name="battery",
        translation_key="vacuum_battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=None,
#        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    PolarisSensorEntityDescription(
        key="battery_state",
        name="battery_state",
        translation_key="vacuum_battery_state",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
#        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:battery",
    ),
        PolarisSensorEntityDescription(
        key="expendables",
        name="side_brush",
        translation_key="vacuum_side_brush",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:asterisk",
    ),
    PolarisSensorEntityDescription(
        key="expendables",
        name="main_brush",
        translation_key="vacuum_main_brush",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:broom",
    ),
    PolarisSensorEntityDescription(
        key="expendables",
        name="filter",
        translation_key="vacuum_filter",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:air-filter",
    ),
    PolarisSensorEntityDescription(
        key="clean_time",
        name="last_clean_time",
        translation_key="last_clean_time",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:timer",
    ),
    PolarisSensorEntityDescription(
        key="clean_area",
        name="last_clean_area",
        translation_key="last_clean_area",
        device_class=None,
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:texture-box",
    ),
]
SENSOR_VACUUM_EXPENDABLE_MOP = [
        PolarisSensorEntityDescription(
        key="expendables",
        name="mop",
        translation_key="vacuum_mop",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:liquid-spot",
    ),
]
SENSOR_VACUUM_EXPENDABLE_DUST = [
    PolarisSensorEntityDescription(
        key="expendables",
        name="dust_container",
        translation_key="vacuum_dust_container",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:pail",
    ),
]
SENSORS_VACUUM_TOTAL_CLEAN = [
    PolarisSensorEntityDescription(
        key="program_data/1",
        name="total_clean_time",
        translation_key="total_clean_time",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:timer",
    ),
    PolarisSensorEntityDescription(
        key="program_data/1",
        name="total_clean_area",
        translation_key="total_clean_area",
        device_class=None,
        native_unit_of_measurement=UnitOfArea.SQUARE_METERS,
        state_class=SensorStateClass.MEASUREMENT,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:texture-box",
    ),
    PolarisSensorEntityDescription(
        key="program_data/1",
        name="clean_count",
        translation_key="clean_count",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
#        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:counter",
    ),
]

SENSORS_WINDOWCLEANER = [
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
        key="battery",
        name="battery",
        translation_key="vacuum_battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=None,
    ),
]
SENSORS_WATER_BOILER = [
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
        key="expendables",
        name="anode_retain",
        translation_key="anode_retain",
        device_class=None,
        native_unit_of_measurement=UnitOfTime.DAYS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        icon="mdi:sign-pole",
    ),
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
]

SENSORS_IRRIGATOR = [
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
        key="time",
        name="time_to_end",
        translation_key="time_to_end_sensor",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:timer",
    ),
    PolarisSensorEntityDescription(
        key="program_data/0",
        name="quality",
        translation_key="quality",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:equalizer",
    ),
]

SENSORS_HEATER = [
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
        key="program_data/0",
        name="current_power",
        translation_key="current_power",
        device_class=None,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=True,
        icon="mdi:equalizer",
    ),
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
]

SENSORS_AIRCONDITIONER = [
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
]

SENSORS_THERMOSTAT = [
    PolarisSensorEntityDescription(
        key="power_consume",
        name="Power consume",
        translation_key="power_consume",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_registry_enabled_default=True,
        icon="mdi:meter-electric-outline",
    ),
]

SENSORS_FAN = [
    PolarisSensorEntityDescription(
        key="battery",
        name="battery",
        translation_key="vacuum_battery",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=None,
    ),
    PolarisSensorEntityDescription(
        key="battery_state",
        name="battery_state",
        translation_key="vacuum_battery_state",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,
        icon="mdi:battery",
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
#        entity_category=EntityCategory.CONFIG,
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
    ),
]

SWITCH_CHILD_LOCK = [
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

SWITCHES_RUSCLIMATE_HUMIDIFIER = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power-standby",
    ),
    PolarisSwitchEntityDescription(
        key="backlight",
        translation_key="backlight_switch",
        entity_category=EntityCategory.CONFIG,
        name="Backlight bottom",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
    ),
    PolarisSwitchEntityDescription(
        key="night",
        translation_key="night_switch",
        entity_category=EntityCategory.CONFIG,
        name="Night light",
        mqttTopicCommand="control/night",
        mqttTopicCurrentValue="state/night",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:weather-night",
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

SWITCH_HUMIDIFIER_NIGHT = [
    PolarisSwitchEntityDescription(
        key="night",
        translation_key="night_switch",
        entity_category=EntityCategory.CONFIG,
        name="Night light",
        mqttTopicCommand="control/night",
        mqttTopicCurrentValue="state/night",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:weather-night",
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

SWITCH_HUMIDIFIER_ULTRAVIOLET = [
    PolarisSwitchEntityDescription(
        key="ultraviolet",
        translation_key="ultraviolet_switch",
        entity_category=EntityCategory.CONFIG,
        name="Ultraviolet",
        mqttTopicCommand="control/uv",
        mqttTopicCurrentValue="state/uv",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:white-balance-sunny",
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
        payload_on="2",
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

SWITCHES_CLIMATE_200 = [
    PolarisSwitchEntityDescription(
        key="damper",
        translation_key="damper_switch",
        entity_category=EntityCategory.CONFIG,
        name="Damper",
        mqttTopicCommand="control/damper",
        mqttTopicCurrentValue="state/damper",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:swap-horizontal-circle-outline",
    ),
    PolarisSwitchEntityDescription(
        key="ioniser",
        translation_key="ioniser_switch",
        entity_category=EntityCategory.CONFIG,
        name="Ioniser",
        mqttTopicCommand="control/ionizer",
        mqttTopicCurrentValue="state/ionizer",
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
        mqttTopicCommand="control/uv",
        mqttTopicCurrentValue="state/uv",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:white-balance-sunny",
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

SWITCHES_AIRCLEANER_EAP = [
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
        mqttTopicCommand="control/uv",
        mqttTopicCurrentValue="state/uv",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:white-balance-sunny",
    ),
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power-standby",
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

SWITCHES_VACUUM = [
    PolarisSwitchEntityDescription(
        key="turbo",
        translation_key="turbo_switch",
        entity_category=EntityCategory.CONFIG,
        name="mode clean carpet",
        mqttTopicCommand="control/turbo",
        mqttTopicCurrentValue="state/turbo",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:texture",
    ),
    PolarisSwitchEntityDescription(
        key="ioniser",
        translation_key="emptying_dust_switch",
        entity_category=EntityCategory.CONFIG,
        name="sbros_musora",
        mqttTopicCommand="control/ioniser",
        mqttTopicCurrentValue="state/ioniser",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:atom-variant",
    ),
    PolarisSwitchEntityDescription(
        key="volume",
        translation_key="sound_switch",
        entity_category=EntityCategory.CONFIG,
        name="Volume",
        mqttTopicCommand="control/volume",
        mqttTopicCurrentValue="state/volume",
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
    ),
    PolarisSwitchEntityDescription(
        key="stream_warm",
        translation_key="stream_warm_switch",
        entity_category=EntityCategory.CONFIG,
        name="Stream warm",
        mqttTopicCommand="control/warm_stream",
        mqttTopicCurrentValue="state/warm_stream",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:heat-wave",
    ),
]

SWITCHES_WINDOWCLEANER = [
    PolarisSwitchEntityDescription(
        key="auto_sprinkle",
        translation_key="auto_sprinkle_switch",
        entity_category=EntityCategory.CONFIG,
        name="Auto Sprinkle",
        mqttTopicCommand="control/tank",
        mqttTopicCurrentValue="state/tank",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="0",
        payload_off="1",
        icon="mdi:sprinkler-variant",
    ),
]
SWITCHES_WATER_BOILER = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
#        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power-standby",
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
    PolarisSwitchEntityDescription(
        key="smart_mode",
        translation_key="smart_mode",
        entity_category=EntityCategory.CONFIG,
        name="smart_mode",
        mqttTopicCommand="control/smart_mode",
        mqttTopicCurrentValue="state/smart_mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:water-boiler-auto",
    ),
    PolarisSwitchEntityDescription(
        key="bss_mode",
        translation_key="bss_mode",
        entity_category=EntityCategory.CONFIG,
        name="bss_mode",
        mqttTopicCommand="control/bss",
        mqttTopicCurrentValue="state/bss",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:bacteria",
    ),
]

SWITCHES_WATER_BOILER_BACKLIGHT = [
    PolarisSwitchEntityDescription(
        key="backlight",
        translation_key="backlight_bright",
        entity_category=EntityCategory.CONFIG,
        name="Backlight",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
    ),
]

SWITCHES_WATER_BOILER_NO_FROST = [
    PolarisSwitchEntityDescription(
        key="no_frost",
        translation_key="no_frost",
        entity_category=EntityCategory.CONFIG,
        name="No frost",
        mqttTopicCommand="control/keep_warm",
        mqttTopicCurrentValue="state/keep_warm",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:snowflake-off",
    ),
]

SWITCHES_IRRIGATOR = [
    PolarisSwitchEntityDescription(
        key="smart_mode",
        translation_key="smart_mode_switch",
        entity_category=EntityCategory.CONFIG,
        name="Massage",
        mqttTopicCommand="control/smart_mode",
        mqttTopicCurrentValue="state/smart_mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:hand-wave",
    ),
    PolarisSwitchEntityDescription(
        key="ioniser",
        translation_key="ozonation_switch",
        entity_category=EntityCategory.CONFIG,
        name="O3",
        mqttTopicCommand="control/ioniser",
        mqttTopicCurrentValue="state/ioniser",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:atom-variant",
    ),
    PolarisSwitchEntityDescription(
        key="power_switch",
        translation_key="power_switch",
        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power",
    ),
]

SWITCHES_HEATER = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
#        entity_category=EntityCategory.CONFIG,
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
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
        translation_key="backlight_bright",
        entity_category=EntityCategory.CONFIG,
        name="Backlight",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
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
    PolarisSwitchEntityDescription(
        key="damper_heater",
        translation_key="damper_heater",
        entity_category=EntityCategory.CONFIG,
        name="Detect open window",
        mqttTopicCommand="control/damper",
        mqttTopicCurrentValue="state/damper",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
    ),
    PolarisSwitchEntityDescription(
        key="display_off_heater",
        translation_key="display_off_heater",
        entity_category=EntityCategory.CONFIG,
        name="Auto-turn off display",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
    PolarisSwitchEntityDescription(
        key="half_power_heater",
        translation_key="half_power_heater",
        entity_category=EntityCategory.CONFIG,
        name="Half the power",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
]

SWITCHES_AIRCONDITIONER = [
    PolarisSwitchEntityDescription(
        key="turbo",
        translation_key="turbo_switch",
        entity_category=EntityCategory.CONFIG,
        name="Turbo mode",
        mqttTopicCommand="control/turbo",
        mqttTopicCurrentValue="state/turbo",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:rocket-launch",
    ),
     PolarisSwitchEntityDescription(
        key="night",
        translation_key="night_switch",
        entity_category=EntityCategory.CONFIG,
        name="Night mode",
        mqttTopicCommand="control/night",
        mqttTopicCurrentValue="state/night",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:weather-night",
    ),
     PolarisSwitchEntityDescription(
        key="self_cleaning",
        translation_key="self_cleaning",
        entity_category=EntityCategory.CONFIG,
        name="Self cleaning",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
     PolarisSwitchEntityDescription(
        key="delicate_blowing",
        translation_key="delicate_blowing",
        entity_category=EntityCategory.CONFIG,
        name="Delicate blowing",
        mqttTopicCommand="control/program_data/2",
        mqttTopicCurrentValue="state/program_data/2",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
        icon="mdi:air-filter",
    ),
     PolarisSwitchEntityDescription(
        key="eco_mode_switch",
        translation_key="eco_mode_switch",
        entity_category=EntityCategory.CONFIG,
        name="Eco mode",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
     PolarisSwitchEntityDescription(
        key="auto_heater_switch",
        translation_key="auto_heater_switch",
        entity_category=EntityCategory.CONFIG,
        name="Auto heater",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
]
SWITCHES_AIRCONDITIONER_820 = [
    PolarisSwitchEntityDescription(
        key="ioniser",
        translation_key="ioniser_switch",
        entity_category=EntityCategory.CONFIG,
        name="Ioniser",
        mqttTopicCommand="control/ionizer",
        mqttTopicCurrentValue="state/ionizer",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:atom-variant",
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
    PolarisSwitchEntityDescription(
        key="turbo",
        translation_key="turbo_switch",
        entity_category=EntityCategory.CONFIG,
        name="Turbo mode",
        mqttTopicCommand="control/turbo",
        mqttTopicCurrentValue="state/turbo",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:rocket-launch",
    ),
     PolarisSwitchEntityDescription(
        key="night",
        translation_key="night_switch",
        entity_category=EntityCategory.CONFIG,
        name="Night mode",
        mqttTopicCommand="control/night",
        mqttTopicCurrentValue="state/night",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:weather-night",
    ),
     PolarisSwitchEntityDescription(
        key="self_cleaning",
        translation_key="self_cleaning",
        entity_category=EntityCategory.CONFIG,
        name="Self cleaning",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
     PolarisSwitchEntityDescription(
        key="quiet_mode",
        translation_key="quiet_mode",
        entity_category=EntityCategory.CONFIG,
        name="Quiet mode",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
        icon="mdi:fan-minus",
    ),
     PolarisSwitchEntityDescription(
        key="eco_mode_switch",
        translation_key="eco_mode_switch",
        entity_category=EntityCategory.CONFIG,
        name="Eco mode",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
     PolarisSwitchEntityDescription(
        key="anti_fingus",
        translation_key="anti_fingus_switch",
        entity_category=EntityCategory.CONFIG,
        name="Anti-fingus",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
        icon="mdi:mushroom-off-outline",
    ),
]

SWITCHES_AIRCONDITIONER_882 = [
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
    PolarisSwitchEntityDescription(
        key="turbo",
        translation_key="turbo_switch",
        entity_category=EntityCategory.CONFIG,
        name="Turbo mode",
        mqttTopicCommand="control/turbo",
        mqttTopicCurrentValue="state/turbo",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:rocket-launch",
    ),
     PolarisSwitchEntityDescription(
        key="night",
        translation_key="night_switch",
        entity_category=EntityCategory.CONFIG,
        name="Night mode",
        mqttTopicCommand="control/night",
        mqttTopicCurrentValue="state/night",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:weather-night",
    ),
    PolarisSwitchEntityDescription(
        key="smart_mode",
        translation_key="smart_mode",
        entity_category=EntityCategory.CONFIG,
        name="smart_mode",
        mqttTopicCommand="control/smart_mode",
        mqttTopicCurrentValue="state/smart_mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:thermometer-auto",
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
]

SWITCHES_AIRCONDITIONER_856 = [
    PolarisSwitchEntityDescription(
        key="fireplace",
        translation_key="fireplace",
        entity_category=EntityCategory.CONFIG,
        name="Fireplace",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
    ),
    PolarisSwitchEntityDescription(
        key="silent_1",
        translation_key="silent_1_switch",
        entity_category=EntityCategory.CONFIG,
        name="Silent 1 mode",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
        icon="mdi:volume-medium",
    ),
     PolarisSwitchEntityDescription(
        key="silent_2",
        translation_key="silent_2_switch",
        entity_category=EntityCategory.CONFIG,
        name="Silent 2 mode",
        mqttTopicCommand="control/program_data/1",
        mqttTopicCurrentValue="state/program_data/1",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="02",
        payload_off="00",
        icon="mdi:volume-low",
    ),
]

SWITCHES_THERMOSTAT = [
    PolarisSwitchEntityDescription(
        key="power",
        translation_key="power_switch",
        name="Power",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
        icon="mdi:power-standby",
    ),
    PolarisSwitchEntityDescription(
        key="display_off_heater",
        translation_key="display_off_heater",
        entity_category=EntityCategory.CONFIG,
        name="Backlight auto off",
        mqttTopicCommand="control/backlight",
        mqttTopicCurrentValue="state/backlight",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="1",
        payload_off="0",
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
    PolarisSwitchEntityDescription(
        key="damper_heater",
        translation_key="damper_heater",
        entity_category=EntityCategory.CONFIG,
        name="Detect open window",
        mqttTopicCommand="control/damper",
        mqttTopicCurrentValue="state/damper",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
    ),
]

SWITCHES_FAN = [
    PolarisSwitchEntityDescription(
        key="volume",
        translation_key="sound_switch",
        entity_category=EntityCategory.CONFIG,
        name="Volume",
        mqttTopicCommand="control/volume",
        mqttTopicCurrentValue="state/volume",
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
    PolarisSwitchEntityDescription(
        key="effect_3d",
        translation_key="effect_3d",
        entity_category=EntityCategory.CONFIG,
        name="effect_3d",
        mqttTopicCommand="control/turbo",
        mqttTopicCurrentValue="state/turbo",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:rotate-3d",
    ),
    PolarisSwitchEntityDescription(
        key="winter_storage",
        translation_key="winter_storage",
        entity_category=EntityCategory.CONFIG,
        name="winter_storage",
        mqttTopicCommand="control/smart_mode",
        mqttTopicCurrentValue="state/smart_mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="true",
        payload_off="false",
        icon="mdi:archive",
    ),
   PolarisSwitchEntityDescription(
        key="night_light_mode",
        translation_key="night_light_mode",
        entity_category=EntityCategory.CONFIG,
        name="Night light",
        mqttTopicCommand="control/mode",
        mqttTopicCurrentValue="state/mode",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="6",
        payload_off="0",
    ),
]

SWITCH_ROTATION_FAN = [
    PolarisSwitchEntityDescription(
        key="auto_rotation",
        translation_key="auto_rotation",
        entity_category=EntityCategory.CONFIG,
        name="Auto rotation",
        mqttTopicCommand="control/program_data/0",
        mqttTopicCurrentValue="state/program_data/0",
        device_class=SwitchDeviceClass.SWITCH,
        payload_on="01",
        payload_off="00",
        icon="mdi:swap-horizontal",
    ),
]

@dataclass
class PolarisWaterHeaterEntityDescription(WaterHeaterEntityDescription):                                                              # breaks_in_ha_version="2026.1"

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
#        entity_category=EntityCategory.CONFIG,
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

WATER_BOILERS = [
    PolarisWaterHeaterEntityDescription(
        key="water_boiler",
        translation_key="water_boiler",
        name="water_boiler",
        mqttTopicCommandMode="control/mode",
        mqttTopicCommandTemperature="control/temperature",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCurrentTemperature="state/sensor/temperature",
        mqttTopicTargetTemperature="state/temperature",
        payload_on="1",
        payload_off="0",
#        icon="mdi:water-boiler",
        min_temp=30,
        max_temp=75,
        mode="off",
        operation_list = {"off": "0", "performance": "1", "electric": "2", "heat_pump": "3", "eco": "6"}
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
        max_humidity = 80,
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

NUMBER_RUSCLIMATE_HUMIDIFIER = [
    PolarisNumberEntityDescription(
        key="speed",
        name="Evaporation rate",
        translation_key="evaporation_rate",
        mqttTopicCurrent = "state/speed",
        mqttTopicCommand = "control/speed",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        native_unit_of_measurement=None,
        entity_registry_enabled_default=True,
        native_max_value=3,
        native_min_value=1,
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

NUMBERS_IRRIGATOR = [
    PolarisNumberEntityDescription(
        key="speed_irrigator",
        name="speed_irrigator",
        translation_key="speed_irrigator",
        mqttTopicCurrent = "state/speed",
        mqttTopicCommand = "control/speed",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=10,
        native_min_value=1,
        native_step=1,
        native_value=1,
        mode="slider",
        icon="mdi:speedometer",
    ),
]

NUMBERS_HEATER = [
    PolarisNumberEntityDescription(
        key="temperature_difference_eco",
        name="ECO difference temperature",
        translation_key="temperature_difference_eco",
        mqttTopicCurrent = "state/program_data/2",
        mqttTopicCommand = "control/program_data/2",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=True,
        native_max_value=7,
        native_min_value=3,
        native_step=1,
        native_value=3,
        mode="slider",
    ),
    PolarisNumberEntityDescription(
        key="temperature_difference_antifrost",
        name="Anti frost difference temperature",
        translation_key="temperature_difference_antifrost",
        mqttTopicCurrent = "state/program_data/3",
        mqttTopicCommand = "control/program_data/3",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_registry_enabled_default=True,
        native_max_value=7,
        native_min_value=3,
        native_step=1,
        native_value=3,
        mode="slider",
    ),
]

NUMBERS_THERMOSTAT = [
    PolarisNumberEntityDescription(
        key="bright_backlight",
        name="Bright backlight",
        translation_key="bright_backlight",
        mqttTopicCurrent = "state/program_data/0",
        mqttTopicCommand = "control/program_data/0",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.POWER_FACTOR,
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=True,
        native_max_value=100,
        native_min_value=20,
        native_step=10,
        native_value=100,
        mode="slider",
        icon="mdi:brightness-percent",
    ),
    PolarisNumberEntityDescription(
        key="power_cable",
        name="Power cable",
        translation_key="power_cable",
        mqttTopicCurrent = "state/program_data/9",
        mqttTopicCommand = "control/program_data/9",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        entity_registry_enabled_default=True,
        native_max_value=3600,
        native_min_value=50,
        native_step=25,
        native_value=50,
        mode="box",
    ),
]

NUMBERS_FAN = [
    PolarisNumberEntityDescription(
        key="fan_tilt",
        name="tilt",
        translation_key="fan_tilt",
        mqttTopicCurrent = "state/program_data/0",
        mqttTopicCommand = "control/program_data/0",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=2,
        native_min_value=0,
        native_step=1,
        native_value=2,
        mode="slider",
        icon="mdi:arrow-split-horizontal",
    ),
    PolarisNumberEntityDescription(
        key="fan_turn",
        name="turn",
        translation_key="fan_turn",
        mqttTopicCurrent = "state/program_data/0",
        mqttTopicCommand = "control/program_data/0",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=True,
        native_max_value=2,
        native_min_value=0,
        native_step=1,
        native_value=2,
        mode="slider",
        icon="mdi:arrow-split-vertical",
    ),
    PolarisNumberEntityDescription(
        key="fan_auto_off",
        name="auto_off",
        translation_key="fan_auto_off",
        mqttTopicCurrent = "state/program_data/4",
        mqttTopicCommand = "control/program_data/4",
        entity_category=EntityCategory.CONFIG,
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        entity_registry_enabled_default=True,
        native_max_value=24,
        native_min_value=1,
        native_step=1,
        native_value=1,
        mode="box",
        icon="mdi:timer"
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

SELECT_AIRCLEANER_EAP = [
    PolarisSelectEntityDescription(
        key="select_night_backlight",
        name="Night backlight",
        translation_key="select_night_backlight",
        mqttTopicCurrentMode="state/program_data/0",
        mqttTopicCommandMode="control/program_data/0",
        options={
          "off": 0,
          "all_on": 1,
          "high_on": 2,
          "mid_on": 3,
          "low_on": 4,
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
    )
]

SELECT_AIRCONDITIONER_NIGHT_MODE = [
    PolarisSelectEntityDescription(
        key="select_night_mode",
        name="Night mode",
        translation_key="select_night_mode",
        mqttTopicCurrentMode="state/night",
        mqttTopicCommandMode="control/night",
        options={
          "off": 0,
          "standard": 1,
          "child": 2,
          "teen": 3,
          "the_aged": 4,
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:weather-night",
    )
]

SELECT_AIRCONDITIONER_SWING_HORIZONTAL  = [
    PolarisSelectEntityDescription(
        key="select_swing_horizontal",
        name="Swing horizontal",
        translation_key="select_swing_horizontal",
        mqttTopicCurrentMode="state/program_data/3",
        mqttTopicCommandMode="control/program_data/3",
        options={
          "off": "00",
          "top": "01",
          "high": "02",
          "middle": "03",
          "low": "04",
          "bottom": "05",
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:arrow-split-horizontal",
    )
]

SELECT_AIRCONDITIONER_SWING_VERTICAL  = [
    PolarisSelectEntityDescription(
        key="select_swing_vertical",
        name="Swing vertical",
        translation_key="select_swing_vertical",
        mqttTopicCurrentMode="state/program_data/4",
        mqttTopicCommandMode="control/program_data/4",
        options={
          "off": "00",
          "left": "01",
          "center-left": "02",
          "center": "03",
          "center-right": "04",
          "right": "05",
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:arrow-split-vertical",
    )
]

SELECT_AIRCONDITIONER_COMPRESSOR_POWER = [
    PolarisSelectEntityDescription(
        key="select_compressor_power",
        name="Compressor power",
        translation_key="select_compressor_power",
        mqttTopicCurrentMode="state/program_data/1",
        mqttTopicCommandMode="control/program_data/1",
        options={
          "low": "00",
          "middle": "01",
          "high": "02"
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
        icon="mdi:lightning-bolt",
    )
]

SELECT_VACUUM = [
    PolarisSelectEntityDescription(
        key="select_mode_vacuum",
        name="select_mode_vacuum",
        translation_key="select_mode_vacuum",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCommandMode="control/mode",
        options={"mode0": 0, "mode1": 1, "mode2": 2, "mode3": 3, "mode4": 4, "mode5": 5},
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:vacuum",
        entity_registry_enabled_default=True,
    ),
    PolarisSelectEntityDescription(
        key="select_room",
        name="select_room",
        translation_key="select_room",
        mqttTopicCurrentMode="control/room",
        mqttTopicCommandMode="control/room",
        options={
          "all_rooms": {"id": "00", "coordinate": []}
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:broom",
        entity_registry_enabled_default=True,
    ),
    PolarisSelectEntityDescription(
        key="vacuum_tank",
        name="vacuum_tank",
        translation_key="vacuum_tank",
        mqttTopicCurrentMode="state/tank",
        mqttTopicCommandMode="control/tank",
        options={"low": "0", "high": "1"},
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:water",
        entity_registry_enabled_default=True,
    )
]

SELECT_WINDOWCLEANER = [
    PolarisSelectEntityDescription(
        key="select_mode_windowcleaner",
        name="Mode",
        translation_key="select_mode_windowcleaner",
        mqttTopicCurrentMode="state/mode",
        mqttTopicCommandMode="control/mode",
        options={"off": "0", "up": "2", "left": "3", "right": "4"},
        device_class=None,
        entity_registry_enabled_default=True,
    ),
]
SELECT_IRRIGATOR = [
    PolarisSelectEntityDescription(
        key="select_irrigator",
        name="Preset",
        translation_key="select_irrigator",
        mqttTopicCurrentMode="state/program_data/1",
        mqttTopicCommandMode="control/",
        options={
          "preset1": 1,
          "preset2": 2,
          "preset3": 3,
        },
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:format-list-numbered",
        entity_registry_enabled_default=True,
    )
]

SELECT_FAN = [
    PolarisSelectEntityDescription(
        key="select_fan_light",
        name="light",
        translation_key="select_fan_light",
        mqttTopicCurrentMode="state/amount",
        mqttTopicCommandMode="control/amount",
        options={"off": "0", "half": "1", "full": "2"},
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        icon="mdi:lightbulb-on",
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

LIGHTS_DOUBLE = [
    PolarisLightEntityDescription(
        key="night_up",
        name="night_up",
        translation_key="night_light_up",
        mqttTopicCurrentColor="state/backlight",
        mqttTopicCommandColor="control/backlight",
        mqttTopicCurrentState="state/backlight",
        mqttTopicCommandState="control/backlight",
        entity_category=EntityCategory.CONFIG,
        device_class=None,
        entity_registry_enabled_default=True,
    ),
    PolarisLightEntityDescription(
        key="night_down",
        name="night_down",
        translation_key="night_light_down",
        mqttTopicCurrentColor="state/backlight",
        mqttTopicCommandColor="control/backlight",
        mqttTopicCurrentState="state/backlight",
        mqttTopicCommandState="control/backlight",
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

BINARYSENSOR_THERMOSTAT = [
    PolarisBinarySensorEntityDescription(
        key="heating",
        name="Heating",
        translation_key="heating_binary_sensor",
        mqttTopicStatus="state/program_data/10",
        device_class=BinarySensorDeviceClass.HEAT,
        entity_registry_enabled_default=True,
        icon="mdi:heat-wave",
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

BUTTON_CLIMATES_200 = [
    PolarisButtonEntityDescription(
        key="button_reset_filter",
        name="button_reset_filter",
        translation_key="button_reset_filter",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[0,100]",
        icon="mdi:filter",
    ),
    PolarisButtonEntityDescription(
        key="button_reset_prefilter",
        name="button_reset_prefilter",
        translation_key="button_reset_prefilter",
        mqttTopicCommand="control/expendables",
        device_class=None,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        payloads="[100,0]",
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
    mqttTopicCommandSwingMode: str | None = None
    mqttTopicStateSwingMode: str | None = None
    payload_on: str | None = None
    payload_off: str | None = None
    min_temp: int | None = None
    max_temp: int | None = None
    temp_step: int | None = None
    swing_mode: str | None = None
    swing_modes: str | None = None


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

CLIMATES_200 = [
    PolarisClimateEntityDescription(
        name = "Climate",
        key = "climate",
        translation_key = "climate",
        fan_mode = "off",
        fan_modes = {"off": "0", "1_speed": "1", "2_speed": "2", "3_speed": "3", "4_speed": "4", "5_speed": "5", "6_speed": "6", "7_speed": "7", "8_speed": "8", "9_speed": "9"},
        preset_mode = "auto",
        preset_modes = {"hands": "1", "auto": "2", "night": "3", "turbo": "4"},
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
        payload_on = "2",
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

AIRCLEANER_EAP = [
    PolarisClimateEntityDescription(
        name = "Aircleaner",
        key = "aircleaner",
        translation_key = "aircleaner",
        fan_mode = "low",
        fan_modes = {"off": "0", "low": "1", "medium": "2", "high": "3", "top": "4"},
        preset_mode = "auto",
        preset_modes = {"auto": "1", "night": "2", "hands": "3"},
        hvac_modes = [HVACMode.OFF, HVACMode.DRY],
        supported_features = (
            ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        mqttTopicStateFanMode = "state/fan_speed",
        mqttTopicCommandFanMode = "control/fan_speed",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        payload_on = "1",
        payload_off = "0",
        device_class = None,
    )
]

CLIMATES_HEATER = [
    PolarisClimateEntityDescription(
        name = "Heater",
        key = "heater",
        translation_key = "heater",
        fan_mode = "auto",
        fan_modes = {"auto": "0", "10_percent": "1", "20_percent": "2", "30_percent": "3", "40_percent": "4", "50_percent": "5", "60_percent": "6", "70_percent": "7", "80_percent": "8", "90_percent": "9", "100_percent": "10"},
        preset_mode = "comfort",
        preset_modes = {"comfort": "1", "eco": "2", "away": "3"},
        hvac_modes = [HVACMode.OFF, HVACMode.HEAT],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
#            | ClimateEntityFeature.AUX_HEAT
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
        payload_on = "1",
        payload_off = "0",
        min_temp = 5,
        max_temp = 35,
        temp_step = 1,
        device_class = None,
    )
]

CLIMATES_AIRCONDITIONER = [
    PolarisClimateEntityDescription(
        name = "Conditioner",
        key = "conditioner",
        translation_key = "conditioner",
        fan_mode = "auto",
        fan_modes = {"auto": "0", "min": "1", "low": "2", "middle": "3", "high": "4", "max": "5"},
        preset_mode = "auto",
        preset_modes = {"auto": "1", "cooling": "2", "defrosting": "3", "heating": "4", "fan": "5"},
        hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.FAN_ONLY, HVACMode.DRY, HVACMode.AUTO],
        swing_mode = "off",
        swing_modes = {"off": "0", "both": "1", "vertical": "2", "horizontal": "3"},
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.SWING_MODE
        ),
        mqttTopicStateTemperature = "state/temperature",
        mqttTopicCommandTemperature = "control/temperature",
        mqttTopicCurrentTemperature = "state/sensor/temperature",
        mqttTopicStateFanMode = "state/speed",
        mqttTopicCommandFanMode = "control/speed",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        mqttTopicCommandSwingMode = "control/program_data/0",
        mqttTopicStateSwingMode = "state/program_data/0",
        payload_on = "1",
        payload_off = "0",
        min_temp = 16,
        max_temp = 30,
        temp_step = 1,
        device_class = None,
    )
]

CLIMATES_THERMOSTAT = [
    PolarisClimateEntityDescription(
        name = "Thermostat",
        key = "thermostat",
        translation_key = "thermostat",
        preset_mode = "comfort",
        preset_modes = {"eco": "1", "comfort": "2", "turbo": "3", "antifrost": "4", "schedule": "5", "vacation": "6", "manual": "7"},
        hvac_modes = [HVACMode.OFF, HVACMode.HEAT],
        supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        ),
        mqttTopicStateTemperature = "state/temperature",
        mqttTopicCommandTemperature = "control/temperature",
        mqttTopicCurrentTemperature = "state/sensor/temperature",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
        payload_on = "1",
        payload_off = "0",
        min_temp = 5,
        max_temp = 45,
        temp_step = 1,
        device_class = None,
    )
]

@dataclass
class PolarisVacuumEntityDescription(ClimateEntityDescription):

    fan_mode: str | None = None
    fan_modes: str | None = None
    mqttTopicCommandMode: str | None = None
    mqttTopicCurrentMode: str | None = None
    mqttTopicCommandTank: str | None = None
    mqttTopicStateTank: str | None = None
    mqttTopicStateFanMode: str | None = None
    mqttTopicCommandFanMode: str | None = None
    mqttTopicCommandFindMe: str | None = None
    mqttTopicCommandGoArea: str | None = None

VACUUM = [
    PolarisVacuumEntityDescription(
        name = "Vacuum",
        key = "vacuum",
        translation_key = "vacuum",
        mqttTopicCommandMode = "control/mode",
        mqttTopicCurrentMode = "state/mode",
        mqttTopicStateFanMode = "state/suction",
        mqttTopicCommandFanMode = "control/suction",
        mqttTopicCommandTank = "control/tank",
        mqttTopicStateTank = "state/tank",
        mqttTopicCommandFindMe = "control/find_me",
        mqttTopicCommandGoArea = "control/go_area",
        device_class = None,
    )
]


@dataclass
class PolarisImageEntityDescription(ImageEntityDescription):

    mqttTopicCommandGoArea: str | None = None

IMAGE = [
    PolarisImageEntityDescription(
        name = "Image",
        key = "image",
        translation_key = "image",
        mqttTopicCommandGoArea = "control/go_area",
        device_class = None,
    )
]


@dataclass
class PolarisFanEntityDescription(FanEntityDescription):

#    current_direction: str | None = None
#    oscillating: bool | None = None
#    percentage: str | None = None
    preset_mode: str | None = None
    preset_modes: list[str] | None = None
    percentage_list: list[str] | None = None
    supported_features:  int | None = None
    mqttTopicCommandFanMode: str | None = None
    mqttTopicCurrentFanMode: str | None = None
    mqttTopicCommandPower: str | None = None
    mqttTopicCurrentPresetMode: str | None = None
    mqttTopicCommandPresetMode: str | None = None

FANS = [
    PolarisFanEntityDescription(
        name = "fan",
        key = "fan",
        translation_key = "fan",
        percentage_list = [1,2,3,4,5,6,7,8,9],
        preset_mode = "passive",
        preset_modes = {"off": "0", "standart": "1", "breeze": "2", "night": "3", "eco": "4", "auto": "5"},
        supported_features = (
            FanEntityFeature.SET_SPEED
            | FanEntityFeature.PRESET_MODE
            | FanEntityFeature.TURN_OFF
            | FanEntityFeature.TURN_ON
        ),
        mqttTopicCurrentFanMode = "state/speed",
        mqttTopicCommandFanMode = "control/speed",
        mqttTopicCommandPower = "control/mode",
        mqttTopicCurrentPresetMode = "state/mode",
        mqttTopicCommandPresetMode = "control/mode",
    )
]