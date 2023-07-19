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

import gphoto2 as gp


class TestNoCamera(unittest.TestCase):
    def setUp(self):
        # switch from virtual camera to normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('vusb', 'iolibs')

    def test_autodetect_and_init(self):
        cameras = gp.Camera.autodetect()
        self.assertIsInstance(cameras, gp.CameraList)
        camera = gp.Camera()
        if len(cameras) > 0:
            # there is actually a camera connected
            camera.init()
        else:
            with self.assertRaises(gp.GPhoto2Error) as cm:
                camera.init()
            ex = cm.exception
            self.assertEqual(ex.code, -105)


if __name__ == "__main__":
    unittest.main()
