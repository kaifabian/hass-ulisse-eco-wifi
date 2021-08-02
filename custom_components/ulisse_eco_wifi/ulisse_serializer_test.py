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

import unittest

from ulisse_serializer import *

class TestUlisse13EcoDCIWiFiSerialization(unittest.TestCase):
    def setUp(self):
        self.serializer = UlisseEco13DCIWiFiSerializer

    def test_pack(self):
        state = {
            "TEMPERATURE_INTENDED": 230,
            "ON_OFF": None,
            "FAN_SPEED": 2,
        }
        state_str = self.serializer.serialize(state)
        self.assertEqual(state_str, "230,N,N,N,2,N,N,N,N,N,N,N,N" + ",N"*21)

    def test_unpack(self):
        state_str = "230,250,1,5,6,N,0,1,1,0,0,0,0,2,1,2,1,0,0,1,0,75,1416,0" + ",N"*10
        state = self.serializer.parse(state_str)
        self.assertEqual(state.get("TEMPERATURE_INTENDED"), 230)
        self.assertEqual(state.get("TEMPERATURE_MEASURED"), 250)
        self.assertEqual(state.get("USE_ECO_MODE"), 1)
        self.assertEqual(state.get("VERTICAL_AIR_MODE"), None)

    def test_empty(self):
        empty = self.serializer.empty()
        state_str = self.serializer.serialize(empty)
        self.assertEqual(state_str, ",".join(("N", ) * 34))


if __name__ == "__main__":
    unittest.main()
