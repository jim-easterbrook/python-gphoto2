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


class TestNoCamera(unittest.TestCase):
    def setUp(self):
        use_vcam(False)

    def test_oo_style(self):
        cameras = gp.Camera.autodetect()
        self.assertIsInstance(cameras, gp.CameraList)
        camera = gp.Camera()
        if len(cameras) > 0:
            # there is actually a camera connected
            camera.init()
            camera.exit()
        else:
            with self.assertRaises(gp.GPhoto2Error) as cm:
                camera.init()
            ex = cm.exception
            self.assertEqual(ex.code, gp.GP_ERROR_MODEL_NOT_FOUND)

    def test_c_style(self):
        OK, cameras = gp.gp_camera_autodetect()
        self.assertGreaterEqual(OK, gp.GP_OK)
        self.assertIsInstance(cameras, gp.CameraList)
        OK, camera = gp.gp_camera_new()
        self.assertEqual(OK, gp.GP_OK)
        OK = gp.gp_camera_init(camera)
        if len(cameras) > 0:
            # there is actually a camera connected
            self.assertEqual(OK, gp.GP_OK)
            self.assertEqual(gp.gp_camera_exit(camera), gp.GP_OK)
        else:
            self.assertEqual(OK, gp.GP_ERROR_MODEL_NOT_FOUND)


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestAutoDetect(unittest.TestCase):
    def setUp(self):
        use_vcam(True)

    def test_oo_style(self):
        cameras = gp.Camera.autodetect()
        self.assertIsInstance(cameras, gp.CameraList)
        self.assertEqual(len(cameras), 1)
        name, value = cameras[0]
        self.assertEqual(name, 'Nikon DSC D750')

    def test_c_style(self):
        OK, cameras = gp.gp_camera_autodetect()
        self.assertGreaterEqual(OK, gp.GP_OK)
        self.assertIsInstance(cameras, gp.CameraList)
        self.assertEqual(gp.gp_list_count(cameras), 1)
        OK, name = gp.gp_list_get_name(cameras, 0)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(name, 'Nikon DSC D750')


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestVirtualCamera(unittest.TestCase):
    def setUp(self):
        use_vcam(True)
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_oo_style(self):
        def list_files(path='/'):
            result = []
            # get files
            for name in self.camera.folder_list_files(path).keys():
                result.append(os.path.join(path, name))
            # recurse over subfolders
            for name in self.camera.folder_list_folders(path).keys():
                result.extend(list_files(os.path.join(path, name)))
            return result

        # get_about
        text = str(self.camera.get_about())
        self.assertTrue(text.startswith('PTP2 driver'))
        self.assertTrue(text.endswith('Enjoy!'))
        # get_summary
        text = str(self.camera.get_summary())
        self.assertTrue(text.startswith('Manufacturer'))
        # get manual
        with self.assertRaises(gp.GPhoto2Error) as cm:
            manual = self.camera.get_manual()
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)
        # get storage info
        storage_info = self.camera.get_storageinfo()
        self.assertEqual(len(storage_info), 1)
        storage_info = storage_info[0]
        self.assertIsInstance(storage_info, gp.CameraStorageInformation)
        # get_config
        widget = self.camera.get_config()
        self.assertIsInstance(widget, gp.CameraWidget)
        self.camera.set_config(widget)
        # get single config
        widget = self.camera.get_single_config('thumbsize')
        self.assertIsInstance(widget, gp.CameraWidget)
        # list config
        config_list = self.camera.list_config()
        self.assertEqual(len(config_list), 68)
        # list_files
        files = list_files()
        self.assertEqual(files[0], '/store_00010001/copyright-free-image.jpg')
        # file_get
        file = self.camera.file_get(
            '/store_00010001', 'copyright-free-image.jpg',
            gp.GP_FILE_TYPE_NORMAL)
        self.assertIsInstance(file, gp.CameraFile)
        # file put
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.folder_put_file('/store_00010001', 'uploaded.jpg',
                                        gp.GP_FILE_TYPE_NORMAL, file)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)
        # file_read
        buffer = bytearray(10)
        with self.assertRaises(gp.GPhoto2Error) as cm:
            data = self.camera.file_read(
                '/store_00010001', 'copyright-free-image.jpg',
                gp.GP_FILE_TYPE_NORMAL, 0, buffer)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)
        # capture
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        self.assertRegex(path.name, 'GPH_\d{4}.JPG')
        self.assertRegex(path.folder, '/store_00010001/DCIM/\d{3}GPHOT')
        info = self.camera.file_get_info(path.folder, path.name)
        self.assertEqual(info.file.size, 7082)
        self.assertEqual(info.file.type, 'image/jpeg')
        # width and height are zero as test image has no exif info
        self.assertEqual(info.file.width, 0)
        self.assertEqual(info.file.height, 0)
        # file set info
        new_info = gp.CameraFileInfo()
        new_info.preview.fields = gp.GP_FILE_INFO_NONE
        new_info.audio.fields = gp.GP_FILE_INFO_NONE
        new_info.file.fields = gp.GP_FILE_INFO_MTIME
        new_info.file.mtime = int(time.time())
        self.camera.file_set_info(path.folder, path.name, new_info)
        # capture preview
        with self.assertRaises(gp.GPhoto2Error) as cm:
            preview_file = self.camera.capture_preview()
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)
        # trigger capture
        self.camera.trigger_capture()
        # wait for event
        while True:
            event_type, event_data = self.camera.wait_for_event(100)
            if event_type in (gp.GP_EVENT_TIMEOUT,
                              gp.GP_EVENT_CAPTURE_COMPLETE):
                break
            if event_type in (gp.GP_EVENT_FILE_ADDED,
                              gp.GP_EVENT_FOLDER_ADDED):
                self.assertIsInstance(event_data, gp.CameraFilePath)
        # delete file(s)
        self.camera.file_delete(path.folder, path.name)
        self.camera.folder_delete_all(path.folder)
        # create folder
        folder, name = '/store_00010001', 'new folder'
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.folder_make_dir(folder, name)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)
        # delete folder
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.folder_remove_dir(folder, name)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_DIRECTORY_NOT_FOUND)
        # port info
        info = self.camera.get_port_info()
        self.assertIsInstance(info, gp.PortInfo)
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.set_port_info(info)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_LIBRARY)
        # port speed
        speed = self.camera.get_port_speed()
        self.assertEqual(speed, 0)
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.set_port_speed(0)
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_BAD_PARAMETERS)
        # abilities list
        abilities = self.camera.get_abilities()
        self.assertIsInstance(abilities, gp.CameraAbilities)
        self.camera.set_abilities(abilities)

    def test_c_style(self):
        def list_files(path='/'):
            result = []
            # get files
            OK, files = gp.gp_camera_folder_list_files(self.camera, path)
            self.assertEqual(OK, gp.GP_OK)
            for idx in range(gp.gp_list_count(files)):
                OK, name = gp.gp_list_get_name(files, idx)
                self.assertEqual(OK, gp.GP_OK)
                result.append(os.path.join(path, name))
            # recurse over subfolders
            OK, folders = gp.gp_camera_folder_list_folders(self.camera, path)
            self.assertEqual(OK, gp.GP_OK)
            for idx in range(gp.gp_list_count(folders)):
                OK, name = gp.gp_list_get_name(folders, idx)
                self.assertEqual(OK, gp.GP_OK)
                result.extend(list_files(os.path.join(path, name)))
            return result

        # get_about
        OK, text = gp.gp_camera_get_about(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertTrue(text.text.startswith('PTP2 driver'))
        self.assertTrue(text.text.endswith('Enjoy!'))
        # get_summary
        OK, text = gp.gp_camera_get_summary(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertTrue(text.text.startswith('Manufacturer'))
        # get manual
        OK, manual = gp.gp_camera_get_manual(self.camera)
        self.assertEqual(OK, gp.GP_ERROR_NOT_SUPPORTED)
        # get storage info
        OK, storage_info = gp.gp_camera_get_storageinfo(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(len(storage_info), 1)
        storage_info = storage_info[0]
        self.assertIsInstance(storage_info, gp.CameraStorageInformation)
        # get_config
        OK, widget = gp.gp_camera_get_config(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(widget, gp.CameraWidget)
        self.assertEqual(gp.gp_camera_set_config(self.camera, widget), gp.GP_OK)
        # get single config
        OK, widget = gp.gp_camera_get_single_config(self.camera, 'thumbsize')
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(widget, gp.CameraWidget)
        # list config
        OK, config_list = gp.gp_camera_list_config(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_list_count(config_list), 68)
        # list_files
        files = list_files()
        self.assertEqual(files[0], '/store_00010001/copyright-free-image.jpg')
        # file_get
        OK, file = gp.gp_camera_file_get(
            self.camera, '/store_00010001', 'copyright-free-image.jpg',
            gp.GP_FILE_TYPE_NORMAL)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(file, gp.CameraFile)
        # file put
        self.assertEqual(
            gp.gp_camera_folder_put_file(
                self.camera, '/store_00010001', 'uploaded.jpg',
                gp.GP_FILE_TYPE_NORMAL, file),
            gp.GP_ERROR_NOT_SUPPORTED)
        # file_read
        buffer = bytearray(10)
        OK, data = gp.gp_camera_file_read(
            self.camera, '/store_00010001', 'copyright-free-image.jpg',
            gp.GP_FILE_TYPE_NORMAL, 0, buffer)
        self.assertEqual(OK, gp.GP_ERROR_NOT_SUPPORTED)
        # capture
        OK, path = gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE)
        self.assertEqual(OK, gp.GP_OK)
        self.assertRegex(path.name, 'GPH_\d{4}.JPG')
        self.assertRegex(path.folder, '/store_00010001/DCIM/\d{3}GPHOT')
        OK, info = gp.gp_camera_file_get_info(
            self.camera, path.folder, path.name)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(info.file.size, 7082)
        self.assertEqual(info.file.type, 'image/jpeg')
        # width and height are zero as test image has no exif info
        self.assertEqual(info.file.width, 0)
        self.assertEqual(info.file.height, 0)
        # file set info
        new_info = gp.CameraFileInfo()
        new_info.preview.fields = gp.GP_FILE_INFO_NONE
        new_info.audio.fields = gp.GP_FILE_INFO_NONE
        new_info.file.fields = gp.GP_FILE_INFO_MTIME
        new_info.file.mtime = int(time.time())
        OK = gp.gp_camera_file_set_info(
            self.camera, path.folder, path.name, new_info)
        self.assertEqual(OK, gp.GP_OK)
        # capture preview
        OK, preview_file = gp.gp_camera_capture_preview(self.camera)
        self.assertEqual(OK, gp.GP_ERROR_NOT_SUPPORTED)
        # trigger capture
        self.assertEqual(gp.gp_camera_trigger_capture(self.camera), gp.GP_OK)
        # wait for event
        while True:
            OK, event_type, event_data = gp.gp_camera_wait_for_event(
                self.camera, 100)
            self.assertEqual(OK, gp.GP_OK)
            if event_type in (gp.GP_EVENT_TIMEOUT,
                              gp.GP_EVENT_CAPTURE_COMPLETE):
                break
            if event_type in (gp.GP_EVENT_FILE_ADDED,
                              gp.GP_EVENT_FOLDER_ADDED):
                self.assertIsInstance(event_data, gp.CameraFilePath)
        # delete file(s)
        self.assertEqual(gp.gp_camera_file_delete(
            self.camera, path.folder, path.name), gp.GP_OK)
        self.assertEqual(gp.gp_camera_folder_delete_all(
            self.camera, path.folder), gp.GP_OK)
        # create folder
        folder, name = '/store_00010001', 'new folder'
        self.assertEqual(
            gp.gp_camera_folder_make_dir(self.camera, folder, name),
            gp.GP_ERROR_NOT_SUPPORTED)
        # delete folder
        self.assertEqual(
            gp.gp_camera_folder_remove_dir(self.camera, folder, name),
            gp.GP_ERROR_DIRECTORY_NOT_FOUND)
        # port info
        OK, info = gp.gp_camera_get_port_info(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(info, gp.PortInfo)
        self.assertEqual(
            gp.gp_camera_set_port_info(self.camera, info), gp.GP_ERROR_LIBRARY)
        # port speed
        speed = gp.gp_camera_get_port_speed(self.camera)
        self.assertEqual(speed, 0)
        self.assertEqual(gp.gp_camera_set_port_speed(self.camera, 0),
                         gp.GP_ERROR_BAD_PARAMETERS)
        # abilities list
        OK, abilities = gp.gp_camera_get_abilities(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(abilities, gp.CameraAbilities)
        self.assertEqual(
            gp.gp_camera_set_abilities(self.camera, abilities), gp.GP_OK)


if __name__ == "__main__":
    unittest.main()
