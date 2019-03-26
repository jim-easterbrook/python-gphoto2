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

import logging
import sys
import time

import gphoto2 as gp

def set_datetime(config, model):
    if model == 'Canon EOS 100D':
        OK, date_config = gp.gp_widget_get_child_by_name(config, 'datetimeutc')
        if OK >= gp.GP_OK:
            now = int(time.time())
            gp.check_result(gp.gp_widget_set_value(date_config, now))
            return True
    OK, sync_config = gp.gp_widget_get_child_by_name(config, 'syncdatetime')
    if OK >= gp.GP_OK:
        gp.check_result(gp.gp_widget_set_value(sync_config, 1))
        return True
    OK, date_config = gp.gp_widget_get_child_by_name(config, 'datetime')
    if OK >= gp.GP_OK:
        widget_type = gp.check_result(gp.gp_widget_get_type(date_config))
        if widget_type == gp.GP_WIDGET_DATE:
            now = int(time.time())
            gp.check_result(gp.gp_widget_set_value(date_config, now))
        else:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            gp.check_result(gp.gp_widget_set_value(date_config, now))
        return True
    return False

def main():
    # use Python logging
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    # open camera connection
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    # get camera details
    abilities = gp.check_result(gp.gp_camera_get_abilities(camera))
    # get configuration tree
    config = gp.check_result(gp.gp_camera_get_config(camera))
    # find the date/time setting config item and set it
    if set_datetime(config, abilities.model):
        # apply the changed config
        gp.check_result(gp.gp_camera_set_config(camera, config))
    else:
        print('Could not set date & time')
    # clean up
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
