# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023  Jim Easterbrook  jim@jim-easterbrook.me.uk
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
import tempfile
import unittest

import gphoto2 as gp


class TestFile(unittest.TestCase):
    def setUp(self):
        self.test_file = os.path.join(
            os.path.dirname(__file__), 'vcamera', 'copyright-free-image.jpg')
        with open(self.test_file, 'rb') as f:
            self.src_data = f.read()
        self.assertEqual(len(self.src_data), os.path.getsize(self.test_file))
        self.assertEqual(self.src_data[:10], b'\xff\xd8\xff\xe0\x00\x10JFIF')

    def test_oo_style(self):
        # create CameraFile from data
        cam_file = gp.CameraFile()
        cam_file.set_data_and_size(self.src_data)
        # get mime type from data
        cam_file.detect_mime_type()
        # check detected mime type
        self.assertEqual(cam_file.get_mime_type(), 'image/jpeg')
        # set mime type anyway
        cam_file.set_mime_type('image/jpeg')
        file_time = int(os.path.getmtime(self.test_file))
        cam_file.set_mtime(file_time)
        file_name = 'cam_file.jpg'
        cam_file.set_name(file_name)
        # read data from CameraFile
        self.assertEqual(cam_file.get_data_and_size(), self.src_data)
        self.assertEqual(cam_file.get_mime_type(), 'image/jpeg')
        self.assertEqual(cam_file.get_mtime(), file_time)
        self.assertEqual(cam_file.get_name(), file_name)
        self.assertEqual(
            cam_file.get_name_by_type(file_name, gp.GP_FILE_TYPE_RAW),
            'raw_' + file_name)
        self.assertEqual(cam_file.detect_mime_type(), None)
        # copy file
        file_copy = gp.CameraFile()
        file_copy.copy(cam_file)
        self.assertEqual(file_copy.get_data_and_size(), self.src_data)
        del file_copy
        # save CameraFile to computer
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = os.path.join(tmp_dir, file_name)
            cam_file.save(temp_file)
            self.assertEqual(os.path.getsize(temp_file), len(self.src_data))
            with open(temp_file, 'rb') as f:
                self.assertEqual(f.read(), self.src_data)
            self.assertEqual(int(os.path.getmtime(temp_file)), file_time)
        # wipe file data
        cam_file.clean()
        self.assertEqual(cam_file.get_data_and_size(), b'')
        self.assertEqual(cam_file.get_name(), '')
        del cam_file
        # open file directly
        direct_file = gp.CameraFile()
        direct_file.open(self.test_file)
        self.assertEqual(direct_file.get_data_and_size(), self.src_data)
        self.assertEqual(direct_file.get_mtime(), file_time)
        self.assertEqual(
            direct_file.get_name(), os.path.basename(self.test_file))
        del direct_file
        # create file from file descriptor
        file_copy = gp.CameraFile(os.open(self.test_file, os.O_RDONLY))
        self.assertEqual(file_copy.get_data_and_size(), self.src_data)
        del file_copy

    def test_c_style(self):
        # create CameraFile from data
        OK, cam_file = gp.gp_file_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(
            gp.gp_file_set_data_and_size(cam_file, self.src_data), gp.GP_OK)
        # get mime type from data
        self.assertEqual(gp.gp_file_detect_mime_type(cam_file), gp.GP_OK)
        # check detected mime type
        self.assertEqual(gp.gp_file_get_mime_type(cam_file),
                         [gp.GP_OK, 'image/jpeg'])
        # set mime type anyway
        self.assertEqual(
            gp.gp_file_set_mime_type(cam_file, 'image/jpeg'), gp.GP_OK)
        file_time = int(os.path.getmtime(self.test_file))
        self.assertEqual(gp.gp_file_set_mtime(cam_file, file_time), gp.GP_OK)
        file_name = 'cam_file.jpg'
        self.assertEqual(gp.gp_file_set_name(cam_file, file_name), gp.GP_OK)
        # read data from CameraFile
        self.assertEqual(gp.gp_file_get_data_and_size(cam_file),
                         [gp.GP_OK, self.src_data])
        self.assertEqual(gp.gp_file_get_mime_type(cam_file),
                         [gp.GP_OK, 'image/jpeg'])
        self.assertEqual(gp.gp_file_get_mtime(cam_file), [gp.GP_OK, file_time])
        self.assertEqual(gp.gp_file_get_name(cam_file), [gp.GP_OK, file_name])
        self.assertEqual(gp.gp_file_get_name_by_type(
            cam_file, file_name, gp.GP_FILE_TYPE_RAW),
                         [gp.GP_OK, 'raw_' + file_name])
        self.assertEqual(gp.gp_file_detect_mime_type(cam_file), gp.GP_OK)
        # copy file
        OK, file_copy = gp.gp_file_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_file_copy(file_copy, cam_file), gp.GP_OK)
        self.assertEqual(gp.gp_file_get_data_and_size(file_copy),
                         [gp.GP_OK, self.src_data])
        del file_copy
        # save CameraFile to computer
        with tempfile.TemporaryDirectory() as tmp_dir:
            temp_file = os.path.join(tmp_dir, file_name)
            self.assertEqual(gp.gp_file_save(cam_file, temp_file), gp.GP_OK)
            self.assertEqual(os.path.getsize(temp_file), len(self.src_data))
            with open(temp_file, 'rb') as f:
                self.assertEqual(f.read(), self.src_data)
            self.assertEqual(int(os.path.getmtime(temp_file)), file_time)
        # wipe file data
        self.assertEqual(gp.gp_file_clean(cam_file), gp.GP_OK)
        self.assertEqual(gp.gp_file_get_data_and_size(cam_file),
                         [gp.GP_OK, b''])
        self.assertEqual(gp.gp_file_get_name(cam_file), [gp.GP_OK, ''])
        del cam_file
        # open file directly
        OK, direct_file = gp.gp_file_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_file_open(direct_file, self.test_file), gp.GP_OK)
        self.assertEqual(gp.gp_file_get_data_and_size(direct_file),
                         [gp.GP_OK, self.src_data])
        self.assertEqual(gp.gp_file_get_mtime(direct_file),
                         [gp.GP_OK, file_time])
        self.assertEqual(gp.gp_file_get_name(direct_file),
                         [gp.GP_OK, os.path.basename(self.test_file)])
        del direct_file
        # create file from file descriptor
        OK, file_copy = gp.gp_file_new_from_fd(
            os.open(self.test_file, os.O_RDONLY))
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_file_get_data_and_size(file_copy),
                         [gp.GP_OK, self.src_data])
        del file_copy


if __name__ == "__main__":
    unittest.main()
