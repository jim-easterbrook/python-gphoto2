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
import sys
import time

import gphoto2 as gp

def main():
    locale.setlocale(locale.LC_ALL, '')
    # use Python logging
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    # open camera connection
    camera = gp.Camera()
    camera.init()
    # get configuration tree
    config = camera.get_config()
    # find the date/time setting config item and get it
    # name varies with camera driver
    #   Canon EOS350d - 'datetime'
    #   PTP - 'd034'
    for name, fmt in (('datetime', '%Y-%m-%d %H:%M:%S'),
                      ('d034',     None)):
        now = datetime.now()
        OK, datetime_config = gp.gp_widget_get_child_by_name(config, name)
        if OK >= gp.GP_OK:
            widget_type = datetime_config.get_type()
            raw_value = datetime_config.get_value()
            if widget_type == gp.GP_WIDGET_DATE:
                camera_time = datetime.fromtimestamp(raw_value)
            else:
                if fmt:
                    camera_time = datetime.strptime(raw_value, fmt)
                else:
                    camera_time = datetime.utcfromtimestamp(float(raw_value))
            print('Camera clock:  ', camera_time.isoformat(' '))
            print('Computer clock:', now.isoformat(' '))
            err = now - camera_time
            if err.days < 0:
                err = -err
                lead_lag = 'ahead'
                print('Camera clock is ahead by',)
            else:
                lead_lag = 'behind'
            print('Camera clock is %s by %d days and %d seconds' % (
                lead_lag, err.days, err.seconds))
            break
    else:
        print('Unknown date/time config item')
    # clean up
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
