#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from __future__ import print_function

import logging
import os
import six
if six.PY2:
    import StringIO
else:
    import io
import sys

from PIL import Image

import gphoto2 as gp

def list_files(camera, context, path='/'):
    result = []
    # get files
    for name, value in gp.check_result(
            gp.gp_camera_folder_list_files(camera, path, context)):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in gp.check_result(
            gp.gp_camera_folder_list_folders(camera, path, context)):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, context, os.path.join(path, name)))
    return result

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())
    context = gp.gp_context_new()
    gp.check_result(gp.gp_camera_init(camera, context))
    print('Getting list of files')
    files = list_files(camera, context)
    if not files:
        print('No files found')
        return 1
    path = files[0]
    print('Copying %s to memory' % path)
    folder, name = os.path.split(path)
    camera_file = gp.check_result(gp.gp_camera_file_get(
        camera, folder, name, gp.GP_FILE_TYPE_NORMAL, context))
    data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
    print(type(data), len(data))
    if six.PY2:
        print(map(ord, data[0:10]))
        image = Image.open(StringIO.StringIO(data))
    else:
        print(data[0:10])
        image = Image.open(io.BytesIO(data))
    image.show()
    print('After deleting camera_file')
    del camera_file
    print(type(data), len(data))
    if six.PY2:
        print(map(ord, data[0:10]))
    else:
        print(data[0:10])
    gp.check_result(gp.gp_camera_exit(camera, context))
    return 0

if __name__ == "__main__":
    sys.exit(main())
