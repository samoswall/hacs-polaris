"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable
import copy

from homeassistant.components import mqtt
from homeassistant.components.switch import DOMAIN, SwitchEntity
#from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import async_get as async_get_dev_reg

from .common import PolarisBaseEntity
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    SWITCHES_ALL_DEVICES,
    SWITCH_KETTLE_BACKLIGHT,
    SWITCH_HUMIDIFIER_BACKLIGHT,
    SWITCH_HUMIDIFIER_NIGHT,
    SWITCH_HUMIDIFIER_IONISER,
    SWITCH_HUMIDIFIER_WARM_STREAM,
    SWITCH_HUMIDIFIER_ULTRAVIOLET,
    SWITCHES_RUSCLIMATE_HUMIDIFIER,
    SWITCHES_COOKER,
    SWITCHES_COFFEEMAKER,
    SWITCHES_COFFEEMAKER_ROG,
    SWITCHES_CLIMATE,
    SWITCHES_CLIMATE_200,
    SWITCHES_AIRCLEANER,
    SWITCHES_AIRCLEANER_EAP,
    SWITCHES_VACUUM,
    SWITCHES_WATER_BOILER,
    SWITCHES_WATER_BOILER_NO_FROST,
    SWITCHES_WATER_BOILER_BACKLIGHT,
    SWITCHES_IRRIGATOR,
    SWITCHES_HEATER,
    SWITCHES_AIRCONDITIONER,
    SWITCHES_AIRCONDITIONER_820,
    SWITCHES_AIRCONDITIONER_882,
    SWITCHES_AIRCONDITIONER_856,
    SWITCHES_THERMOSTAT,
    SWITCHES_FAN,
    SWITCH_ROTATION_FAN,
    SWITCHES_WINDOWCLEANER,
    SWITCH_CHILD_LOCK,
    PolarisSwitchEntityDescription,
    POLARIS_KETTLE_TYPE,
    POLARIS_KETTLE_WITH_WEIGHT_TYPE,
    POLARIS_KETTLE_WITH_BACKLIGHT_TYPE,
    POLARIS_HUMIDDIFIER_TYPE,
    POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE,
    POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE,
    POLARIS_COOKER_TYPE,
    POLARIS_COFFEEMAKER_TYPE,
    POLARIS_COFFEEMAKER_ROG_TYPE,
    POLARIS_CLIMATE_TYPE,
    POLARIS_AIRCLEANER_TYPE,
    POLARIS_AIRCLEANER_EAP_TYPE,
    POLARIS_VACUUM_TYPE,
    POLARIS_BOILER_TYPE,
    POLARIS_IRRIGATOR_TYPE,
    POLARIS_HEATER_TYPE,
    POLARIS_AIRCONDITIONER_TYPE,
    POLARIS_THERMOSTAT_TYPE,
    POLARIS_FAN_TYPE,
    POLARIS_VACUUM_SWITCH_CHILD_LOCK,
    POLARIS_VACUUM_SWITCH_VOLUME,
    POLARIS_VACUUM_SWITCH_TURBO,
    POLARIS_VACUUM_SWITCH_IONISER,
    POLARIS_VACUUM_SWITCH_STREAM_WARM,
    POLARIS_VACUUM_SWITCH_BACKLIGHT,
    POLARIS_WINDOWCLEANER_TYPE,
    VACUUM_SWITCH_01_TURBO,
    VACUUM_SWITCH_02_TURBO,
    VACUUM_SWITCH_03_TURBO
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

async def async_setup_entry(
    hass: HomeAssistant, config: ConfigEntry, async_add_entities: AddEntitiesCallback,
) -> None:
    integrationUniqueID = config.unique_id
    mqtt_root = config.data[MQTT_ROOT_TOPIC]
    device_id = config.data["DEVICEID"]
    device_type = config.data[DEVICETYPE]
    device_prefix_topic = config.data["DEVPREFIXTOPIC"]
    switchList = []

    if (device_type in POLARIS_KETTLE_TYPE) or (device_type in POLARIS_KETTLE_WITH_WEIGHT_TYPE):
        # Create sensors for all devices
        SWITCHES_ALL_DEVICES_LC = copy.deepcopy(SWITCHES_ALL_DEVICES)
        for description in SWITCHES_ALL_DEVICES_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if device_type in POLARIS_KETTLE_WITH_BACKLIGHT_TYPE:
        # Create sensors for backlight devices
        SWITCH_KETTLE_BACKLIGHT_LC = copy.deepcopy(SWITCH_KETTLE_BACKLIGHT)
        for description in SWITCH_KETTLE_BACKLIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HUMIDDIFIER_TYPE):
      if device_type == "881":
        SWITCHES_RUSCLIMATE_HUMIDIFIER_LC = copy.deepcopy(SWITCHES_RUSCLIMATE_HUMIDIFIER)
        for description in SWITCHES_RUSCLIMATE_HUMIDIFIER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
      else:
        # Create switches for all devices
        SWITCHES_ALL_DEVICES_LC = copy.deepcopy(SWITCHES_ALL_DEVICES)
        for description in SWITCHES_ALL_DEVICES_LC:
          if (device_type != "835" or description.translation_key != "child_lock_switch"):
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
        if (device_type == "158"):
            SWITCH_HUMIDIFIER_NIGHT_LC = copy.deepcopy(SWITCH_HUMIDIFIER_NIGHT)
            for description in SWITCH_HUMIDIFIER_NIGHT_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
        else:
            SWITCH_HUMIDIFIER_BACKLIGHT_LC = copy.deepcopy(SWITCH_HUMIDIFIER_BACKLIGHT)
            for description in SWITCH_HUMIDIFIER_BACKLIGHT_LC:
              if (device_type != "835" or description.translation_key != "backlight_switch"):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_HUMIDDIFIER_WITH_IONISER_TYPE):
        # Create switch ioniser for humidifiers
        SWITCH_HUMIDIFIER_IONISER_LC = copy.deepcopy(SWITCH_HUMIDIFIER_IONISER)
        for description in SWITCH_HUMIDIFIER_IONISER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_HUMIDDIFIER_WITH_WARM_STREAM_TYPE):
        # Create switch stream warm for humidifiers
        SWITCH_HUMIDIFIER_WARM_STREAM_LC = copy.deepcopy(SWITCH_HUMIDIFIER_WARM_STREAM)
        for description in SWITCH_HUMIDIFIER_WARM_STREAM_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in {"835","157"}):
        # Create switch stream warm for humidifiers
        SWITCH_HUMIDIFIER_ULTRAVIOLET_LC = copy.deepcopy(SWITCH_HUMIDIFIER_ULTRAVIOLET)
        for description in SWITCH_HUMIDIFIER_ULTRAVIOLET_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COOKER_TYPE):
        # Create switches for cooker
        SWITCHES_COOKER_LC = copy.deepcopy(SWITCHES_COOKER)
        for description in SWITCHES_COOKER_LC:
          if (device_type not in ("290","291","292") or description.translation_key != "keepwarm_switch"):
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
        if (device_type in ("290","291","292")):
            SWITCH_KETTLE_BACKLIGHT_LC = copy.deepcopy(SWITCH_KETTLE_BACKLIGHT)
            for description in SWITCH_KETTLE_BACKLIGHT_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_COFFEEMAKER_TYPE):
        # Create switches for coffeemaker
        SWITCHES_COFFEEMAKER_LC = copy.deepcopy(SWITCHES_COFFEEMAKER)
        for description in SWITCHES_COFFEEMAKER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_COFFEEMAKER_ROG_TYPE):
        # Create switches for coffeemaker
        SWITCHES_COFFEEMAKER_ROG_LC = copy.deepcopy(SWITCHES_COFFEEMAKER_ROG)
        for description in SWITCHES_COFFEEMAKER_ROG_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_CLIMATE_TYPE):
        # Create switches for climate
        SWITCHES_CLIMATE_LC = copy.deepcopy(SWITCHES_CLIMATE)
        for description in SWITCHES_CLIMATE_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
        if (device_type == "859"):
            SWITCHES_CLIMATE_200_LC = copy.deepcopy(SWITCHES_CLIMATE_200)
            for description in SWITCHES_CLIMATE_200_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_AIRCLEANER_TYPE):
        # Create switches for all devices
        SWITCHES_ALL_DEVICES_LC = copy.deepcopy(SWITCHES_ALL_DEVICES)
        for description in SWITCHES_ALL_DEVICES_LC:
            if (device_type not in ("140", "172") or description.translation_key != "child_lock_switch"):
              description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
              description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
              description.device_prefix_topic = device_prefix_topic
              switchList.append(
                  PolarisSwitch(
                      description=description,
                      device_friendly_name=device_id,
                      mqtt_root=mqtt_root,
                      device_type=device_type,
                      device_id=device_id
                  )
              )
        if (device_type in ("140", "172")):
            SWITCH_HUMIDIFIER_BACKLIGHT_LC = copy.deepcopy(SWITCH_HUMIDIFIER_BACKLIGHT)
            for description in SWITCH_HUMIDIFIER_BACKLIGHT_LC:
              if (device_type != "835" or description.translation_key != "backlight_switch"):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
            SWITCH_HUMIDIFIER_IONISER_LC = copy.deepcopy(SWITCH_HUMIDIFIER_IONISER)
            for description in SWITCH_HUMIDIFIER_IONISER_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
        else:
            SWITCHES_AIRCLEANER_LC = copy.deepcopy(SWITCHES_AIRCLEANER)
            for description in SWITCHES_AIRCLEANER_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_AIRCLEANER_EAP_TYPE):
        SWITCHES_AIRCLEANER_EAP_LC = copy.deepcopy(SWITCHES_AIRCLEANER_EAP)
        for description in SWITCHES_AIRCLEANER_EAP_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_VACUUM_TYPE):
        # Create switches for vacuum
        SWITCHES_VACUUM_LC = copy.deepcopy(SWITCHES_VACUUM)
        for description in SWITCHES_VACUUM_LC:
            if ( (int(device_type) in POLARIS_VACUUM_SWITCH_CHILD_LOCK and description.translation_key == "child_lock_switch")
               | (int(device_type) in POLARIS_VACUUM_SWITCH_VOLUME and description.translation_key == "sound_switch")
               | (int(device_type) in POLARIS_VACUUM_SWITCH_TURBO and description.translation_key == "turbo_switch")
               | (int(device_type) in POLARIS_VACUUM_SWITCH_IONISER and description.translation_key == "emptying_dust_switch")
               | (int(device_type) in POLARIS_VACUUM_SWITCH_STREAM_WARM and description.translation_key == "stream_warm_switch")
               | (int(device_type) in POLARIS_VACUUM_SWITCH_BACKLIGHT and description.translation_key == "backlight_switch") ): 
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                if (int(device_type) in VACUUM_SWITCH_01_TURBO and description.translation_key == "turbo_switch"):
                    description.translation_key = "wet_dry_switch"
                if (int(device_type) in VACUUM_SWITCH_02_TURBO and description.translation_key == "turbo_switch"):
                    description.translation_key = "carpet_booster_switch"
                if (int(device_type) in VACUUM_SWITCH_03_TURBO and description.translation_key == "turbo_switch"):
                    description.translation_key = "carpet_cleaning_switch"
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in POLARIS_BOILER_TYPE):
        # Create switches for boiler
        SWITCHES_WATER_BOILER_LC = copy.deepcopy(SWITCHES_WATER_BOILER)
        for description in SWITCHES_WATER_BOILER_LC:
            if (device_type not in {"802","807","833","844","877"} or description.translation_key != "child_lock_switch") and (device_type not in {"807","833"} or description.translation_key != "smart_mode"):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in ("844","815","877","860")):
        # Create switches for boiler bright 50%
        SWITCHES_WATER_BOILER_BACKLIGHT_LC = copy.deepcopy(SWITCHES_WATER_BOILER_BACKLIGHT)
        for description in SWITCHES_WATER_BOILER_BACKLIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            if device_type == "815":
                description.translation_key = "backlight_switch"
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type == "802"):
        # Create switches for boiler no frost
        SWITCHES_WATER_BOILER_NO_FROST_LC = copy.deepcopy(SWITCHES_WATER_BOILER_NO_FROST)
        for description in SWITCHES_WATER_BOILER_NO_FROST_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_IRRIGATOR_TYPE):
        # Create switches for irrigator
        SWITCHES_IRRIGATOR_LC = copy.deepcopy(SWITCHES_IRRIGATOR)
        for description in SWITCHES_IRRIGATOR_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if ((device_type in POLARIS_HEATER_TYPE) and (device_type not in ("814","849"))):
        # Create switches for heater
        SWITCHES_HEATER_LC = copy.deepcopy(SWITCHES_HEATER)
        for description in SWITCHES_HEATER_LC:
            if (device_type not in {"806","847"} or description.translation_key != "half_power_heater"):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in ("814","849")):
        SWITCH_CHILD_LOCK_LC = copy.deepcopy(SWITCH_CHILD_LOCK)
        for description in SWITCH_CHILD_LOCK_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
        SWITCH_KETTLE_BACKLIGHT_LC = copy.deepcopy(SWITCH_KETTLE_BACKLIGHT)
        for description in SWITCH_KETTLE_BACKLIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type == "820"):
        SWITCHES_AIRCONDITIONER_820_LC = copy.deepcopy(SWITCHES_AIRCONDITIONER_820)
        for description in SWITCHES_AIRCONDITIONER_820_LC:
            if (device_type not in ("868","821") or description.translation_key not in ("ioniser_switch", "self_cleaning", "anti_fingus_switch")):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type in ("813","815","857")):
        SWITCHES_AIRCONDITIONER_LC = copy.deepcopy(SWITCHES_AIRCONDITIONER)
        for description in SWITCHES_AIRCONDITIONER_LC:
            if (device_type not in ("815","857") or description.translation_key != "delicate_blowing") and (device_type != "857" or description.translation_key not in ("self_cleaning", "turbo_switch")):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
        if device_type == "857":
            # Create backlight
            SWITCH_KETTLE_BACKLIGHT_LC = copy.deepcopy(SWITCH_KETTLE_BACKLIGHT)
            for description in SWITCH_KETTLE_BACKLIGHT_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if device_type in ("815", "856"):
        SWITCH_HUMIDIFIER_IONISER_LC = copy.deepcopy(SWITCH_HUMIDIFIER_IONISER)
        for description in SWITCH_HUMIDIFIER_IONISER_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if device_type in ("808","882","821","868","860","856"):
        SWITCHES_AIRCONDITIONER_882_LC = copy.deepcopy(SWITCHES_AIRCONDITIONER_882)
        for description in SWITCHES_AIRCONDITIONER_882_LC:
            if (device_type not in ("808","860","856") or description.translation_key not in ("backlight_switch", "smart_mode", "sound_switch")):
                if (device_type not in ("821","868") or description.translation_key not in ("turbo_switch", "night_switch", "sound_switch")):
                  if (device_type != "856" or description.translation_key != "night_switch"):
                    description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                    description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                    description.device_prefix_topic = device_prefix_topic
                    switchList.append(
                        PolarisSwitch(
                            description=description,
                            device_friendly_name=device_id,
                            mqtt_root=mqtt_root,
                            device_type=device_type,
                            device_id=device_id
                        )
                    )
    if device_type in ("856","860"):
        SWITCHES_AIRCONDITIONER_LC = copy.deepcopy(SWITCHES_AIRCONDITIONER)
        for description in SWITCHES_AIRCONDITIONER_LC:
            if description.translation_key in ("auto_heater_switch", "eco_mode_switch"):
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
        if device_type == "856":
            SWITCHES_AIRCONDITIONER_856_LC = copy.deepcopy(SWITCHES_AIRCONDITIONER_856)
            for description in SWITCHES_AIRCONDITIONER_856_LC:
                description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
                description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
                description.device_prefix_topic = device_prefix_topic
                switchList.append(
                    PolarisSwitch(
                        description=description,
                        device_friendly_name=device_id,
                        mqtt_root=mqtt_root,
                        device_type=device_type,
                        device_id=device_id
                    )
                )
    if (device_type == "851"):
        SWITCH_HUMIDIFIER_NIGHT_LC = copy.deepcopy(SWITCH_HUMIDIFIER_NIGHT)
        for description in SWITCH_HUMIDIFIER_NIGHT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_THERMOSTAT_TYPE):
        SWITCHES_THERMOSTAT_LC = copy.deepcopy(SWITCHES_THERMOSTAT)
        for description in SWITCHES_THERMOSTAT_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_FAN_TYPE):
        SWITCHES_FAN_LC = copy.deepcopy(SWITCHES_FAN)
        for description in SWITCHES_FAN_LC:
          if (device_type != "248" or description.translation_key not in ("effect_3d", "winter_storage", "night_light_mode")):
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type == "248"):
        SWITCH_ROTATION_FAN_LC = copy.deepcopy(SWITCH_ROTATION_FAN)
        for description in SWITCH_ROTATION_FAN_LC:
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    if (device_type in POLARIS_WINDOWCLEANER_TYPE):
        for description in copy.deepcopy(SWITCHES_WINDOWCLEANER):
            description.mqttTopicCommand = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommand}"
            description.mqttTopicCurrentValue = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentValue}"
            description.device_prefix_topic = device_prefix_topic
            switchList.append(
                PolarisSwitch(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id
                )
            )
    async_add_entities(switchList, update_before_add=True)

class PolarisSwitch(PolarisBaseEntity, SwitchEntity):
    entity_description: PolarisSwitchEntityDescription
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisSwitchEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None
    ) -> None:
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id,
        )
        self.entity_description = description
        if device_type == "877" and self.entity_description.translation_key == "backlight_bright":
            self.entity_description.mqttTopicCommand = self.entity_description.mqttTopicCommand.replace("backlight","program_data/0")
            self.entity_description.mqttTopicCurrentValue = self.entity_description.mqttTopicCurrentValue.replace("backlight","program_data/0")
            self.entity_description.payload_on = "01"
            self.entity_description.payload_off = "00"
        if device_type == "248" and self.entity_description.translation_key == "sound_switch":
            self.entity_description.mqttTopicCommand = self.entity_description.mqttTopicCommand.replace("volume","sound")
            self.entity_description.mqttTopicCurrentValue = self.entity_description.mqttTopicCurrentValue.replace("volume","sound")
        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class'].replace('-', '_').lower()}_{POLARIS_DEVICE[int(device_type)]['model'].replace('-', '_').lower()}_{description.key}"
        self.payload_on=self.entity_description.payload_on
        self.payload_off=self.entity_description.payload_off
        self._attr_has_entity_name = True
#        self._old_mode = "0"
        self._attr_available = False
#        self._attr_assumed_state = False
#        self._optimistic = False
#        self._value_template = self.entity_description.mqttTopicCurrentValue
        if device_type == "806":
            self._heater_prog_data0 = "0000"
        else:
            self._heater_prog_data0 = "000000"
        if device_type == "826":
            self._EAP_data0 = "0000"
        if device_type in POLARIS_AIRCONDITIONER_TYPE:
            if device_type == "882":
                self._swing_message = "000000000000"
            else:
                self._swing_message = "00000000"
                self._aircond_data0 = "0000"
            if device_type == "882":
                self._aircond_data1 = "00000000"
            if self.entity_description.key == "fireplace":
                self._attr_available = False
            if self.entity_description.key == "silent_1":
                self._attr_available = False
            if self.entity_description.key == "silent_2":
                self._attr_available = False
            if self.entity_description.key == "turbo":
                self._attr_available = False
            if self.entity_description.key == "self_cleaning":
                self._attr_available = False
            if self.entity_description.key == "eco_mode_switch":
                self._attr_available = False
            if self.entity_description.key == "anti_fingus":
                self._attr_available = False
            if self.entity_description.key == "night":
                self._attr_available = False

    async def async_added_to_hass(self):
        @callback
        def message_received(message):
            if POLARIS_DEVICE[int(self.device_type)]['class'] == "coffeemaker":
                if self.device_type in POLARIS_COFFEEMAKER_ROG_TYPE:
                    if str(message.payload) in ("1", "2", "3", "4", "5", "6", "true"):
                        self._attr_is_on = True
                    else:
                        self._attr_is_on = False
                elif str(message.payload) in ("01", "1", "03", "3"):
                    self._attr_is_on = True
                else:
                    self._attr_is_on = False
            elif self.entity_description.key == "display_off_heater":
                self._heater_prog_data0 = str(message.payload)
                self._attr_is_on = True if (self._heater_prog_data0[2:4] == "01") else False
            elif self.entity_description.key == "half_power_heater":
                self._heater_prog_data0 = str(message.payload)
                self._attr_is_on = True if (self._heater_prog_data0[-2:] == "01") else False
                
            elif self.entity_description.key == "quiet_mode":
                self._aircond_data0 = str(message.payload)
                self._attr_is_on = True if (self._aircond_data0[-2:] == "01") else False
            elif self.entity_description.key == "self_cleaning":
                self._aircond_data0 = str(message.payload)
                self._attr_is_on = True if (self._aircond_data0[:2] == "01") else False
            elif self.entity_description.key == "night_light_mode":
                self._attr_is_on = True if (message.payload == "6") else False
            else:
                if message.payload == self.payload_on:
                    self._attr_is_on = True
                elif message.payload == self.payload_off:
                    self._attr_is_on = False
                elif str(message.payload).lower() in ("1", "01", "2", "3", "4", "5", "true"):
                    self._attr_is_on = True
                elif str(message.payload).lower() in ("0", "00", "false"):
                   self._attr_is_on = False
            self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue,
            message_received,
            1,
        )
        
        @callback
        def mode_message_received(message):
            if self.entity_description.translation_key == "keepwarm_switch":
                if str(message.payload) in ("[]", '[{"mode":1,"time":0,"temperature":0}]'):
                    self._attr_available = False
#                    self._attr_is_on = False
                else:
                    self._attr_available = True
                    self._attr_is_on = True
                self.async_write_ha_state()

        await mqtt.async_subscribe(
            self.hass,
            self.entity_description.mqttTopicCurrentValue.replace("keepwarm", "steps"),
            mode_message_received,
            1,
        )
        
        @callback
        def EAP_data_message_received(message):
            self._EAP_data0 = message.payload
        if self.device_type == "826":
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue.replace("backlight", "program_data/0"),
                EAP_data_message_received,
                1,
            )
            
        @callback
        def mode_conditioner_data_message_received(message):
            if self.entity_description.key in ("auto_heater_switch", "eco_mode_switch", "turbo", "night", "self_cleaning", "anti_fingus"):
                if self.device_type in ("857","860"): # air_conditioner "Shuft-Berg_MBO-M1" & "Ballu-Discovery-DC"
                    if self.entity_description.key == "night":
                        # night доступен при режиме HEAT ("4") и COOL ("2")
                        self._attr_available = message.payload in ("4", "2")
                    elif self.entity_description.key == "eco_mode_switch":
                        # eco_mode_switch доступен при COOL ("2")
                        self._attr_available = message.payload == "2"
                    elif self.entity_description.key == "auto_heater_switch":
                        # auto_heater_switch доступен при HEAT ("4")
                        self._attr_available = message.payload == "4"
                else:
                    if (message.payload == "5"): #FAN
                        if self.entity_description.key == "night":
                                self._attr_available = False
                        elif self.entity_description.key == "night":
                            self._attr_available = True
                        if (message.payload == "4"): #HEAT
                            if self.entity_description.key in ("auto_heater_switch", "turbo"):
                                self._attr_available = True
                        elif self.entity_description.key == "auto_heater_switch":
                            self._attr_available = False
                        if (message.payload == "2"): #COOL
                            if self.entity_description.key in ("eco_mode_switch", "turbo"): 
                                self._attr_available = True
                        elif self.entity_description.key == "eco_mode_switch":
                            self._attr_available = False
                        if (message.payload == "0"): #OFF
                            if self.entity_description.key in ("self_cleaning", "anti_fingus"): 
                                self._attr_available = True
                        elif self.entity_description.key in ("self_cleaning", "anti_fingus"):
                            self._attr_available = False
                        if message.payload in ("0", "1", "3", "5"):
                            if self.entity_description.key == "turbo":
                                self._attr_available = False
                self.async_write_ha_state()
            if self.entity_description.key == "night_light_mode":
                if message.payload in ("0","6"):
                    self._attr_available = True
                else:
                    self._attr_available = False
                self.async_write_ha_state()

        if (self.device_type in POLARIS_AIRCONDITIONER_TYPE) or (self.device_type in POLARIS_FAN_TYPE):
            await mqtt.async_subscribe(
                self.hass,
                f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/mode",
                mode_conditioner_data_message_received,
                1,
            )
        
        @callback
        def swing_data_message_received(message):
            self._swing_message = message.payload
            if self.entity_description.key == "eco_mode_switch":
                if message.payload[4:6] == "01":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
            if self.entity_description.key == "auto_heater_switch":
                if message.payload[-2:] == "01":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
            if self.entity_description.key == "anti_fingus":
                if message.payload[-2:] == "01":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
        if self.device_type in POLARIS_AIRCONDITIONER_TYPE:
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                swing_data_message_received,
                1,
            )
        
        @callback
        def switch_data1_message_received(message):
            self._aircond_data1 = message.payload
            if self.entity_description.key == "fireplace":
                if message.payload[2:4] == "01":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
            if self.entity_description.key == "silent_1":
                if message.payload[4:6] == "01":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
            if self.entity_description.key == "silent_2":
                if message.payload[4:6] == "02":
                    self._attr_is_on = True
                else:
                   self._attr_is_on = False
                self.async_write_ha_state()
        if self.device_type == "856":
            await mqtt.async_subscribe(
                self.hass,
                self.entity_description.mqttTopicCurrentValue,
                switch_data1_message_received,
                1,
            )
        
        @callback
        async def entity_availability(message):
            if self.entity_description.name != "available":
                if str(message.payload).lower() in ("1", "true"):
                    self._attr_available = False
                else:
                    if self.entity_description.key != "keepwarm":
                        self._attr_available = True
                self.async_write_ha_state()
            
        await mqtt.async_subscribe(self.hass, f"{self.mqtt_root}/{self.entity_description.device_prefix_topic}/state/error/connection", entity_availability, 1)


    def turn_on(self, **kwargs):
#        self._attr_is_on = True # optimistic mode
        topic = f"{self.entity_description.mqttTopicCommand}"
        if self.entity_description.key == "display_off_heater":
            if self.device_type == "806":
                send_message = self._heater_prog_data0[:2] + self.payload_on
            else:
                send_message = self._heater_prog_data0[:2] + self.payload_on + self._heater_prog_data0[-2:]
        elif self.entity_description.key == "eco_mode_switch":
            send_message = self._swing_message[:4] + self.payload_on + self._swing_message[-2:]
        elif self.entity_description.key == "auto_heater_switch":
            send_message = self._swing_message[:6] + self.payload_on
        elif self.entity_description.key == "anti_fingus":
            send_message = self._swing_message[:6] + self.payload_on
        elif self.entity_description.key == "half_power_heater":
            send_message = self._heater_prog_data0[:4] + self.payload_on
        elif self.entity_description.key == "quiet_mode":
            send_message = self._aircond_data0[:2] + self.payload_on
        elif self.entity_description.key == "self_cleaning":
            send_message = self.payload_on + self._aircond_data0[-2:]
        elif (self.device_type == "826" and self.entity_description.key == "backlight"):
            self._EAP_data0 = self._EAP_data0[:2] + "01"
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommand.replace("backlight", "program_data/0"), self._EAP_data0)
            send_message = self.payload_on
        elif self.device_type == "856":
            if self.entity_description.key == "fireplace":
                self._aircond_data1 = self._aircond_data1[:2] + self.payload_on + self._aircond_data1[-4:]
                send_message = self._aircond_data1
            if self.entity_description.key in ("silent_1", "silent_2"):
                self._aircond_data1 = self._aircond_data1[:4] + self.payload_on + self._aircond_data1[-2:]
                send_message = self._aircond_data1
            if self.entity_description.key == "ioniser":
                send_message = self.payload_on
            if self.entity_description.key == "turbo":
                send_message = self.payload_on
        else:
            send_message = self.payload_on
        mqtt.publish(self.hass, topic, send_message)


    def turn_off(self, **kwargs):
#        self._attr_is_on = False # optimistic mode
        topic = f"{self.entity_description.mqttTopicCommand}"
        if self.entity_description.key == "display_off_heater":
            if self.device_type == "806":
                send_message = self._heater_prog_data0[:2] + self.payload_off
            else:
                send_message = self._heater_prog_data0[:2] + self.payload_off + self._heater_prog_data0[-2:]
        elif self.entity_description.key == "eco_mode_switch":
            send_message = self._swing_message[:4] + self.payload_off + self._swing_message[-2:]
        elif self.entity_description.key == "auto_heater_switch":
            send_message = self._swing_message[:6] + self.payload_off
        elif self.entity_description.key == "anti_fingus":
            send_message = self._swing_message[:6] + self.payload_off
        elif self.entity_description.key == "half_power_heater":
            send_message = self._heater_prog_data0[:4] + self.payload_off
        elif self.entity_description.key == "quiet_mode":
            send_message = self._aircond_data0[:2] + self.payload_off
        elif self.entity_description.key == "self_cleaning":
            send_message = self.payload_off + self._aircond_data0[-2:]
        elif (self.device_type == "826" and self.entity_description.key == "backlight"):
            self._EAP_data0 = self._EAP_data0[:2] + "00"
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommand.replace("backlight", "program_data/0"), self._EAP_data0)
            send_message = self.payload_off
        elif self.device_type == "856":
            if self.entity_description.key == "fireplace":
                self._aircond_data1 = self._aircond_data1[:2] + self.payload_off + self._aircond_data1[-4:]
                send_message = self._aircond_data1
            if self.entity_description.key in ("silent_1", "silent_2"):
                self._aircond_data1 = self._aircond_data1[:4] + self.payload_off + self._aircond_data1[-2:]
                send_message = self._aircond_data1
            if self.entity_description.key == "ioniser":
                send_message = self.payload_off
            if self.entity_description.key == "turbo":
                send_message = self.payload_off
        else:
            send_message = self.payload_off
        mqtt.publish(self.hass, topic, send_message)



