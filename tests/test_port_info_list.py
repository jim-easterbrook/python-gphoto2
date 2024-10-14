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
from tests.vcamera import use_vcam


class TestPortInfoList(unittest.TestCase):
    def setUp(self):
        use_vcam(False)

    def test_oo_style(self):
        port_info_list = gp.PortInfoList()
        self.assertIsInstance(port_info_list, gp.PortInfoList)
        self.assertEqual(len(port_info_list), 0)
        port_info_list.load()
        self.assertGreater(len(port_info_list), 0)
        port_info = port_info_list.get_info(0)
        name = port_info.get_name()
        self.assertIsInstance(name, str)
        self.assertEqual(port_info_list.lookup_name(name), 0)
        path = port_info.get_path()
        self.assertIsInstance(path, str)
        self.assertEqual(port_info_list.lookup_path(path), 0)
        type_ = port_info.get_type()
        self.assertIsInstance(type_, int)

    def test_c_style(self):
        OK, port_info_list = gp.gp_port_info_list_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(port_info_list, gp.PortInfoList)
        self.assertEqual(gp.gp_port_info_list_count(port_info_list), 0)
        self.assertEqual(gp.gp_port_info_list_load(port_info_list), gp.GP_OK)
        self.assertGreater(gp.gp_port_info_list_count(port_info_list), 0)
        OK, port_info = gp.gp_port_info_list_get_info(port_info_list, 0)
        self.assertEqual(OK, gp.GP_OK)
        OK, name = gp.gp_port_info_get_name(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(name, str)
        self.assertEqual(
            gp.gp_port_info_list_lookup_name(port_info_list, name), 0)
        OK, path = gp.gp_port_info_get_path(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(path, str)
        self.assertEqual(
            gp.gp_port_info_list_lookup_path(port_info_list, path), 0)
        OK, type_ = gp.gp_port_info_get_type(port_info)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(type_, int)


if __name__ == "__main__":
    unittest.main()
