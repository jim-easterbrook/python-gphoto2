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

def list_files(camera, context, path='/'):
    result = []
    gp_list = gp.check_result(gp.gp_list_new())
    # get files
    gp.check_result(
        gp.gp_camera_folder_list_files(camera, path, gp_list, context))
    for n in range(gp.gp_list_count(gp_list)):
        result.append(os.path.join(
            path, gp.check_result(gp.gp_list_get_name(gp_list, n))))
    # read folders
    folders = []
    gp.check_result(gp.gp_list_reset(gp_list))
    gp.check_result(
        gp.gp_camera_folder_list_folders(camera, path, gp_list, context))
    for n in range(gp.gp_list_count(gp_list)):
        folders.append(gp.check_result(gp.gp_list_get_name(gp_list, n)))
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, context, os.path.join(path, name)))
    return result

def get_file_info(camera, context, path):
    folder, name = os.path.split(path)
    info = gp.CameraFileInfo()
    gp.check_result(
        gp.gp_camera_file_get_info(camera, folder, name, info, context))
    return info

def delete_file(camera, context, path):
    folder, name = os.path.split(path)
    gp.check_result(gp.gp_camera_file_delete(camera, folder, name, context))

def main(argv=None):
    if argv is None:
        argv = sys.argv
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())
    context = gp.gp_context_new()
    gp.check_result(gp.gp_camera_init(camera, context))
    storage_info = gp.check_result(gp.gp_camera_get_storageinfo(camera, context))
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
    files = list_files(camera, context)
    mtime = {}
    size = {}
    for path in files:
        info = get_file_info(camera, context, path)
        mtime[path] = info.file.mtime
        size[path] = info.file.size
    files.sort(key=lambda x: mtime[x], reverse=True)
    while True:
        while files and free_space < target:
            path = files.pop()
            print('Delete', path)
            delete_file(camera, context, path)
            free_space += size[path] // 1000
        storage_info = gp.check_result(
            gp.gp_camera_get_storageinfo(camera, context))
        si = storage_info[0]
        print('Camera has %.1f%% free space' % (
            100.0 * float(si.freekbytes) / float(si.capacitykbytes)))
        free_space = si.freekbytes
        if free_space >= target:
            break
    gp.check_result(gp.gp_camera_exit(camera, context))
    return 0

if __name__ == "__main__":
    sys.exit(main())
