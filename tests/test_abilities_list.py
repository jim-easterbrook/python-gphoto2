# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023-24  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This file is part of python-gphoto2.
#
# python-gphoto2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# python-gphoto2 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with python-gphoto2.  If not, see
# <https://www.gnu.org/licenses/>.

import os
import sys
import unittest

import gphoto2 as gp

path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.insert(0, path)
from tests.vcamera import has_vcam, use_vcam


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestAbilitiesList(unittest.TestCase):
    def setUp(self):
        use_vcam(True)
        # set locale dir (should be already set by package __init__)
        locale_dir = os.environ['IOLIBS'].replace('vusb', 'locale')
        self.assertEqual(gp.gp_init_localedir(locale_dir), gp.GP_OK)
        self.assertEqual(gp.gp_message_codeset('utf-8'), 'utf-8')

    def test_oo_style(self):
        abilities_list = gp.CameraAbilitiesList()
        self.assertIsInstance(abilities_list, gp.CameraAbilitiesList)
        self.assertEqual(len(abilities_list), 0)
        abilities_list.load()
        self.assertGreater(len(abilities_list), 0)
        abilities = abilities_list[0]
        self.assertIsInstance(abilities, gp.CameraAbilities)
        self.assertIsInstance(abilities.model, str)
        port_info_list = gp.PortInfoList()
        port_info_list.load()
        camera_list = abilities_list.detect(port_info_list)
        self.assertEqual(len(camera_list), 1)
        name, value = camera_list[0]
        self.assertEqual(name, 'Nikon DSC D750')
        self.assertIsInstance(abilities_list.lookup_model(name), int)
        abilities_list.reset()
        self.assertEqual(len(abilities_list), 0)
        abilities_list.load_dir(os.environ['CAMLIBS'])
        self.assertGreater(len(abilities_list), 0)

    def test_c_style(self):
        OK, abilities_list = gp.gp_abilities_list_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(abilities_list, gp.CameraAbilitiesList)
        self.assertEqual(gp.gp_abilities_list_count(abilities_list), 0)
        self.assertEqual(gp.gp_abilities_list_load(abilities_list), gp.GP_OK)
        self.assertGreater(gp.gp_abilities_list_count(abilities_list), 0)
        OK, abilities = gp.gp_abilities_list_get_abilities(abilities_list, 0)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(abilities, gp.CameraAbilities)
        self.assertIsInstance(abilities.model, str)
        OK, port_info_list = gp.gp_port_info_list_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_port_info_list_load(port_info_list), gp.GP_OK)
        OK, camera_list = gp.gp_abilities_list_detect(
            abilities_list, port_info_list)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_list_count(camera_list), 1)
        OK, name = gp.gp_list_get_name(camera_list, 0)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(name, 'Nikon DSC D750')
        OK, value = gp.gp_list_get_value(camera_list, 0)
        self.assertEqual(OK, gp.GP_OK)
        idx = gp.gp_abilities_list_lookup_model(abilities_list, name)
        self.assertIsInstance(idx, int)
        self.assertEqual(gp.gp_abilities_list_reset(abilities_list), gp.GP_OK)
        self.assertEqual(gp.gp_abilities_list_count(abilities_list), 0)
        self.assertEqual(
            gp.gp_abilities_list_load_dir(abilities_list,
                                          os.environ['CAMLIBS']), gp.GP_OK)
        self.assertGreater(gp.gp_abilities_list_count(abilities_list), 0)


if __name__ == "__main__":
    unittest.main()
