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

import os
import unittest

import gphoto2 as gp


class TestList(unittest.TestCase):
    def test_oo_style(self):
        test_list = gp.CameraList()
        self.assertIsInstance(test_list, gp.CameraList)
        self.assertEqual(len(test_list), 0)
        test_list.append('B', '2')
        test_list.append('A', '1')
        test_list.append('D', None)
        self.assertEqual(len(test_list), 3)
        self.assertEqual(test_list.get_name(0), 'B')
        self.assertEqual(test_list.get_value(0), '2')
        self.assertEqual(test_list.get_name(1), 'A')
        self.assertEqual(test_list.get_value(1), '1')
        self.assertEqual(test_list.get_name(2), 'D')
        self.assertIsNone(test_list.get_value(2))
        self.assertEqual(test_list.find_by_name('B'), 0)
        self.assertEqual(test_list.find_by_name('A'), 1)
        self.assertEqual(test_list.find_by_name('D'), 2)
        with self.assertRaises(gp.GPhoto2Error) as cm:
            test_list.find_by_name('Z')
        ex = cm.exception
        self.assertEqual(ex.code, gp.GP_ERROR)
        keys = test_list.keys()
        self.assertEqual(len(keys), 3)
        self.assertEqual(keys[1], 'A')
        with self.assertRaises(IndexError):
            keys[3]
        self.assertEqual(tuple(keys), ('B', 'A', 'D'))
        self.assertEqual(tuple(test_list.values()), ('2', '1', None))
        self.assertEqual(tuple(test_list.items()),
                         (('B', '2'), ('A', '1'), ('D', None)))
        with self.assertRaises(IndexError):
            test_list[-4]
        self.assertEqual(test_list[-3], ('B', '2'))
        self.assertEqual(test_list[-2], ('A', '1'))
        self.assertEqual(test_list[-1], ('D', None))
        self.assertEqual(test_list[0], ('B', '2'))
        self.assertEqual(test_list[1], ('A', '1'))
        self.assertEqual(test_list[2], ('D', None))
        with self.assertRaises(IndexError):
            test_list[3]
        self.assertEqual(test_list['B'], '2')
        self.assertEqual(test_list['A'], '1')
        with self.assertRaises(KeyError):
            test_list['Z']
        it = iter(test_list)
        self.assertEqual(next(it), test_list[0])
        self.assertEqual(next(it), test_list[1])
        self.assertEqual(next(it), test_list[2])
        with self.assertRaises(StopIteration):
            next(it)
        test_list.sort()
        self.assertEqual(test_list.get_name(0), 'A')
        self.assertEqual(test_list.get_value(0), '1')
        test_list.set_name(0, 'C')
        test_list.set_value(0, '3')
        self.assertEqual(test_list.get_name(0), 'C')
        self.assertEqual(test_list.get_value(0), '3')
        test_list.reset()
        self.assertEqual(len(test_list), 0)

    def test_c_style(self):
        OK, test_list = gp.gp_list_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(test_list, gp.CameraList)
        self.assertEqual(gp.gp_list_count(test_list), 0)
        self.assertEqual(gp.gp_list_append(test_list, 'B', '2'), gp.GP_OK)
        self.assertEqual(gp.gp_list_append(test_list, 'A', '1'), gp.GP_OK)
        self.assertEqual(gp.gp_list_append(test_list, 'D', None), gp.GP_OK)
        self.assertEqual(gp.gp_list_count(test_list), 3)
        self.assertEqual(gp.gp_list_get_name(test_list, 0), [gp.GP_OK, 'B'])
        self.assertEqual(gp.gp_list_get_value(test_list, 0), [gp.GP_OK, '2'])
        self.assertEqual(gp.gp_list_get_name(test_list, 1), [gp.GP_OK, 'A'])
        self.assertEqual(gp.gp_list_get_value(test_list, 1), [gp.GP_OK, '1'])
        self.assertEqual(gp.gp_list_get_name(test_list, 2), [gp.GP_OK, 'D'])
        self.assertEqual(gp.gp_list_get_value(test_list, 2), [gp.GP_OK, None])
        self.assertEqual(gp.gp_list_find_by_name(test_list, 'B'), [gp.GP_OK, 0])
        self.assertEqual(gp.gp_list_find_by_name(test_list, 'A'), [gp.GP_OK, 1])
        self.assertEqual(gp.gp_list_find_by_name(test_list, 'D'), [gp.GP_OK, 2])
        self.assertEqual(
            gp.gp_list_find_by_name(test_list, 'Z'), [gp.GP_ERROR, 0])
        self.assertEqual(gp.gp_list_sort(test_list), gp.GP_OK)
        self.assertEqual(gp.gp_list_get_name(test_list, 0), [gp.GP_OK, 'A'])
        self.assertEqual(gp.gp_list_get_value(test_list, 0), [gp.GP_OK, '1'])
        self.assertEqual(gp.gp_list_set_name(test_list, 0, 'C'), gp.GP_OK)
        self.assertEqual(gp.gp_list_set_value(test_list, 0, '3'), gp.GP_OK)
        self.assertEqual(gp.gp_list_get_name(test_list, 0), [gp.GP_OK, 'C'])
        self.assertEqual(gp.gp_list_get_value(test_list, 0), [gp.GP_OK, '3'])
        self.assertEqual(gp.gp_list_reset(test_list), gp.GP_OK)
        self.assertEqual(gp.gp_list_count(test_list), 0)


if __name__ == "__main__":
    unittest.main()
