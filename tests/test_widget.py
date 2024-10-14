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
import sys
import time
import unittest

import gphoto2 as gp

path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.insert(0, path)
from tests.vcamera import has_vcam, use_vcam


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestWidget(unittest.TestCase):
    def setUp(self):
        use_vcam(True)
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_oo_style(self):
        # test almost every gphoto2.CameraWidget method
        # untested: get_range() & set_range() as no GP_WIDGET_RANGE widget
        config = self.camera.get_config()
        # test top level widget
        self.assertEqual(config.get_label(), 'Camera and Driver Configuration')
        self.assertEqual(config.get_name(), 'main')
        self.assertEqual(config.get_type(), gp.GP_WIDGET_WINDOW)
        self.assertIsInstance(config.get_id(), int)
        self.assertEqual(config.get_info(), '')
        self.assertEqual(config.count_children(), 6)
        # test section widgets
        actions = config.get_child_by_name('actions')
        self.assertEqual(actions.get_parent(), config)
        self.assertEqual(actions, config.get_child(0))
        actions_id = actions.get_id()
        self.assertEqual(actions, config.get_child_by_id(actions_id))
        self.assertEqual(actions.get_type(), gp.GP_WIDGET_SECTION)
        settings = config.get_child_by_name('settings')
        self.assertEqual(settings.get_type(), gp.GP_WIDGET_SECTION)
        self.assertEqual(settings.get_readonly(), 0)
        status = config.get_child_by_name('status')
        self.assertEqual(status.get_type(), gp.GP_WIDGET_SECTION)
        self.assertEqual(status.get_readonly(), 0)
        # test text widget
        widget = actions.get_child_by_label('Set Nikon Control Mode')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_TEXT)
        self.assertEqual(widget.get_value(), '0')
        self.assertEqual(widget.changed(), 0)
        widget.set_value('1')
        self.assertEqual(widget.get_value(), '1')
        self.assertEqual(widget.changed(), 1)
        self.assertEqual(widget.get_root(), config)
        # test toggle widget
        widget = actions.get_child_by_name('bulb')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_TOGGLE)
        self.assertEqual(widget.get_value(), 2)
        self.assertEqual(widget.changed(), 0)
        widget.set_value(0)
        self.assertEqual(widget.get_value(), 0)
        self.assertEqual(widget.changed(), 1)
        # test radio widget
        widget = settings.get_child_by_name('capturetarget')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_RADIO)
        self.assertEqual(widget.count_choices(), 2)
        choices = list(widget.get_choices())
        self.assertEqual(widget.get_choice(0), choices[0])
        self.assertEqual(widget.get_choice(1), choices[1])
        self.assertEqual(widget.get_value(), choices[0])
        self.assertEqual(widget.changed(), 0)
        widget.set_value(choices[1])
        self.assertEqual(widget.get_value(), choices[1])
        widget.set_value(choices[0])
        self.assertEqual(widget.get_value(), choices[0])
        self.assertEqual(widget.changed(), 1)
        widget.set_changed(0)
        self.assertEqual(widget.changed(), 0)
        # test date widget
        widget = settings.get_child_by_name('datetime')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_DATE)
        now = time.time()
        if time.localtime(now).tm_isdst == 1:
            # this needs testing on other time zones
            now -= 3600
        self.assertEqual(widget.get_value(), int(now))
        # test read-only widget
        widget = status.get_child_by_name('batterylevel')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_TEXT)
        self.assertEqual(widget.get_readonly(), 1)
        # store changed config
        self.camera.set_config(config)
        del config
        # test single config
        widget = self.camera.get_single_config('thumbsize')
        self.assertEqual(widget.get_type(), gp.GP_WIDGET_RADIO)
        self.assertEqual(widget.count_choices(), 2)
        choices = list(widget.get_choices())
        self.assertEqual(widget.get_choice(0), choices[0])
        self.assertEqual(widget.get_choice(1), choices[1])
        widget.set_value(choices[1])
        self.assertEqual(widget.get_value(), choices[1])
        self.assertEqual(widget.changed(), 1)
        self.camera.set_single_config('thumbsize', widget)
        del widget

    def test_c_style(self):
        # test almost every gphoto2.CameraWidget method
        # untested: get_range() & set_range() as no GP_WIDGET_RANGE widget
        OK, config = gp.gp_camera_get_config(self.camera)
        self.assertEqual(OK, gp.GP_OK)
        # test top level widget
        self.assertEqual(gp.gp_widget_get_label(config),
                         [gp.GP_OK, 'Camera and Driver Configuration'])
        self.assertEqual(gp.gp_widget_get_name(config), [gp.GP_OK, 'main'])
        self.assertEqual(gp.gp_widget_get_type(config),
                         [gp.GP_OK, gp.GP_WIDGET_WINDOW])
        OK, config_id = gp.gp_widget_get_id(config)
        self.assertEqual(OK, gp.GP_OK)
        self.assertIsInstance(config_id, int)
        self.assertEqual(gp.gp_widget_get_info(config), [gp.GP_OK, ''])
        self.assertEqual(gp.gp_widget_count_children(config), 6)
        # test section widgets
        OK, actions = gp.gp_widget_get_child_by_name(config, 'actions')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_parent(actions), [gp.GP_OK, config])
        self.assertEqual(gp.gp_widget_get_child(config, 0), [gp.GP_OK, actions])
        OK, actions_id = gp.gp_widget_get_id(actions)
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_child_by_id(config, actions_id),
                         [gp.GP_OK, actions])
        self.assertEqual(gp.gp_widget_get_type(actions),
                         [gp.GP_OK, gp.GP_WIDGET_SECTION])
        OK, settings = gp.gp_widget_get_child_by_name(config, 'settings')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(settings),
                         [gp.GP_OK, gp.GP_WIDGET_SECTION])
        self.assertEqual(gp.gp_widget_get_readonly(settings), [gp.GP_OK, 0])
        OK, status = gp.gp_widget_get_child_by_name(config, 'status')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(status),
                         [gp.GP_OK, gp.GP_WIDGET_SECTION])
        self.assertEqual(gp.gp_widget_get_readonly(status), [gp.GP_OK, 0])
        # test text widget
        OK, widget = gp.gp_widget_get_child_by_label(
            actions, 'Set Nikon Control Mode')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_TEXT])
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, '0'])
        self.assertEqual(gp.gp_widget_changed(widget), 0)
        self.assertEqual(gp.gp_widget_set_value(widget, '1'), gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, '1'])
        self.assertEqual(gp.gp_widget_changed(widget), 1)
        self.assertEqual(gp.gp_widget_get_root(widget), [gp.GP_OK, config])
        # test toggle widget
        OK, widget = gp.gp_widget_get_child_by_name(actions, 'bulb')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_TOGGLE])
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, 2])
        self.assertEqual(gp.gp_widget_changed(widget), 0)
        self.assertEqual(gp.gp_widget_set_value(widget, 0), gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, 0])
        self.assertEqual(gp.gp_widget_changed(widget), 1)
        # test radio widget
        OK, widget = gp.gp_widget_get_child_by_name(settings, 'capturetarget')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_RADIO])
        self.assertEqual(gp.gp_widget_count_choices(widget), 2)
        choices = []
        for idx in range(gp.gp_widget_count_choices(widget)):
            OK, choice = gp.gp_widget_get_choice(widget, idx)
            self.assertEqual(OK, gp.GP_OK)
            self.assertIsInstance(choice, str)
            choices.append(choice)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, choices[0]])
        self.assertEqual(gp.gp_widget_changed(widget), 0)
        self.assertEqual(gp.gp_widget_set_value(widget, choices[1]), gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, choices[1]])
        self.assertEqual(gp.gp_widget_changed(widget), 1)
        self.assertEqual(gp.gp_widget_set_value(widget, choices[0]), gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, choices[0]])
        self.assertEqual(gp.gp_widget_changed(widget), 1)
        self.assertEqual(gp.gp_widget_set_changed(widget, 0), gp.GP_OK)
        self.assertEqual(gp.gp_widget_changed(widget), 0)
        # test date widget
        OK, widget = gp.gp_widget_get_child_by_name(settings, 'datetime')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_DATE])
        now = time.time()
        if time.localtime(now).tm_isdst == 1:
            # this needs testing on other time zones
            now -= 3600
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, int(now)])
        # test read-only widget
        OK, widget = gp.gp_widget_get_child_by_name(status, 'batterylevel')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_TEXT])
        self.assertEqual(gp.gp_widget_get_readonly(widget), [gp.GP_OK, 1])
        # store changed config
        self.assertEqual(gp.gp_camera_set_config(self.camera, config), gp.GP_OK)
        del config
        # test single config
        OK, widget = gp.gp_camera_get_single_config(self.camera, 'thumbsize')
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_type(widget),
                         [gp.GP_OK, gp.GP_WIDGET_RADIO])
        self.assertEqual(gp.gp_widget_count_choices(widget), 2)
        choices = []
        for idx in range(gp.gp_widget_count_choices(widget)):
            OK, choice = gp.gp_widget_get_choice(widget, idx)
            self.assertEqual(OK, gp.GP_OK)
            self.assertIsInstance(choice, str)
            choices.append(choice)
        self.assertEqual(gp.gp_widget_set_value(widget, choices[1]), gp.GP_OK)
        self.assertEqual(gp.gp_widget_get_value(widget), [gp.GP_OK, choices[1]])
        self.assertEqual(gp.gp_widget_changed(widget), 1)
        self.assertEqual(gp.gp_camera_set_single_config(
            self.camera, 'thumbsize', widget), gp.GP_OK)
        del widget


if __name__ == "__main__":
    unittest.main()
