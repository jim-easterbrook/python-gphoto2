# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import os

import gphoto2 as gp


def _has_vcam():
    vusb_dir = os.environ['IOLIBS'].replace('iolibs', 'vusb')
    if not os.path.isdir(vusb_dir):
        return False
    gp_version = gp.gp_library_version(gp.GP_VERSION_SHORT)[0]
    if gp_version in ('2.5.30',):
        return False
    return True

has_vcam = _has_vcam()
