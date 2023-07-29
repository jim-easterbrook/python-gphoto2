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


class TestNoCamera(unittest.TestCase):
    def setUp(self):
        # switch from virtual camera to normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('vusb', 'iolibs')

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


class TestAutoDetect(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')

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


class TestVirtualCamera(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_oo_style(self):
        def list_config(widget):
            label = '{} ({})'.format(widget.get_label(), widget.get_name())
            result = [label]
            widget_type = widget.get_type()
            if widget_type in (gp.GP_WIDGET_WINDOW, gp.GP_WIDGET_SECTION):
                for child in widget.get_children():
                    result += list_config(child)
            return result

        def list_files(path='/'):
            result = []
            # get files
            for name, value in self.camera.folder_list_files(path):
                result.append(os.path.join(path, name))
            # recurse over subfolders
            for name, value in self.camera.folder_list_folders(path):
                result.extend(list_files(os.path.join(path, name)))
            return result

        # get_about
        text = str(self.camera.get_about())
        self.assertTrue(text.startswith('PTP2 driver'))
        self.assertTrue(text.endswith('Enjoy!'))
        # get_summary
        text = str(self.camera.get_summary())
        self.assertTrue(text.startswith('Manufacturer'))
        # get_config
        widget = self.camera.get_config()
        config_list = list_config(widget)
        self.assertEqual(len(config_list), 31)
        self.assertEqual(
            config_list[0], 'Camera and Driver Configuration (main)')
        # list_files
        files = list_files()
        self.assertEqual(files[0], '/store_00010001/copyright-free-image.jpg')
        # file_get
        file = self.camera.file_get(
            '/store_00010001', 'copyright-free-image.jpg',
            gp.GP_FILE_TYPE_NORMAL)
        self.assertIsInstance(file, gp.CameraFile)
        # capture
        path = self.camera.capture(gp.GP_CAPTURE_IMAGE)
        self.assertRegex(path.name, 'GPH_\d{4}.JPG')
        self.assertRegex(path.folder, '/store_00010001/DCIM/\d{3}GPHOT')
        info = self.camera.file_get_info(path.folder, path.name).file
        self.assertEqual(info.size, 7082)
        self.assertEqual(info.type, 'image/jpeg')
        # width and height are zero as test image has no exif info
        self.assertEqual(info.width, 0)
        self.assertEqual(info.height, 0)
        # delete file
        self.camera.file_delete(path.folder, path.name)
        # capture preview
        with self.assertRaises(gp.GPhoto2Error) as cm:
            self.camera.capture_preview()
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR_NOT_SUPPORTED)

    def test_c_style(self):
        def list_config(widget):
            OK, label = gp.gp_widget_get_label(widget)
            self.assertEqual(OK, gp.GP_OK)
            OK, name = gp.gp_widget_get_name(widget)
            self.assertEqual(OK, gp.GP_OK)
            result = ['{} ({})'.format(label, name)]
            OK, widget_type = gp.gp_widget_get_type(widget)
            self.assertEqual(OK, gp.GP_OK)
            if widget_type in (gp.GP_WIDGET_WINDOW, gp.GP_WIDGET_SECTION):
                for idx in range(gp.gp_widget_count_children(widget)):
                    OK, child = gp.gp_widget_get_child(widget, idx)
                    self.assertEqual(OK, gp.GP_OK)
                    result += list_config(child)
            return result

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
        # get_config
        OK, widget = gp.gp_camera_get_config(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        config_list = list_config(widget)
        self.assertEqual(len(config_list), 31)
        self.assertEqual(
            config_list[0], 'Camera and Driver Configuration (main)')
        # list_files
        files = list_files()
        self.assertEqual(files[0], '/store_00010001/copyright-free-image.jpg')
        # file_get
        OK, file = gp.gp_camera_file_get(
            self.camera, '/store_00010001', 'copyright-free-image.jpg',
            gp.GP_FILE_TYPE_NORMAL)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(file, gp.CameraFile)
        # capture
        OK, path = gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE)
        self.assertEqual(OK, gp.GP_OK)
        self.assertRegex(path.name, 'GPH_\d{4}.JPG')
        self.assertRegex(path.folder, '/store_00010001/DCIM/\d{3}GPHOT')
        OK, info = gp.gp_camera_file_get_info(
            self.camera, path.folder, path.name)
        self.assertEqual(OK, gp.GP_OK)
        info = info.file
        self.assertEqual(info.size, 7082)
        self.assertEqual(info.type, 'image/jpeg')
        # width and height are zero as test image has no exif info
        self.assertEqual(info.width, 0)
        self.assertEqual(info.height, 0)
        # delete file
        self.assertEqual(gp.gp_camera_file_delete(
            self.camera, path.folder, path.name), gp.GP_OK)
        # capture preview
        OK, path = gp.gp_camera_capture_preview(self.camera)
        self.assertEqual(OK, gp.GP_ERROR_NOT_SUPPORTED)


if __name__ == "__main__":
    unittest.main()
