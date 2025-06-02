# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023-24  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import os

import gphoto2 as gp


def use_vcam(enable):
    if 'IOLIBS' not in os.environ:
        return
    if enable:
        os.environ['VCAMERADIR'] = os.path.join(
            os.path.dirname(__file__), 'vcamera')
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')
    else:
        # switch from virtual camera to normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('vusb', 'iolibs')


def _has_vcam():
    if 'IOLIBS' not in os.environ:
        return False
    vusb_dir = os.environ['IOLIBS'].replace('iolibs', 'vusb')
    if not os.path.isdir(vusb_dir):
        return False
    gp_version = gp.gp_library_version(gp.GP_VERSION_SHORT)[0]
    gp_version = tuple(int(x) for x in gp_version.split('.'))
    if gp_version > (2, 5, 30):
        return True
    return False

has_vcam = _has_vcam()
