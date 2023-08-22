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

from datetime import datetime
import locale
import logging
import os
import sys

import gphoto2 as gp

# my Canon dSLR raises an error on every deletion, but still does it OK
gp.error_severity[gp.GP_ERROR] = logging.WARNING

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

def get_file_info(camera, path):
    folder, name = os.path.split(path)
    return camera.file_get_info(folder, name)

def delete_file(camera, path):
    folder, name = os.path.split(path)
    camera.file_delete(folder, name)

def main(argv=None):
    if argv is None:
        argv = sys.argv
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    storage_info = camera.get_storageinfo()
    if len(storage_info) > 1:
        print('Unable to handle camera with multiple storage media')
        return 1
    if len(storage_info) == 0:
        print('No storage info available')
        return 2
    si = storage_info[0]
    if not (si.fields & gp.GP_STORAGEINFO_MAXCAPACITY and
            si.fields & gp.GP_STORAGEINFO_FREESPACEKBYTES):
        print('Cannot read storage capacity')
        return 3
    print('Camera has %.1f%% free space' % (
        100.0 * float(si.freekbytes) / float(si.capacitykbytes)))
    if len(argv) < 2:
        return 4
    if len(argv) > 2:
        print('usage: %s [percent_to_clear]' % argv[0])
        return 5
    target = float(argv[1]) / 100.0
    target = int(target * float(si.capacitykbytes))
    free_space = si.freekbytes
    if free_space >= target:
        print('Sufficient free space')
        return 0
    print('Getting file list...')
    files = list_files(camera)
    mtime = {}
    size = {}
    for path in files:
        info = get_file_info(camera, path)
        mtime[path] = info.file.mtime
        size[path] = info.file.size
    files.sort(key=lambda x: mtime[x], reverse=True)
    while True:
        while files and free_space < target:
            path = files.pop()
            print('Delete', path)
            delete_file(camera, path)
            free_space += size[path] // 1000
        storage_info = camera.get_storageinfo()
        si = storage_info[0]
        print('Camera has %.1f%% free space' % (
            100.0 * float(si.freekbytes) / float(si.capacitykbytes)))
        free_space = si.freekbytes
        if free_space >= target or len(files) == 0:
            break
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
