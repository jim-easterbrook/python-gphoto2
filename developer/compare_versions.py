#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2017  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import difflib
import os
import sys
import time

def main():
    if len(sys.argv) != 3:
        print('Two arguments required')
        return 1
    root_1 = os.path.join('src', 'swig-gp' + sys.argv[1])
    root_2 = os.path.join('src', 'swig-gp' + sys.argv[2])
    print('Comparing {} and {}'.format(root_1, root_2))
    for root, dirs, files in os.walk(root_1):
        for name in files:
            this = os.path.join(root, name)
            that = os.path.join(root.replace(root_1, root_2), name)
            if not os.path.exists(that):
                print('File {} does not exist'.format(that))
            else:
                this_date = time.ctime(os.stat(this).st_mtime)
                that_date = time.ctime(os.stat(that).st_mtime)
                diff = difflib.unified_diff(
                    open(this).readlines(), open(that).readlines(),
                    this, that, this_date, that_date, n=4)
                sys.stdout.writelines(diff)
    for root, dirs, files in os.walk(root_2):
        for name in files:
            that = os.path.join(root.replace(root_1, root_2), name)
            if not os.path.exists(that):
                print('File {} does not exist'.format(that))
    return 0

if __name__ == '__main__':
    sys.exit(main())
