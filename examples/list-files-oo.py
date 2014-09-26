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

# "object oriented" version of list-files.py

from __future__ import print_function

from datetime import datetime
import logging
import os
import sys

import gphoto2 as gp

def list_files(camera, context, path='/'):
    result = []
    # get files
    for name, value in camera.folder_list_files(path, context):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path, context):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, context, os.path.join(path, name)))
    return result

def get_file_info(camera, context, path):
    folder, name = os.path.split(path)
    return camera.file_get_info(folder, name, context)

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    context = gp.Context()
    camera = gp.Camera()
    camera.init(context)
    files = list_files(camera, context)
    if not files:
        print('No files found')
        return 1
    print('File list')
    print('=========')
    for path in files[:10]:
        print(path)
    print('...')
    for path in files[-10:]:
        print(path)
    info = get_file_info(camera, context, files[-1])
    print
    print('File info')
    print('=========')
    print('image dimensions:', info.file.width, info.file.height)
    print('image type:', info.file.type)
    print('file mtime:', datetime.fromtimestamp(info.file.mtime).isoformat(' '))
    camera.exit(context)
    return 0

if __name__ == "__main__":
    sys.exit(main())
