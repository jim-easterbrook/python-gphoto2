#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from datetime import datetime
import locale
import logging
import os
import sys

import gphoto2 as gp

PHOTO_DIR = os.path.expanduser('~/Pictures/from_camera')

def get_target_dir(timestamp):
    return os.path.join(PHOTO_DIR, timestamp.strftime('%Y/%Y_%m_%d/'))

def list_computer_files():
    result = []
    for root, dirs, files in os.walk(os.path.expanduser(PHOTO_DIR)):
        for name in files:
            if '.thumbs' in dirs:
                dirs.remove('.thumbs')
            if name in ('.directory',):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in ('.db',):
                continue
            result.append(os.path.join(root, name))
    return result

def list_camera_files(camera, path='/'):
    result = []
    # get files
    gp_list = camera.folder_list_files(path)
    for name in gp_list.keys():
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    gp_list = camera.folder_list_folders(path)
    for name in gp_list.keys():
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_camera_files(camera, os.path.join(path, name)))
    return result

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    computer_files = list_computer_files()
    camera = gp.Camera()
    camera.init()
    print('Getting list of files from camera...')
    camera_files = list_camera_files(camera)
    if not camera_files:
        print('No files found')
        return 1
    print('Copying files...')
    for path in camera_files:
        folder, name = os.path.split(path)
        info = camera.file_get_info(folder, name)
        timestamp = datetime.fromtimestamp(info.file.mtime)
        dest_dir = get_target_dir(timestamp)
        dest = os.path.join(dest_dir, name)
        if dest in computer_files:
            continue
        print('%s -> %s' % (path, dest_dir))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        camera_file = camera.file_get(folder, name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(dest)
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
