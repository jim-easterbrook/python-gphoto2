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

import unittest

import gphoto2 as gp


class TestResult(unittest.TestCase):
    def test_result(self):
        for error in (gp.GP_ERROR_MODEL_NOT_FOUND, gp.GP_ERROR_NO_MEMORY):
            with self.assertRaises(gp.GPhoto2Error) as cm:
                gp.check_result(error)
            ex = cm.exception
            self.assertEqual(ex.code, error)
            self.assertEqual(ex.string, gp.gp_result_as_string(error))


if __name__ == "__main__":
    unittest.main()
