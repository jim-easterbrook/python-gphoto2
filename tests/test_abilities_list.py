# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import unittest

os.environ['VCAMERADIR'] = os.path.join(os.path.dirname(__file__), 'vcamera')

import gphoto2 as gp


class TestAbilitiesList(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')

    def test_abilities_list(self):
        abilities_list = gp.CameraAbilitiesList()
        self.assertIsInstance(abilities_list, gp.CameraAbilitiesList)
        self.assertEqual(len(abilities_list), 0)
        abilities_list.load()
        self.assertNotEqual(len(abilities_list), 0)
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


if __name__ == "__main__":
    unittest.main()
