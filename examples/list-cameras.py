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

import logging
import sys

import gphoto2 as gp

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    cameras = gp.check_result(gp.gp_list_new())
    context = gp.gp_context_new()
    cam_count = gp.check_result(gp.gp_camera_autodetect(cameras, context))
    assert cam_count == gp.gp_list_count(cameras)
    for n in range(gp.gp_list_count(cameras)):
        print 'camera number', n
        print '==============='
        print gp.check_result(gp.gp_list_get_name(cameras, n))
        print gp.check_result(gp.gp_list_get_value(cameras, n))
        print
    gp.gp_list_unref(cameras)
    return 0

if __name__ == "__main__":
    sys.exit(main())
