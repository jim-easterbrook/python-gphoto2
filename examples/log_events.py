#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2018  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

# print events as they are received from a camera

from __future__ import print_function

import sys
from datetime import datetime

import gphoto2 as gp

def main():
    # create event name lookup table (not essential but helps readability)
    ev_name = {}
    for name in ('GP_EVENT_UNKNOWN', 'GP_EVENT_TIMEOUT', 'GP_EVENT_FILE_ADDED',
                 'GP_EVENT_FOLDER_ADDED', 'GP_EVENT_CAPTURE_COMPLETE'):
        ev_name[getattr(gp, name)] = name
    camera = gp.Camera()
    camera.init()
    while True:
        try:
            ev_type, ev_data = camera.wait_for_event(2000)
        except KeyboardInterrupt:
            break
        if not ev_data:
            ev_data = ''
        print(datetime.now().strftime('%H:%M:%S'), ev_name[ev_type], ev_data)
    camera.exit()
    return 0

if __name__ == "__main__":
    sys.exit(main())
