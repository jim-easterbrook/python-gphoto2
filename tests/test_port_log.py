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

import logging
import sys
import unittest

import gphoto2 as gp
from gphoto2.port_log import _gphoto2_logger_cb


class TestPortLog(unittest.TestCase):
    def callback(self, level, domain, string, data):
        self.assertEqual(level, gp.GP_LOG_DEBUG)
        self.assertEqual(domain, 'domain')
        self.assertEqual(string, 'string')
        self.assertEqual(data, 'data')

    def test_oo_style(self):
        callback = gp.Log.add_func(gp.GP_LOG_DEBUG, self.callback, 'data')
        gp.gp_log(gp.GP_LOG_DEBUG, 'domain', 'string')
        del callback
        gp.gp_log(gp.GP_LOG_DEBUG, 'wrong', 'wrong')

    def test_c_style(self):
        OK, callback = gp.gp_log_add_func(
            gp.GP_LOG_DEBUG, self.callback, 'data')
        self.assertGreaterEqual(OK, gp.GP_OK)
        gp.gp_log(gp.GP_LOG_DEBUG, 'domain', 'string')
        del callback
        gp.gp_log(gp.GP_LOG_DEBUG, 'wrong', 'wrong')

    def test_use_python_logging(self):
        self.assertEqual(sys.getrefcount(_gphoto2_logger_cb), 3)
        # test default mapping
        # GP_LOG_DATA maps to DEBUG - 5 which self.assertLogs doesn't handle
        OK, callbacks = gp.use_python_logging()
        self.assertGreaterEqual(OK, gp.GP_OK)
        self.assertEqual(sys.getrefcount(_gphoto2_logger_cb), 4)
        with self.assertLogs('gphoto2', logging.DEBUG):
            gp.gp_log(gp.GP_LOG_DEBUG, 'debug', 'debug_message')
        with self.assertLogs('gphoto2', logging.INFO):
            gp.gp_log(gp.GP_LOG_VERBOSE, 'verbose', 'verbose_message')
        with self.assertLogs('gphoto2', logging.WARNING):
            gp.gp_log(gp.GP_LOG_ERROR, 'error', 'error_message')
        del callbacks
        self.assertEqual(sys.getrefcount(_gphoto2_logger_cb), 3)
        # test custom mapping
        OK, callbacks = gp.use_python_logging(mapping={
            gp.GP_LOG_ERROR   : logging.CRITICAL,
            gp.GP_LOG_VERBOSE : logging.ERROR,
            gp.GP_LOG_DEBUG   : logging.WARNING,
            gp.GP_LOG_DATA    : logging.WARNING})
        self.assertGreaterEqual(OK, gp.GP_OK)
        with self.assertLogs('gphoto2') as cm:
            gp.gp_log(gp.GP_LOG_DATA, 'data', 'data_message')
            gp.gp_log(gp.GP_LOG_DEBUG, 'debug', 'debug_message')
            gp.gp_log(gp.GP_LOG_VERBOSE, 'verbose', 'verbose_message')
            gp.gp_log(gp.GP_LOG_ERROR, 'error', 'error_message')
        self.assertEqual(cm.output, ['WARNING:gphoto2:(data) data_message',
                                     'WARNING:gphoto2:(debug) debug_message',
                                     'ERROR:gphoto2:(verbose) verbose_message',
                                     'CRITICAL:gphoto2:(error) error_message'])


if __name__ == "__main__":
    unittest.main()
