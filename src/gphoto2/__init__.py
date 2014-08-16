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

import logging

# make all SWIG objects available at top level
from .lib import *
from .lib import __version__

# result error checking function
class GPhoto2Error(EnvironmentError):
    pass

_return_logger = logging.getLogger('gphoto2.returnvalue')

def check_result(result):
    if not isinstance(result, (tuple, list)):
        error = result
    elif len(result) == 2:
        error, result = result
    else:
        error = result[0]
        result = result[1:]
    if error in (GP_ERROR_IO_USB_CLAIM,
                 GP_ERROR_IO_USB_FIND,
                 GP_ERROR_MODEL_NOT_FOUND):
        raise GPhoto2Error(error, gp_result_as_string(error))
    elif error < 0:
        _return_logger.error('[%d] %s', error, gp_result_as_string(error))
    return result

# define some higher level Python classes
class Context(object):
    """Context helper class.

    Wraps all gp_*(..., context) function calls. For example
        gp_camera_autodetect(list, context)
    becomes
        Context.camera_autodetect(list)

    The context attribute stores the low-level GPContext object
    created by the helper class.
    
    """
    def __init__(self, use_python_logging=True):
        """Constructor.

        Arguments:
        use_python_logging -- should errors be logged via Python's
        logging package.

        """
        if use_python_logging:
            check_result(lib.use_python_logging())
        self.context = gp_context_new()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result(
            (self._next_call)(*(arg + (self.context,))))

class Camera(object):
    """Camera helper class.

    Wraps all gp_camera_*(camera, ..., context) function calls. For
    example
        gp_camera_folder_list_files(camera, folder, list, context)
    becomes
        Camera.list_files(folder, list)

    The camera attribute stores the low-level Camera object created by the
    helper class.
    
    """
    def __init__(self, context):
        """Constructor.

        Arguments:
        context -- a GPContext object.

        """
        self.context = context
        self.camera = check_result(gp_camera_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_camera_%s' % name)
        if name in ('get_abilities',  'set_abilities',
                    'get_port_info',  'set_port_info',
                    'get_port_speed', 'set_port_speed',
                    'start_timeout',  'stop_timeout',   'set_timeout_funcs'):
            return self._call_no_context
        return self._call

    def _call(self, *arg):
        return check_result(
            (self._next_call)(self.camera, *(arg + (self.context,))))

    def _call_no_context(self, *arg):
        return check_result((self._next_call)(self.camera, *arg))

class CameraWidget(object):
    """CameraWidget helper class.

    Wraps all gp_widget_*(widget, ...) function calls. For example
        gp_widget_get_child(widget, child_number)
    becomes
        CameraWidget.get_child(child_number)

    The widget attribute stores the low-level CameraWidget object.
    
    """
    def __init__(self, widget):
        """Constructor.

        Arguments: widget -- a CameraWidget object, e.g. as returned
        by gp_camera_get_config.

        """
        self.widget = widget

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_widget_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.widget, *arg))

class CameraFile(object):
    """CameraFile helper class.

    Wraps all gp_file_*(file, ...) function calls. For example
        gp_file_save(file, filename)
    becomes
        CameraFile.save(filename)

    The file attribute stores the low-level CameraFile object created
    by the helper class.
    
    """
    def __init__(self):
        self.file = check_result(gp_file_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_file_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.file, *arg))

class CameraAbilitiesList(object):
    """CameraAbilitiesList helper class.

    Wraps all gp_abilities_list_*(list, ...) function calls. For example
        gp_abilities_list_lookup_model(list, model)
    becomes
        CameraAbilitiesList.lookup_model(model)

    The list attribute stores the low-level CameraAbilitiesList object
    created by the helper class.
    
    """
    def __init__(self):
        self.list = check_result(gp_abilities_list_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_abilities_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.list, *arg))

class CameraList(object):
    """CameraList helper class.

    Wraps all gp_list_*(list, ...) function calls. For example
        gp_list_get_name(list, index)
    becomes
        CameraList.get_name(index)

    The list attribute stores the low-level CameraList object created
    by the helper class.
    
    """
    def __init__(self):
        self.list = check_result(gp_list_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.list, *arg))

class PortInfoList(object):
    """PortInfoList helper class.

    Wraps all gp_port_info_list_*(list, ...) function calls. For example
        gp_port_info_list_lookup_path(list, path)
    becomes
        PortInfoList.lookup_path(path)

    The list attribute stores the low-level GPPortInfoList object
    created by the helper class.
    
    """
    def __init__(self):
        self.list = check_result(gp_port_info_list_new())

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_port_info_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self.list, *arg))
