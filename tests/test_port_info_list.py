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


class TestPortInfoList(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')

    def test_oo_style(self):
        port_info_list = gp.PortInfoList()
        self.assertIsInstance(port_info_list, gp.PortInfoList)
        self.assertEqual(len(port_info_list), 0)
        port_info_list.load()
        self.assertEqual(len(port_info_list), 1)
        port_info = port_info_list.get_info(0)
        name = port_info.get_name()
        self.assertEqual(name, 'Universal Serial Bus')
        self.assertEqual(port_info_list.lookup_name(name), 0)
        path = port_info.get_path()
        self.assertEqual(path, 'usb:001,001')
        self.assertEqual(port_info_list.lookup_path(path), 0)
        type_ = port_info.get_type()
        self.assertEqual(type_, gp.GP_PORT_USB)

    def test_c_style(self):
        OK, port_info_list = gp.gp_port_info_list_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(port_info_list, gp.PortInfoList)
        self.assertEqual(gp.gp_port_info_list_count(port_info_list), 0)
        self.assertEqual(gp.gp_port_info_list_load(port_info_list), gp.GP_OK)
        self.assertEqual(gp.gp_port_info_list_count(port_info_list), 1)
        OK, port_info = gp.gp_port_info_list_get_info(port_info_list, 0)
        self.assertEqual(OK, gp.GP_OK)
        OK, name = gp.gp_port_info_get_name(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(name, 'Universal Serial Bus')
        self.assertEqual(
            gp.gp_port_info_list_lookup_name(port_info_list, name), 0)
        OK, path = gp.gp_port_info_get_path(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(path, 'usb:001,001')
        self.assertEqual(
            gp.gp_port_info_list_lookup_path(port_info_list, path), 0)
        OK, type_ = gp.gp_port_info_get_type(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(type_, gp.GP_PORT_USB)


if __name__ == "__main__":
    unittest.main()
