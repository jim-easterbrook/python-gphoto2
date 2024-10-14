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
import time
import unittest

import gphoto2 as gp

path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.insert(0, path)
from tests.vcamera import has_vcam, use_vcam


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestFilesys(unittest.TestCase):
    def setUp(self):
        use_vcam(True)
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_camera_storage_information(self):
        storage_info = self.camera.get_storageinfo()
        self.assertEqual(len(storage_info), 1)
        storage_info = storage_info[0]
        self.assertIsInstance(storage_info, gp.CameraStorageInformation)
        self.assertEqual(storage_info.fields,
                         gp.GP_STORAGEINFO_FREESPACEIMAGES |
                         gp.GP_STORAGEINFO_FREESPACEKBYTES|
                         gp.GP_STORAGEINFO_MAXCAPACITY|
                         gp.GP_STORAGEINFO_FILESYSTEMTYPE |
                         gp.GP_STORAGEINFO_STORAGETYPE |
                         gp.GP_STORAGEINFO_ACCESS |
                         gp.GP_STORAGEINFO_DESCRIPTION |
                         gp.GP_STORAGEINFO_LABEL |
                         gp.GP_STORAGEINFO_BASE)
        self.assertEqual(storage_info.basedir, '/store_00010001')
        self.assertEqual(storage_info.label, 'GPVCS Label')
        self.assertEqual(storage_info.description, 'GPVC Storage')
        self.assertEqual(storage_info.type, gp.GP_STORAGEINFO_ST_FIXED_RAM)
        self.assertEqual(storage_info.fstype, gp.GP_STORAGEINFO_FST_DCF)
        self.assertEqual(storage_info.access,
                         gp.GP_STORAGEINFO_AC_READONLY_WITH_DELETE)
        self.assertEqual(storage_info.capacitykbytes, 1085584)
        self.assertEqual(storage_info.freekbytes, 542792)
        self.assertEqual(storage_info.freeimages, 150)

    def test_camera_file_info(self):
        file_name = 'copyright-free-image.jpg'
        test_file = os.path.join(
            os.path.dirname(__file__), 'vcamera', file_name)
        camera_file_info = self.camera.file_get_info(
            '/store_00010001', file_name)
        self.assertIsInstance(camera_file_info, gp.CameraFileInfo)
        # check preview info
        preview_info = camera_file_info.preview
        self.assertIsInstance(preview_info, gp.CameraFileInfoPreview)
        self.assertEqual(preview_info.fields, gp.GP_FILE_INFO_TYPE)
        # check audio info
        audio_info = camera_file_info.audio
        self.assertIsInstance(audio_info, gp.CameraFileInfoAudio)
        self.assertEqual(audio_info.fields, gp.GP_FILE_INFO_NONE)
        # check file info
        file_info = camera_file_info.file
        self.assertIsInstance(file_info, gp.CameraFileInfoFile)
        self.assertEqual(file_info.fields,
                         gp.GP_FILE_INFO_MTIME | gp.GP_FILE_INFO_PERMISSIONS |
                         gp.GP_FILE_INFO_SIZE | gp.GP_FILE_INFO_TYPE)
        self.assertEqual(file_info.size, os.path.getsize(test_file))
        self.assertEqual(file_info.type, 'image/jpeg')
        self.assertEqual(file_info.permissions,
                         gp.GP_FILE_PERM_READ | gp.GP_FILE_PERM_DELETE)
        mtime = os.path.getmtime(test_file)
        if time.localtime(mtime).tm_isdst == 1:
            # this needs testing on other time zones
            mtime -= 3600
        self.assertEqual(file_info.mtime, int(mtime))


if __name__ == "__main__":
    unittest.main()
