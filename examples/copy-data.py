#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import io
import locale
import logging
import os
import six
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
    print('Copying %s to memory' % path)
    folder, name = os.path.split(path)
    camera_file = gp.check_result(gp.gp_camera_file_get(
        camera, folder, name, gp.GP_FILE_TYPE_NORMAL))
##    # read file data using 'slurp' and a buffer allocated in Python
##    info = gp.check_result(
##        gp.gp_camera_file_get_info(camera, folder, name))
##    file_data = bytearray(info.file.size)
##    count = gp.check_result(gp.gp_file_slurp(camera_file, file_data))
##    print(count, 'bytes read')
    # or read data using 'get_data_and_size' which allocates its own buffer
    file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
    data = memoryview(file_data)
    print(type(data), len(data))
    print(data[:10].tolist())
    image = Image.open(io.BytesIO(file_data))
    image.show()
    print('After deleting camera_file and file_data')
    del camera_file, file_data
    print(type(data), len(data))
    print(data[:10].tolist())
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
