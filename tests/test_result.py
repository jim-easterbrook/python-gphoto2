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

import locale
import os
import platform
import unittest

import gphoto2 as gp


class TestResult(unittest.TestCase):
    def test_exceptions(self):
        for error in (gp.GP_ERROR_MODEL_NOT_FOUND, gp.GP_ERROR_NO_MEMORY):
            with self.assertRaises(gp.GPhoto2Error) as cm:
                gp.check_result(error)
            ex = cm.exception
            self.assertEqual(ex.code, error)
            self.assertEqual(ex.string, gp.gp_result_as_string(error))

    def set_lang(self, lang):
        # setting environ works on Ubuntu, setlocale works on openSUSE
        # using both seems to be harmless
        os.environ['LC_ALL'] = lang
        os.environ['LANG'] = lang
        os.environ['LANGUAGE'] = lang
        # try default locale first
        try:
            if locale.setlocale(locale.LC_MESSAGES, '').startswith(lang):
                return
        except locale.Error:
            pass
        # try all known locales
        for k in locale.locale_alias:
            if k.startswith(lang):
                try:
                    locale.setlocale(
                        locale.LC_MESSAGES, locale.locale_alias[k])
                    return
                except locale.Error:
                    pass
        self.skipTest("failed to set language '{}'".format(lang))

    @unittest.skipIf(platform.system() == 'Darwin',
                     'locale setting fails on MacOS')
    def test_locales(self):
        self.set_lang('de')
        self.assertEqual(gp.gp_result_as_string(gp.GP_ERROR_MODEL_NOT_FOUND),
                         'Unbekanntes Modell')
        self.assertEqual(gp.gp_port_result_as_string(gp.GP_ERROR_NO_MEMORY),
                         'Speicher voll')
        self.set_lang('en')
        self.assertEqual(gp.gp_result_as_string(gp.GP_ERROR_MODEL_NOT_FOUND),
                         'Unknown model')
        self.assertEqual(gp.gp_port_result_as_string(gp.GP_ERROR_NO_MEMORY),
                         'Out of memory')


if __name__ == "__main__":
    unittest.main()
