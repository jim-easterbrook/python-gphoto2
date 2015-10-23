#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from datetime import datetime
import io
import logging
import os
import sys

import exifread
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

class PseudoFile(object):
    def __init__(self, camera, context, path):
        self._camera = camera
        self._context = context
        self._folder, self._file_name = os.path.split(path)
        info = self._camera.file_get_info(
            self._folder, self._file_name, self._context)
        self._size = info.file.size
        self._ptr = 0
        self._buf = bytearray(16 * 1024)
        self._buf_ptr = 0
        self._buf_len = 0

    def read(self, size=None):
        if size is None or size < 0:
            size = self._size - self._ptr
        if (self._ptr < self._buf_ptr or
                self._ptr >= self._buf_ptr + self._buf_len):
            self._buf_ptr = self._ptr - (self._ptr % len(self._buf))
            self._buf_len = self._camera.file_read(
                self._folder, self._file_name, gp.GP_FILE_TYPE_NORMAL,
                self._buf_ptr, self._buf, self._context)
        offset = self._ptr - self._buf_ptr
        size = min(size, self._buf_len - offset)
        self._ptr += size
        return self._buf[offset:offset + size]

    def seek(self, offset, whence=0):
        if whence == 0:
            self._ptr = offset
        elif whence == 1:
            self._ptr += offset
        else:
            self._ptr = self._size - ptr

    def tell(self):
        return self._ptr

def get_file_exif(camera, context, path):
    pf = PseudoFile(camera, context, path)
    return exifread.process_file(pf)

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
    print()
    print('Exif data')
    print('=========')
    for path in files:
        if os.path.splitext(path)[1].lower() != '.jpg':
            continue
        exif = get_file_exif(camera, context, path)
        for key in ('EXIF DateTimeOriginal', 'EXIF LensModel', 'Image Copyright'):
            if key in exif:
                print(key, ':', exif[key])
        break
    print()
    camera.exit(context)
    return 0

if __name__ == "__main__":
    sys.exit(main())
