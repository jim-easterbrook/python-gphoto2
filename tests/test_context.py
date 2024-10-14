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

from collections import defaultdict
import os
import sys
import unittest

import gphoto2 as gp

path = os.path.dirname(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.insert(0, path)
from tests.vcamera import has_vcam, use_vcam


@unittest.skipUnless(has_vcam, 'no virtual camera')
class TestContext(unittest.TestCase):
    def setUp(self):
        use_vcam(True)

    def cb_idle(self, context, data):
        self.callback_count['cb_idle'] += 1
        self.assertEqual(data, 'A')

    def cb_error(self, context, text, data):
        self.callback_count['cb_error'] += 1
        self.assertEqual(data, 'B')

    def cb_status(self, context, text, data):
        self.callback_count['cb_status'] += 1
        self.assertEqual(data, 'C')

    def cb_message(self, context, text, data):
        self.callback_count['cb_message'] += 1
        self.assertEqual(data, 'D')

    def cb_question(self, context, text, data):
        self.callback_count['cb_question'] += 1
        self.assertEqual(data, 'E')
        return gp.GP_CONTEXT_FEEDBACK_OK

    def cb_cancel(self, context, data):
        self.callback_count['cb_cancel'] += 1
        self.assertEqual(data, 'F')
        return gp.GP_CONTEXT_FEEDBACK_OK

    def cb_progress_start(self, context, target, text, data):
        self.callback_count['cb_progress_start'] += 1
        self.assertEqual(data, 'G')
        return 123

    def cb_progress_update(self, context, id_, current, data):
        self.callback_count['cb_progress_update'] += 1
        self.assertEqual(data, 'G')
        self.assertEqual(id_, 123)

    def cb_progress_stop(self, context, id_, data):
        self.callback_count['cb_progress_stop'] += 1
        self.assertEqual(id_, 123)

    def test_oo_style(self):
        self.callback_count = defaultdict(int)
        context = gp.Context()
        # set callbacks
        callbacks = []
        callbacks.append(context.set_idle_func(self.cb_idle, 'A'))
        callbacks.append(context.set_error_func(self.cb_error, 'B'))
        callbacks.append(context.set_status_func(self.cb_status, 'C'))
        callbacks.append(context.set_message_func(self.cb_message, 'D'))
        callbacks.append(context.set_question_func(self.cb_question, 'E'))
        callbacks.append(context.set_cancel_func(self.cb_cancel, 'F'))
        callbacks.append(context.set_progress_funcs(
            self.cb_progress_start, self.cb_progress_update,
            self.cb_progress_stop, 'G'))
        for cb in callbacks:
            self.assertIsInstance(cb, gp.CallbackDetails)
        # create a virtual camera
        camera = gp.Camera()
        camera.init(context)
        # call some camera functions which may invoke some callbacks
        text = camera.get_summary(context)
        config = camera.get_config(context)
        path = camera.capture(gp.GP_CAPTURE_IMAGE, context)
        info = camera.file_get_info(path.folder, path.name, context)
        # all done
        camera.exit(context)
        del callbacks
        # check result
        self.assertEqual(self.callback_count['cb_progress_start'], 1)
        self.assertEqual(self.callback_count['cb_progress_stop'], 1)
        self.assertEqual(self.callback_count['cb_progress_update'], 20)
        self.assertEqual(self.callback_count['cb_cancel'], 30)

    def test_c_style(self):
        self.callback_count = defaultdict(int)
        context = gp.gp_context_new()
        # set callbacks
        callbacks = []
        callbacks.append(
            gp.gp_context_set_idle_func(context, self.cb_idle, 'A'))
        callbacks.append(
            gp.gp_context_set_error_func(context, self.cb_error, 'B'))
        callbacks.append(
            gp.gp_context_set_status_func(context, self.cb_status, 'C'))
        callbacks.append(
            gp.gp_context_set_message_func(context, self.cb_message, 'D'))
        callbacks.append(
            gp.gp_context_set_question_func(context, self.cb_question, 'E'))
        callbacks.append(
            gp.gp_context_set_cancel_func(context, self.cb_cancel, 'F'))
        callbacks.append(
            gp.gp_context_set_progress_funcs(
                context, self.cb_progress_start, self.cb_progress_update,
                self.cb_progress_stop, 'G'))
        for cb in callbacks:
            self.assertIsInstance(cb, gp.CallbackDetails)
        # create a virtual camera
        OK, camera = gp.gp_camera_new()
        self.assertEqual(OK, gp.GP_OK)
        self.assertEqual(gp.gp_camera_init(camera, context), gp.GP_OK)
        # call some camera functions which may invoke some callbacks
        OK, text = gp.gp_camera_get_summary(camera, context)
        self.assertEqual(OK, gp.GP_OK)
        OK, config = gp.gp_camera_get_config(camera, context)
        self.assertEqual(OK, gp.GP_OK)
        OK, path = gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE, context)
        self.assertEqual(OK, gp.GP_OK)
        OK, info = gp.gp_camera_file_get_info(
            camera, path.folder, path.name, context)
        self.assertEqual(OK, gp.GP_OK)
        # all done
        self.assertEqual(gp.gp_camera_exit(camera, context), gp.GP_OK)
        del callbacks
        # check result
        self.assertEqual(self.callback_count['cb_progress_start'], 1)
        self.assertEqual(self.callback_count['cb_progress_stop'], 1)
        self.assertEqual(self.callback_count['cb_progress_update'], 20)
        self.assertEqual(self.callback_count['cb_cancel'], 30)


if __name__ == "__main__":
    unittest.main()
