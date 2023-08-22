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

import locale
import logging
import sys
import time

import gphoto2 as gp

def set_datetime(config, model):
    if model == 'Canon EOS 100D':
        OK, date_config = gp.gp_widget_get_child_by_name(config, 'datetimeutc')
        if OK >= gp.GP_OK:
            now = int(time.time())
            date_config.set_value(now)
            return True
    OK, sync_config = gp.gp_widget_get_child_by_name(config, 'syncdatetime')
    if OK >= gp.GP_OK:
        sync_config.set_value(1)
        return True
    OK, date_config = gp.gp_widget_get_child_by_name(config, 'datetime')
    if OK >= gp.GP_OK:
        widget_type = date_config.get_type()
        if widget_type == gp.GP_WIDGET_DATE:
            now = int(time.time())
            date_config.set_value(now)
        else:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            date_config.set_value(now)
        return True
    return False

def main():
    locale.setlocale(locale.LC_ALL, '')
    # use Python logging
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    # open camera connection
    camera = gp.Camera()
    camera.init()
    # get camera details
    abilities = camera.get_abilities()
    # get configuration tree
    config = camera.get_config()
    # find the date/time setting config item and set it
    if set_datetime(config, abilities.model):
        # apply the changed config
        camera.set_config(config)
    else:
        print('Could not set date & time')
    # clean up
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
