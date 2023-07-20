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
import time
import unittest

os.environ['VCAMERADIR'] = os.path.join(os.path.dirname(__file__), 'vcamera')

import gphoto2 as gp


class TestWidget(unittest.TestCase):
    def setUp(self):
        # switch to virtual camera from normal drivers
        os.environ['IOLIBS'] = os.environ['IOLIBS'].replace('iolibs', 'vusb')
        self.camera = gp.Camera()
        self.camera.init()

    def tearDown(self):
        self.camera.exit()

    def test_single_config(self):
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

    def test_config_tree(self):
        # test almost every gphoto2.CameraWidget method
        # untested: get_range() & set_range() as no GP_WIDGET_RANGE widget
        config = self.camera.get_config()
        # test top level widget
        self.assertEqual(config.get_label(), 'Camera and Driver Configuration')
        self.assertEqual(config.get_name(), 'main')
        self.assertEqual(config.get_type(), gp.GP_WIDGET_WINDOW)
        self.assertEqual(config.get_id(), 31)
        self.assertEqual(config.get_info(), '')
        config.set_info('top')
        self.assertEqual(config.get_info(), 'top')
        config.set_name('Main')
        self.assertEqual(config.get_name(), 'Main')
        self.assertEqual(config.count_children(), 6)
        # test section widgets
        actions = config.get_child_by_name('actions')
        self.assertEqual(actions.get_parent(), config)
        self.assertEqual(actions, config.get_child(0))
        self.assertEqual(actions, config.get_child_by_id(32))
        self.assertEqual(actions.get_type(), gp.GP_WIDGET_SECTION)
        settings = config.get_child_by_name('settings')
        self.assertEqual(settings.get_type(), gp.GP_WIDGET_SECTION)
        self.assertEqual(settings.get_readonly(), 0)
        settings.set_readonly(1)
        self.assertEqual(settings.get_readonly(), 1)
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
        widget.add_choice('Memory Card 2')
        self.assertEqual(widget.count_choices(), 3)
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
        # store changed config
        self.camera.set_config(config)


if __name__ == "__main__":
    unittest.main()
