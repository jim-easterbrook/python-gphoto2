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

# "object oriented" version of camera-summary.py

from __future__ import print_function

import logging
import six
import sys

import gphoto2 as gp

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    context = gp.Context()
    # make a list of all available cameras
    camera_list = []
    for name, addr in context.camera_autodetect():
        camera_list.append((name, addr))
    if not camera_list:
        print('No camera detected')
        return 1
    camera_list.sort(key=lambda x: x[0])
    # ask user to choose one
    for index, (name, addr) in enumerate(camera_list):
        print('{:d}:  {:s}  {:s}'.format(index, addr, name))
    if six.PY3:
        choice = input('Please input number of chosen camera: ')
    else:
        choice = raw_input('Please input number of chosen camera: ')
    try:
        choice = int(choice)
    except ValueError:
        print('Integer values only!')
        return 2
    if choice < 0 or choice >= len(camera_list):
        print('Number out of range')
        return 3
    # initialise chosen camera
    name, addr = camera_list[choice]
    camera = gp.Camera()
    # search ports for camera port name
    port_info_list = gp.PortInfoList()
    port_info_list.load()
    idx = port_info_list.lookup_path(addr)
    camera.set_port_info(port_info_list[idx])
    camera.init(context)
    text = camera.get_summary(context)
    print('Summary')
    print('=======')
    print(str(text))
    camera.exit(context)
    return 0

if __name__ == "__main__":
    sys.exit(main())
