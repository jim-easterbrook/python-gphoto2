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
import sys

import gphoto2 as gp

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    with gp.Context() as context:
        with gp.CameraList() as cameras:
            if hasattr(gp, 'gp_camera_autodetect'):
                # gphoto2 version 2.5+
                cam_count = context.camera_autodetect(cameras.list)
                assert cam_count == cameras.count()
            else:
                with gp.PortInfoList() as port_info_list:
                    port_info_list.load()
                    with gp.CameraAbilitiesList() as abilities_list:
                        abilities_list.load(context.context)
                        abilities_list.detect(
                            port_info_list.list, cameras.list, context.context)
            for n in range(cameras.count()):
                print('camera number', n)
                print('===============')
                print(cameras.get_name(n))
                print(cameras.get_value(n))
                print
    return 0

if __name__ == "__main__":
    sys.exit(main())
