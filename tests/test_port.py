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

import logging
import os
import sys
import unittest

import gphoto2 as gp

path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.insert(0, path)
from tests.vcamera import has_vcam, use_vcam


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestPort(unittest.TestCase):
    def setUp(self):
        use_vcam(True)
        self.camera = gp.Camera()
        self.camera.init()
        self.camera.exit()

    def test_oo_style(self):
        info = self.camera.get_port_info()
        port = gp.GPPort()
        self.assertIsInstance(port, gp.GPPort)
        port.set_info(info)
        info_copy = port.get_info()
        self.assertIsInstance(info_copy, gp.PortInfo)
        port.open()
        port.reset()
        port.close()

    def test_c_style(self):
        OK, info = gp.gp_camera_get_port_info(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        OK, port = gp.gp_port_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(port, gp.GPPort)
        self.assertEqual(gp.gp_port_set_info(port, info), gp.GP_OK)
        OK, info_copy = gp.gp_port_get_info(port)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(info_copy, gp.PortInfo)
        self.assertEqual(gp.gp_port_open(port), gp.GP_OK)
        self.assertEqual(gp.gp_port_reset(port), gp.GP_OK)
        self.assertEqual(gp.gp_port_close(port), gp.GP_OK)


if __name__ == "__main__":
    unittest.main()
