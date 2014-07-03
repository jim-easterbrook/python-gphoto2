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

from datetime import datetime
import logging
import os
import sys

import gphoto2 as gp

def list_files(camera, path='/'):
    result = []
    folders = []
    with gp.CameraList() as camera_list:
        # get files
        camera.folder_list_files(path, camera_list.list)
        for n in range(camera_list.count()):
            result.append(os.path.join(path, camera_list.get_name(n)))
        # read folders
        camera_list.reset()
        camera.folder_list_folders(path, camera_list.list)
        for n in range(camera_list.count()):
            folders.append(camera_list.get_name(n))
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, os.path.join(path, name)))
    return result

def get_file_info(camera, path):
    folder, name = os.path.split(path)
    info = gp.CameraFileInfo()
    camera.file_get_info(folder, name, info)
    return info

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    with gp.Context() as context:
        with gp.Camera(context.context) as camera:
            camera.init()
            files = list_files(camera)
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
            info = get_file_info(camera, files[-1])
            print
            print('File info')
            print('=========')
            print('image dimensions:', info.file.width, info.file.height)
            print('image type:', info.file.type)
            print('file mtime:', datetime.fromtimestamp(info.file.mtime).isoformat(' '))
            camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
