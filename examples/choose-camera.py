#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-20  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import logging
import sys

import gphoto2 as gp

def main():
    if len(sys.argv) > 2:
        print('Usage: {} [port_address]'.format(sys.argv[0]))
        return 1
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    if len(sys.argv) > 1:
        # if user has given an address open it directly
        addr = sys.argv[1]
    else:
        # make a list of all available cameras
        camera_list = list(gp.Camera.autodetect())
        if not camera_list:
            print('No camera detected')
            return 1
        camera_list.sort(key=lambda x: x[0])
        # ask user to choose one
        for index, (name, addr) in enumerate(camera_list):
            print('{:d}:  {:s}  {:s}'.format(index, addr, name))
        choice = input('Please input number of chosen camera: ')
        try:
            choice = int(choice)
        except ValueError:
            print('Integer values only!')
            return 2
        if choice < 0 or choice >= len(camera_list):
            print('Number out of range')
            return 3
        # use chosen camera
        addr = camera_list[choice][1]
    # get port info and camera abilities
    port_info_list = gp.PortInfoList()
    port_info_list.load()
    abilities_list = gp.CameraAbilitiesList()
    abilities_list.load()
    camera_list = abilities_list.detect(port_info_list)
    if len(camera_list) < 1:
        print('No camera detected')
        return 4
    # choose camera
    camera = gp.Camera()
    idx = port_info_list.lookup_path(addr)
    camera.set_port_info(port_info_list[idx])
    idx = abilities_list.lookup_model(camera_list[0][0])
    camera.set_abilities(abilities_list[idx])
    # do something with camera
    text = camera.get_summary()
    print('Summary')
    print('=======')
    print(str(text))
    try:
        text = camera.get_manual()
        print('Manual')
        print('=======')
        print(str(text))
    except Exception as ex:
        print(str(ex))
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
