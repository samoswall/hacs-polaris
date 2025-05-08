"""The Polaris IQ Home component."""
from __future__ import annotations

import json
import re
import logging
from typing import Iterable, Final, Any
import copy
import datetime
import os
import voluptuous as vol
import struct


from homeassistant.components import mqtt
from homeassistant.components.mqtt.models import ReceiveMessage
from homeassistant.components.vacuum import (
    DOMAIN,
    ATTR_CLEANED_AREA,
    StateVacuumEntity,
#    VacuumActivity,
    VacuumEntityFeature,
)
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.const import ATTR_ENTITY_ID, ATTR_ID
from homeassistant.util import slugify
from homeassistant.core import HomeAssistant, callback, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import config_validation as cv, entity_platform
from .common import PolarisBaseEntity
# Import global values.
from .const import (
    MANUFACTURER,
    MQTT_ROOT_TOPIC,
    DEVICEID,
    DEVICETYPE,
    POLARIS_DEVICE,
    VACUUM,
    PolarisSelectEntityDescription,
    POLARIS_VACUUM_TYPE,
    CUSTOM_SELECT_FILE_PATH,
    SELECT_VACUUM,
)

SERVICE_VACUUM_CLEANING_ROOM: Final = "vacuum_cleaning_room"
ATTR_SELECTED_ROOMS = "rooms"
SELECT_ROOMS = "select_rooms"

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
    vacuumList = []

    
#    if rooms_js:
#    available_rooms = list(rooms_js.keys())
    
    file_path = CUSTOM_SELECT_FILE_PATH
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            custom_data_rooms = json.loads(file.read())
    else:
        custom_data_rooms = None

    if custom_data_rooms is not None and "SELECT_VACUUM_rooms" in custom_data_rooms:
        custom_data_rooms = json.loads(json.dumps(custom_data_rooms))
        rooms_js = custom_data_rooms["SELECT_VACUUM_rooms"]
#        _LOGGER.debug("rooms_js %s", rooms_js)
    else:
        rooms_js = {"no_room": {"id": "00", "coordinates": []}}
    available_rooms = list(rooms_js.keys())
    
    
    
#    _LOGGER.debug("available_rooms read %s", available_rooms)
    
    
    
    
    if (device_type in POLARIS_VACUUM_TYPE):
        VACUUM_LC = copy.deepcopy(VACUUM)
        for description in VACUUM_LC:
            description.mqttTopicCurrentMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCurrentMode}"
            description.mqttTopicCommandMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandMode}"
            description.mqttTopicBatteryState = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicBatteryState}"
            description.mqttTopicBatteryLevel = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicBatteryLevel}"
            description.mqttTopicStateFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicStateFanMode}"
            description.mqttTopicCommandFanMode = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFanMode}"
            description.mqttTopicCommandFindMe = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandFindMe}"
            description.mqttTopicCommandGoArea = f"{mqtt_root}/{device_prefix_topic}/{description.mqttTopicCommandGoArea}"
            description.mqttTopicCommandTest = f"{mqtt_root}/{device_prefix_topic}/state"
            vacuumList.append(
                PolarisVacuum(
                    description=description,
                    device_friendly_name=device_id,
                    mqtt_root=mqtt_root,
                    device_type=device_type,
                    device_id=device_id,
                    available_rooms=available_rooms,
                    rooms_js=rooms_js
                )
            )
    async_add_entities(vacuumList, update_before_add=True)
    
    
    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        "select_rooms",
        {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(SELECT_ROOMS): vol.All(cv.string, vol.In(available_rooms))
    },
        "sweep_rooms_wrapper",
    )


class PolarisVacuum(PolarisBaseEntity, StateVacuumEntity):

    entity_description: PolarisVacuumEntityDescription
#    _unrecorded_attributes = frozenset({ATTR_ROOMS})
    
    
    def __init__(
        self,
        device_friendly_name: str,
        description: PolarisVacuumEntityDescription,
        mqtt_root: str,
        device_id: str | None=None,
        device_type: str | None=None,
        available_rooms: list | None=None,
        rooms_js: str | None=None,
    ) -> None:
        super().__init__(
            device_friendly_name=device_friendly_name,
            mqtt_root=mqtt_root,
            device_type=device_type,
            device_id=device_id,
        )
        self.entity_description = description
        self._attr_unique_id = slugify(f"{device_id}_{description.name}")
        self.entity_id = f"{DOMAIN}.{POLARIS_DEVICE[int(device_type)]['class']}_{POLARIS_DEVICE[int(device_type)]['model']}_{description.name}"
        self._attr_has_entity_name = True
        
        self._attr_fan_speed="min"
        self._attr_fan_speed_list = ["min", "medium", "high", "max"]
        self._attr_supported_features = (
              VacuumEntityFeature.BATTERY
            | VacuumEntityFeature.RETURN_HOME
            | VacuumEntityFeature.CLEAN_SPOT
            | VacuumEntityFeature.STOP
#            | VacuumEntityFeature.PAUSE
            | VacuumEntityFeature.START
            | VacuumEntityFeature.LOCATE
            | VacuumEntityFeature.STATE
            | VacuumEntityFeature.SEND_COMMAND
            | VacuumEntityFeature.FAN_SPEED
            | VacuumEntityFeature.STATUS
            | VacuumEntityFeature.MAP
        )
#        self._entity_component_unrecorded_attributes = frozenset({ATTR_FAN_SPEED_LIST})

        self._attr_battery_icon="mdi:vacuum"
        self._attr_battery_level=70
        self._attr_state = "idle"
        
        
        
        self._select_rooms = []
        self._available_rooms = available_rooms
        self._rooms_js = rooms_js
        
        
        
 
    @property
    def select_rooms(self) -> list | None:
        """Return a list of rooms available to clean."""
        if self._select_rooms:
#            _LOGGER.debug("select_rooms : %s", self._select_rooms)
            return self._rooms
        return []
 
    @property
    def extra_state_attributes(self):
        """Return a dictionary of device state attributes specific to sharkiq."""
        data = {}
        if self._available_rooms is not None:
            data["available_rooms"] = self._available_rooms
        if self._select_rooms is not None:
            data["select_rooms"] = self._select_rooms
        return data


    def int16_array_to_bytes(self, int16_array, byteorder='little'):
        """
        Преобразует массив int16 обратно в байтовую строку.
        Аргументы:
            int16_array: Массив int16 значений (list of int).
            byteorder: Порядок байтов ('little' или 'big'), по умолчанию 'little'.
        Возвращает:
            Байтовая строка (bytes).
        Вызывает исключение ValueError:
            Если byteorder не является 'little' или 'big'.
        """
        if byteorder not in ('little', 'big'):
            raise ValueError("Неверный порядок байтов. Допустимые значения: 'little', 'big'.")
        endian_prefix = '<' if byteorder == 'little' else '>'
        format_string = endian_prefix + 'h' * len(int16_array)
        return struct.pack(format_string, *int16_array) # * распаковывает массив в аргументы для pack
        
    async def sweep_rooms_wrapper(self, select_rooms):
#        for room in self._room_manager.rooms.keys():
#            self._room_manager.rooms[room] = False
        _LOGGER.debug("room in service %s ", select_rooms)
        #for entry in mysel_rooms:
          #  name = self.hass.states.get(entry).attributes['room_name']
        #    _LOGGER.debug("target_rooms entry %s", entry)
#        await self.sweep_rooms(target_rooms)
#        self.async_schedule_update_ha_state(force_refresh=True)
        
        
    def start(self) -> None:
        """Start or resume the cleaning task."""
        if self._attr_state != "cleaning":
            self._attr_state = "cleaning"
            self.schedule_update_ha_state()
            state_mode = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_select_mode_vacuum").state
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, json.loads(json.dumps(SELECT_VACUUM[0].options[state_mode])))

    def stop(self, **kwargs: Any) -> None:
        """Stop the cleaning task, do not return to dock."""
        self._attr_state = "idle"
        self.schedule_update_ha_state()
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, "0")

    def return_to_base(self, **kwargs: Any) -> None:
        """Return dock to charging base."""
        self._attr_state = "returning"
        self.schedule_update_ha_state()
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandMode, "5")

    def clean_spot(self, **kwargs: Any) -> None:
        """Perform a spot clean-up."""
        self._attr_state = "cleaning"
        self.schedule_update_ha_state()
        select_room = self.hass.states.get(f"select.{POLARIS_DEVICE[int(self.device_type)]['class']}_{POLARIS_DEVICE[int(self.device_type)]['model'].replace('-', '_')}_select_room").state
#        _LOGGER.debug("room in select %s ", select_room)
#        _LOGGER.debug("room in select %s ", self._rooms_js[select_room]["coordinate"])
#        _LOGGER.debug("int16_to_bytes %s",self.int16_array_to_bytes(self._rooms_js[select_room]["coordinate"]))
        mqtt.publish(
            self.hass, self.entity_description.mqttTopicCommandGoArea,
            self.int16_array_to_bytes(self._rooms_js[select_room]["coordinate"]),
            1,
            None,
        )

    def set_fan_speed(self, fan_speed: str, **kwargs: Any) -> None:
        """Set the vacuum's fan speed."""
        if fan_speed in self.fan_speed_list:
            self._attr_fan_speed = fan_speed
            self.schedule_update_ha_state()
            mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFanMode, self._attr_fan_speed_list.index(fan_speed)+1)

    async def async_locate(self, **kwargs: Any) -> None:
        """Locate the vacuum's position."""
        await self.hass.services.async_call(
            "notify",
            "persistent_notification",
            service_data={"message": "I'm here!", "title": "Locate request"},
        )
        self._attr_state = "idle"
        self.async_write_ha_state()
        mqtt.publish(self.hass, self.entity_description.mqttTopicCommandFindMe, "true")


    async def async_send_command(
        self,
        command: str,
        params: dict[str, Any] | list[Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Send a command to the vacuum."""
        self._attr_state = "idle"
        self.async_write_ha_state()
        
    
    
#    def _save_log(self, message, topic) -> None:
#        file_path = "vacuum_log.txt"
#        with open(file_path, 'a+', encoding='utf-8') as file:
#            file.write(f"{datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")} {topic} {message}\n")
    

    
    async def async_added_to_hass(self):
        @callback
        def message_received_batt_state(message):
            payload = message.payload
            self._attr_state = payload
        await mqtt.async_subscribe(self.hass, self.entity_description.mqttTopicBatteryState, message_received_batt_state, 1)
        
        @callback
        def message_received_batt_level(message):
            payload = message.payload
            self._attr_battery_level = int(payload)
            self.async_write_ha_state()
        await mqtt.async_subscribe(self.hass, self.entity_description.mqttTopicBatteryLevel, message_received_batt_level, 1)
    
        # @callback
        # def message_received_contour(message):
            # payload = message.payload
            # self._save_log(payload, "Log contour:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/contour", message_received_contour, 1, None)
        
        # @callback
        # def message_received_go_area(message):
            # payload = message.payload
            # self._save_log(payload, "Log go_area:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/go_area", message_received_go_area, 1, None)
    
        # @callback
        # def message_received_mode(message):
            # payload = message.payload
            # self._save_log(payload, "Log mode:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/mode", message_received_mode, 1)
    
        # @callback
        # def message_received_map_angle(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_angle:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_angle", message_received_map_angle, 1)
    
        # @callback
        # def message_received_clean_area(message):
            # payload = message.payload
            # self._save_log(payload, "Log clean_area:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/clean_area", message_received_clean_area, 1)
    
        # @callback
        # def message_received_program_data_0(message):
            # payload = message.payload
            # self._save_log(payload, "Log program_data_0:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/program_data/0", message_received_program_data_0, 1)
    
        # @callback
        # def message_received_program_data_1(message):
            # payload = message.payload
            # self._save_log(payload, "Log program_data_1:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/program_data/1", message_received_program_data_1, 1)
    
        # @callback
        # def message_received_program_data_2(message):
            # payload = message.payload
            # self._save_log(payload, "Log program_data_2:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/program_data/2", message_received_program_data_2, 1)
    
        # @callback
        # def message_received_program_data_3(message):
            # payload = message.payload
            # self._save_log(payload, "Log program_data_3:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/program_data/3", message_received_program_data_3, 1)
    
        # @callback
        # def message_received_program_data_4(message):
            # payload = message.payload
            # self._save_log(payload, "Log program_data_4:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/program_data/4", message_received_program_data_4, 1)
    
        # @callback
        # def message_received_location_current(message):
            # payload = message.payload
            # self._save_log(payload, "Log location_current:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/location_current", message_received_location_current, 1)
    
        # @callback
        # def message_received_map_0(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_0:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map/0", message_received_map_0, 1, None)
    
        # @callback
        # def message_received_map_1(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_1:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map/1", message_received_map_1, 1, None)
    
        # @callback
        # def message_received_virtual_wall(message):
            # payload = message.payload
            # self._save_log(payload, "Log virtual_wall:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/virtual_wall", message_received_virtual_wall, 1, None)
    
        # @callback
        # def message_received_no_go_area(message):
            # payload = message.payload
            # self._save_log(payload, "Log no_go_area:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/no_go_area", message_received_no_go_area, 1, None)
    
        # @callback
        # def message_received_map_image(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_image:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_image", message_received_map_image, 1, None)
    
        # @callback
        # def message_received_map_long_0(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_0:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/0", message_received_map_long_0, 1, None)
    
        # @callback
        # def message_received_map_long_1(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_1:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/1", message_received_map_long_1, 1, None)
    
        # @callback
        # def message_received_map_long_2(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_2:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/2", message_received_map_long_2, 1, None)
    
        # @callback
        # def message_received_map_long_3(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_3:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/3", message_received_map_long_3, 1, None)
    
        # @callback
        # def message_received_map_long_4(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_4:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/4", message_received_map_long_4, 1, None)
    
        # @callback
        # def message_received_map_long_5(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_5:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/5", message_received_map_long_5, 1, None)
    
        # @callback
        # def message_received_map_long_6(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_6:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/6", message_received_map_long_6, 1, None)
    
        # @callback
        # def message_received_map_long_7(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_7:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/7", message_received_map_long_7, 1, None)
    
        # @callback
        # def message_received_map_long_8(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_8:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/8", message_received_map_long_8, 1, None)
    
        # @callback
        # def message_received_map_long_9(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_long_9:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_long/9", message_received_map_long_9, 1, None)
    
        # @callback
        # def message_received_map_location_0(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_0:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/0", message_received_map_location_0, 1, None)
    
        # @callback
        # def message_received_map_location_1(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_1:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/1", message_received_map_location_1, 1, None)
    
        # @callback
        # def message_received_map_location_2(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_2:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/2", message_received_map_location_2, 1, None)
    
        # @callback
        # def message_received_map_location_3(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_3:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/3", message_received_map_location_3, 1, None)
    
        # @callback
        # def message_received_map_location_4(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_4:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/4", message_received_map_location_4, 1, None)
    
        # @callback
        # def message_received_map_location_5(message):
            # payload = message.payload
            # self._save_log(payload, "Log map_location_5:")
        # await mqtt.async_subscribe(self.hass, f"{self.entity_description.mqttTopicCommandTest}/map_location/5", message_received_map_location_5, 1, None)
    