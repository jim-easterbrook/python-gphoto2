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
import tempfile
import time
import unittest

os.environ['VCAMERADIR'] = os.path.join(os.path.dirname(__file__), 'vcamera')

import gphoto2 as gp


class TestFile(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')
        camera = gp.Camera()
        camera.init()
        path = camera.capture(gp.GP_CAPTURE_IMAGE)
        self.file = camera.file_get(
            path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
        camera.file_delete(path.folder, path.name)
        camera.exit()

    def test_file(self):
        data = memoryview(self.file.get_data_and_size())
        self.assertEqual(data[:10], b'\xff\xd8\xff\xe0\x00\x10JFIF')
        self.assertEqual(len(data), 7082)
        self.assertEqual(self.file.get_mime_type(), 'image/jpeg')
        test_file = os.path.join(
            os.environ['VCAMERADIR'], 'copyright-free-image.jpg')
        file_time = os.path.getmtime(test_file)
        if time.localtime(file_time).tm_isdst == 1:
            # this needs testing on other time zones
            file_time -= 3600
        self.assertEqual(self.file.get_mtime(), int(file_time))
        name = self.file.get_name()
        self.assertEqual(name, 'GPH_0099.JPG')
        self.assertEqual(self.file.get_name_by_type(name, gp.GP_FILE_TYPE_RAW),
                         'raw_GPH_0099.jpg')
        self.assertEqual(self.file.get_mime_type(), 'image/jpeg')
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = os.path.join(tmp_dir, name)
            self.file.save(temp_file)
            self.assertEqual(os.path.getsize(temp_file), 7082)
            with open(temp_file, 'rb') as f:
                self.assertEqual(f.read(), data)


if __name__ == "__main__":
    unittest.main()
