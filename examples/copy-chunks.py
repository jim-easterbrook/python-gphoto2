#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import locale
import logging
import os
import io
import sys

from PIL import Image

import gphoto2 as gp

def list_files(camera, path='/'):
    result = []
    # get files
    for name, value in gp.check_result(
            gp.gp_camera_folder_list_files(camera, path)):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in gp.check_result(
            gp.gp_camera_folder_list_folders(camera, path)):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, os.path.join(path, name)))
    return result

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    print('Getting list of files')
    files = list_files(camera)
    if not files:
        print('No files found')
        return 1
    path = files[0]
    print('Copying %s to memory in 100 kilobyte chunks' % path)
    folder, name = os.path.split(path)
    file_info = gp.check_result(gp.gp_camera_file_get_info(
        camera, folder, name))
    data = bytearray(file_info.file.size)
    view = memoryview(data)
    chunk_size = 100 * 1024
    offset = 0
    while offset < len(data):
        bytes_read = gp.check_result(gp.gp_camera_file_read(
            camera, folder, name, gp.GP_FILE_TYPE_NORMAL,
            offset, view[offset:offset + chunk_size]))
        offset += bytes_read
        print(bytes_read)
    print(' '.join(map(str, data[0:10])))
    image = Image.open(io.BytesIO(data))
    image.show()
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
