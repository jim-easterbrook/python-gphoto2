#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2020  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from __future__ import print_function

import sys

import gphoto2 as gp


def main():
    print('python:', sys.version)
    print('libgphoto2:', gp.gp_library_version(gp.GP_VERSION_VERBOSE))
    print('libgphoto2_port:', gp.gp_port_library_version(gp.GP_VERSION_VERBOSE))
    print('python-gphoto2:', gp.__version__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
