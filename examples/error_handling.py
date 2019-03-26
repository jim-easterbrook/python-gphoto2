#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-19  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

# demonstrate Python handling of libgphoto2 errors
# needs to run with no camera connected

from __future__ import print_function

import logging
import sys

import gphoto2 as gp

def main():
    def callback(level, domain, string, data=None):
        print('Callback: level =', level, ', domain =', domain, ', string =', string)
        if data:
            print('Callback data:', data)
    camera = gp.Camera()
    # add our own callback
    print('Using Python callback')
    print('=====================')
    callback_obj = gp.check_result(
        gp.gp_log_add_func(gp.GP_LOG_VERBOSE, callback))
    print('callback_obj', callback_obj)
    # create an error
    gp.gp_camera_init(camera)
    # uninstall callback
    del callback_obj
    # add our own callback, with data
    print('Using Python callback, with data')
    print('================================')
    callback_obj = gp.check_result(
        gp.gp_log_add_func(gp.GP_LOG_VERBOSE, callback, 'some data'))
    print('callback_obj', callback_obj)
    # create an error
    gp.gp_camera_init(camera)
    # uninstall callback
    del callback_obj
    # set gphoto2 to use Python's logging directly
    print('Using Python logging')
    print('====================')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    # create an error
    gp.gp_camera_init(camera)
    return 0

if __name__ == "__main__":
    sys.exit(main())
