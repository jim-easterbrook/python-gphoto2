# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

# make all SWIG objects available at top level
from .lib import *

# define some higher level Python classes
class Context(object):
    def __init__(self, use_python_logging=True):
        if use_python_logging:
            check_result(lib.use_python_logging())
        self.context = gp_context_new()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result(
            (self._next_call)(*(arg + (self.context,))))

    def cleanup(self):
        gp_context_unref(self.context)

class Camera(object):
    def __init__(self, context):
        self.context = context
        self.camera = check_result(gp_camera_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_camera_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result(
            (self._next_call)(self.camera, *(arg + (self.context,))))

    def cleanup(self):
        check_result(gp_camera_unref(self.camera))

class CameraWidget(object):
    def __init__(self, widget):
        self.widget = widget

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_widget_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.widget, *arg))

    def cleanup(self):
        check_result(gp_widget_unref(self.widget))

class CameraList(object):
    def __init__(self):
        self.list = check_result(gp_list_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.cleanup()

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.list, *arg))

    def cleanup(self):
        check_result(gp_list_unref(self.list))
