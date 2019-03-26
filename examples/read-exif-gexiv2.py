#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

# read just enough of an image to decode the Exif data

from __future__ import print_function

import logging
import os
import sys

from gi.repository import GObject, GExiv2
import gphoto2 as gp

def list_files(camera, path='/'):
    result = []
    # get files
    for name, value in camera.folder_list_files(path):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, os.path.join(path, name)))
    return result

def get_file_exif_normal(camera, path):
    # a 32k buffer is large enough for my Canon EOS 100D and A1100 IS
    # use a bigger buffer if you get "GExiv2: unsupported format" errors
    buf = bytearray(32 * 1024)
    folder, file_name = os.path.split(path)
    camera.file_read(folder, file_name, gp.GP_FILE_TYPE_NORMAL, 0, buf)
    md = GExiv2.Metadata()
    md.open_buf(buf)
    return md

def get_file_exif_metadata(camera, path):
    # this doesn't work for me as from_app1_segment wants a pointer to a
    # single byte but then tries to read beyond it, causing a segfault
    folder, file_name = os.path.split(path)
    cam_file = camera.file_get(
        folder, file_name, gp.GP_FILE_TYPE_EXIF)
    md = GExiv2.Metadata()
    file_data = cam_file.get_data_and_size()
    data = bytes(file_data)
    md.from_app1_segment(data, len(data))
    return md

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
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
    print()
    print('Exif data via GP_FILE_TYPE_NORMAL')
    print('=================================')
    for path in files:
        if os.path.splitext(path)[1].lower() != '.jpg':
            continue
        md = get_file_exif_normal(camera, path)
        for key in ('Exif.Photo.DateTimeOriginal', 'Exif.Image.Model', 'Exif.Image.Copyright'):
            if key in md.get_exif_tags():
                print(key, ':', md.get_tag_string(key))
        break
    print()
    print('Exif data via GP_FILE_TYPE_EXIF')
    print('===============================')
    for path in files:
        if os.path.splitext(path)[1].lower() != '.jpg':
            continue
        md = get_file_exif_metadata(camera, path)
        for key in ('Exif.Photo.DateTimeOriginal', 'Exif.Image.Model', 'Exif.Image.Copyright'):
            if key in md.get_exif_tags():
                print(key, ':', md.get_tag_string(key))
        break
    print()
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
