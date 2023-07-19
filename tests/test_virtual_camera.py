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


class TestAutoDetect(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')

    def test_autodetect(self):
        cameras = gp.Camera.autodetect()
        self.assertIsInstance(cameras, gp.CameraList)
        self.assertEqual(len(cameras), 1)
        name, value = cameras[0]
        self.assertEqual(name, 'Nikon DSC D750')


class TestVirtualCamera(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_get_about(self):
        text = str(self.camera.get_about())
        self.assertTrue(text.startswith('PTP2 driver'))
        self.assertTrue(text.endswith('Enjoy!'))

    def test_get_summary(self):
        text = str(self.camera.get_summary())
        self.assertTrue(text.startswith('Manufacturer'))

    def list_config(self, widget):
        label = '{} ({})'.format(widget.get_label(), widget.get_name())
        result = [label]
        widget_type = widget.get_type()
        if widget_type in (gp.GP_WIDGET_WINDOW, gp.GP_WIDGET_SECTION):
            for child in widget.get_children():
                result += self.list_config(child)
        return result

    def test_get_config(self):
        widget = self.camera.get_config()
        config_list = self.list_config(widget)
        self.assertEqual(len(config_list), 31)
        self.assertEqual(
            config_list[0], 'Camera and Driver Configuration (main)')

    def list_files(self, path='/'):
        result = []
        # get files
        for name, value in self.camera.folder_list_files(path):
            result.append(os.path.join(path, name))
        # read folders
        folders = []
        for name, value in self.camera.folder_list_folders(path):
            folders.append(name)
        # recurse over subfolders
        for name in folders:
            result.extend(self.list_files(os.path.join(path, name)))
        return result

    def test_list_files(self):
        files = self.list_files()
        self.assertEqual(files, ['/store_00010001/copyright-free-image.jpg'])

    def test_capture(self):
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        self.assertEqual(path.name, 'GPH_0099.JPG')
        self.assertEqual(path.folder, '/store_00010001/DCIM/100GPHOT')
        info = self.camera.file_get_info(path.folder, path.name).file
        self.assertEqual(info.size, 7082)
        self.assertEqual(info.type, 'image/jpeg')
        # width and height are zero as test image has no exif info
        self.assertEqual(info.width, 0)
        self.assertEqual(info.height, 0)


if __name__ == "__main__":
    unittest.main()
