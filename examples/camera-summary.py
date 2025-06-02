#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2019-25  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

# "object oriented" version of camera-summary.py

import locale
import logging
import sys

import gphoto2 as gp

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    text = camera.get_summary()
    print('Summary')
    print('=======')
    print(str(text))
    print('Config')
    print('======')
    config_items = camera.list_config()
    config_root = camera.get_config()
    for n in range(len(config_items)):
        name = config_items.get_name(n)
        try:
            config = config_root.get_child_by_name(name)
            print(name, config.get_value())
        except gp.GPhoto2Error as ex:
            print(name, 'Error:', str(ex))
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
