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

class UlisseSerializer:
    @classmethod
    def empty(cls):
        return dict((key, None, ) for key in cls._fields if key)

    @classmethod
    def parse(cls, state_str):
        fields = [None if x.strip().upper() == 'N' else int(x, 10) for x in state_str.split(",")]
        state = dict(zip(cls._fields, fields[:len(cls._fields)]))
        return state

    @classmethod
    def serialize(cls, state):
        fmt = lambda x: str(int(x)) if x is not None else 'N'
        fields = ",".join(fmt(state.get(key, None)) for key in cls._fields)
        return fields


class UlisseEco13DCIWiFiSerializer(UlisseSerializer):
    _fields = (
        "TEMPERATURE_INTENDED",
        "TEMPERATURE_MEASURED",
        "ON_OFF",
        "MODE",
        "FAN_SPEED",
        "VERTICAL_AIR_MODE",
        "USE_REMOTE_TEMPERATURE",
        "USE_FILTER",
        "USE_ECO_MODE",
        "USE_TURBO_MODE",
        "USE_NIGHT_MODE",
        "LIGHT_MODE",
        "TIMER_MODE",
    ) + (None, ) * 21


