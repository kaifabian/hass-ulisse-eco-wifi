#!/usr/bin/env python3
# -*- coding: utf-8 -*-
############################################################################
# Copyright 2021 Kai Fabian                                                #
#                                                                          #
# Licensed under the Apache License, Version 2.0 (the "License");          #
# you may not use this file except in compliance with the License.         #
# You may obtain a copy of the License at                                  #
#                                                                          #
#     http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                          #
# Unless required by applicable law or agreed to in writing, software      #
# distributed under the License is distributed on an "AS IS" BASIS,        #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. #
# See the License for the specific language governing permissions and      #
# limitations under the License.                                           #
############################################################################

import logging
import requests
import time

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.climate import (
    ClimateEntity,
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    TEMP_CELSIUS,
)
from homeassistant.components.climate.const import (
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
    FAN_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_OFF,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_NONE,
    PRESET_SLEEP,
    SUPPORT_FAN_MODE,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    CONF_DEVICES,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SSL,
    CONF_UNIQUE_ID,
)


from . import DOMAIN
from .ulisse_serializer import UlisseEco13DCIWiFiSerializer

try:
    from functools import reduce
except ImportError: pass


_LOGGER = logging.getLogger(__name__)


DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=1001): cv.port,
    vol.Optional(CONF_SSL, default=False): cv.boolean,
    vol.Optional(CONF_NAME, default="Ulisse Air Conditioner"): cv.string,
    vol.Optional(CONF_UNIQUE_ID, default=None): cv.matches_regex(r'^[\da-z][\da-z_]*(?<!_)$'),
})


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_DEVICES, default=[]): vol.Schema([DEVICE_SCHEMA]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    devices = config[CONF_DEVICES]
    entities = list()

    for device in devices:
        entities.append(Ulisse13EcoDCIWiFi(device))

    add_entities(entities)


class Ulisse13EcoDCIWiFi(ClimateEntity):
    __ro = lambda val: property(lambda *args, **kwargs: val)
    _hvac_mode_map = {
       HVAC_MODE_HEAT: 3,
       HVAC_MODE_COOL: 1,
       HVAC_MODE_HEAT_COOL: 5,
       HVAC_MODE_DRY: 2,
       HVAC_MODE_FAN_ONLY: 4,
    }
    _hvac_mode_rmap = dict((v,k) for k,v in _hvac_mode_map.items())

    _features = {
        SUPPORT_FAN_MODE,
        SUPPORT_PRESET_MODE,
        SUPPORT_TARGET_TEMPERATURE,
    }

    should_poll = __ro(True)
    temperature_unit = __ro(TEMP_CELSIUS)
    precision = __ro(0.1)
    max_temp = __ro(32)
    min_temp = __ro(10)

    hvac_modes = __ro({HVAC_MODE_OFF, } | set(_hvac_mode_map.keys()))
    supported_features = __ro(reduce(int.__or__, _features, 0))
    fan_modes = __ro({FAN_LOW, FAN_MEDIUM, FAN_HIGH, FAN_AUTO, })
    preset_modes = __ro({PRESET_BOOST, PRESET_ECO, PRESET_NONE, PRESET_SLEEP, })

    def __init__(self, config, *args, **kwargs):
        self._config = config

        if CONF_UNIQUE_ID in config:
            self.entity_id = ENTITY_ID_FORMAT.format(DOMAIN + "_" + config[CONF_UNIQUE_ID])

        self.serializer = UlisseEco13DCIWiFiSerializer
        self._state = self.serializer.empty()
        self._state_update = self.serializer.empty()

        super().__init__(*args, **kwargs)

    def url(self, hmi="", update=False):
        device_url = "{scheme}://{host}:{port}/".format(
            scheme="https" if self._config[CONF_SSL] else "http",
            host=self._config[CONF_HOST],
            port=self._config[CONF_PORT],
        )
        url = device_url + "?HMI=" + hmi
        if update:
            url += "&UPD=1"
        return url

    def push_changes(self):
        state_update = self.serializer.empty()

        # atomic swap
        state_update, self._state_update = self._state_update, state_update
        _LOGGER.debug(f"ulisse_intended_changes={state_update!r}")

        if state_update != self.serializer.empty():
            for i in range(5):
                request_uri = self.url(self.serializer.serialize(state_update), update=True)

                try:
                    _LOGGER.debug(f"ulisse_request: {request_uri!r}")
                    response = requests.get(request_uri)
                    _LOGGER.debug(f"ulisse_response: {response!r}")
                except IOError as e:
                    _LOGGER.error(f"Could not access Ulisse 13 DCI: request_uri={request_uri!r} exc={e!r}")
                    return False

                time.sleep(0.2)

        if not self.update():
            return False

        # # restore failed/deferred state changes
        # for key in state_update:
        #     if state_update[key] is None: continue

        #     if self._state[key] != state_update[key] and self._state_update[key] is None:
        #         self._state_update[key] = state_update[key]
        #         _LOGGER.debug(f"ulisse_restored_state_update: key={key!r}")


    def update(self, update_state=True):
        request_uri = self.url()
        response = None

        try:
            _LOGGER.debug(f"ulisse_request: {request_uri!r}")
            response = requests.get(request_uri).text
            _LOGGER.debug(f"ulisse_response: {response!r}")
        except IOError as e:
            _LOGGER.error(f"Could not access Ulisse 13 DCI: request_uri={request_uri!r} exc={e!r}")
            return False

        self._state = self.serializer.parse(response)
        _LOGGER.debug(f"ulisse_updated_state={self._state!r}")

        return True

    @property
    def current_temperature(self):
        temp = self._state.get("TEMPERATURE_MEASURED")
        if temp is None: return temp
        return temp * 0.1

    @property
    def target_temperature(self):
        temp = self._state.get("TEMPERATURE_INTENDED")
        if temp is None: return temp
        return temp * 0.1

    def set_temperature(self, **kwargs):
        self._state_update["TEMPERATURE_INTENDED"] = int(kwargs.get(ATTR_TEMPERATURE) * 10)
        self.push_changes()

    @property
    def hvac_mode(self):
        if self._state["ON_OFF"] != 1:
            return HVAC_MODE_OFF

        return self._hvac_mode_rmap.get(self._state["MODE"], HVAC_MODE_OFF) 

    def set_hvac_mode(self, mode):
        self._state_update["ON_OFF"] = 0 if mode == HVAC_MODE_OFF else 1
        self._state_update["MODE"] = self._hvac_mode_map.get(mode, None)
        self.push_changes()


    @property
    def name(self):
        return self._config[CONF_NAME]

    @property
    def preset_mode(self):
        if self._state.get("USE_TURBO_MODE", None):
            return PRESET_BOOST

        if self._state.get("USE_NIGHT_MODE", None):
            return PRESET_SLEEP

        if self._state.get("USE_ECO_MODE", None):
            return PRESET_ECO

        return PRESET_NONE
        

    def set_preset_mode(self, preset_mode):
        mode_is = lambda m: 1 if preset_mode == m else 0
        self._state_update.update({
            "USE_TURBO_MODE": mode_is(PRESET_BOOST),
            "USE_NIGHT_MODE": mode_is(PRESET_SLEEP),
            "USE_ECO_MODE":   mode_is(PRESET_ECO),
        })
        self.push_changes()

    @property
    def fan_mode(self):
        speed = self._state.get("FAN_SPEED", None)
        speed_map = {
            0: FAN_AUTO,
            1: FAN_LOW,
            2: FAN_LOW,
            3: FAN_MEDIUM,
            4: FAN_MEDIUM,
            5: FAN_HIGH,
            6: FAN_HIGH,
        }
        return speed_map.get(speed, FAN_AUTO)

    def set_fan_mode(self, fan_mode):
        speed_rmap = {
            FAN_AUTO: 0,
            FAN_LOW: 2,
            FAN_MEDIUM: 4,
            FAN_HIGH: 6,
        }
        self._state_update["FAN_SPEED"] = speed_rmap.get(fan_mode, FAN_AUTO)
        self.push_changes()


