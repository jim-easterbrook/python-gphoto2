#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2015-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import gphoto2 as gp

def main():
    locale.setlocale(locale.LC_ALL, '')
    # use Python logging
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    # open camera connection
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))
    # get configuration tree
    config = gp.check_result(gp.gp_camera_get_config(camera))
    # find the capture target config item
    capture_target = gp.check_result(
        gp.gp_widget_get_child_by_name(config, 'capturetarget'))
    # print current setting
    value = gp.check_result(gp.gp_widget_get_value(capture_target))
    print('Current setting:', value)
    # print possible settings
    for n in range(gp.check_result(gp.gp_widget_count_choices(capture_target))):
        choice = gp.check_result(gp.gp_widget_get_choice(capture_target, n))
        print('Choice:', n, choice)
    # clean up
    gp.check_result(gp.gp_camera_exit(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
