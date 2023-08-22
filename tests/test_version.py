# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2023  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import unittest

import gphoto2 as gp


class TestVersion(unittest.TestCase):
    def test_version(self):
        version = gp.gp_library_version(gp.GP_VERSION_SHORT)
        self.assertIsInstance(version, list)
        self.assertIsInstance(version[0], str)
        version = gp.gp_port_library_version(gp.GP_VERSION_SHORT)
        self.assertIsInstance(version, list)
        self.assertIsInstance(version[0], str)


if __name__ == "__main__":
    unittest.main()
