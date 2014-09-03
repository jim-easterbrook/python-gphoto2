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

class GPhoto2Error(EnvironmentError):
    """Raised by check_result if error_severity[error] >=
    error_exception"""
    pass

_return_logger = logging.getLogger('gphoto2.returnvalue')

error_severity = {
    GP_ERROR_CANCEL           : logging.INFO,
    GP_ERROR_DIRECTORY_EXISTS : logging.WARNING,
    }
error_exception = logging.ERROR

def check_result(result):
    """Pops gphoto2 'error' value from 'result' list and checks it.

    If there is no error the remaining result is returned. For other
    errors a severity level is taken from the error_severity dict, or
    set to logging.CRITICAL if the error is not in error_severity.

    If the severity >= error_severity an exception is raised.
    Otherwise a message is logged at the appropriate severity level.
    """

    if not isinstance(result, (tuple, list)):
        error = result
    elif len(result) == 2:
        error, result = result
    else:
        error = result[0]
        result = result[1:]
    if error >= GP_OK:
        return result
    severity = logging.CRITICAL
    if error in error_severity:
        severity = error_severity[error]
    if severity >= error_exception:
        raise GPhoto2Error(error, gp_result_as_string(error))
    _return_logger.log(severity, '[%d] %s', error, gp_result_as_string(error))
    return result

_logger = None

def use_python_logging():
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    """
    def python_logging_callback(level, domain, msg):
      if level == GP_LOG_ERROR:
        lvl = logging.ERROR
      elif level == GP_LOG_VERBOSE:
        lvl = logging.INFO
      else:
        lvl = logging.DEBUG
      _logger(lvl, '(%s) %s', domain, msg)

    global _logger
    if _logger:
        return GP_OK
    _logger = logging.getLogger('gphoto2').log
    return gp_log_add_func_py(GP_LOG_DATA, python_logging_callback)

# define some higher level Python classes
class Context(gphoto2_context._GPContext):
    """Context helper class.

    Wraps all gp_*(..., context) function calls. For example
        gp_camera_autodetect(list, context)
    becomes
        Context.camera_autodetect(list)

    The context attribute stores the low-level GPContext object
    created by the helper class.
    
    """
    def __init__(self, with_python_logging=True):
        """Constructor.

        Arguments:
        with_python_logging -- should errors be logged via Python's
        logging package.

        """
        gphoto2_context._GPContext.__init__(self)
        if with_python_logging:
            check_result(use_python_logging())
        self.context = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result(
            (self._next_call)(*(arg + (self,))))

class Camera(gphoto2_camera._Camera):
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
        gphoto2_camera._Camera.__init__(self)
        self.context = context
        self.camera = self

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
            (self._next_call)(self, *(arg + (self.context,))))

    def _call_no_context(self, *arg):
        return check_result((self._next_call)(self, *arg))

class CameraWidget(gphoto2_widget._CameraWidget):
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
        gphoto2_widget._CameraWidget.__init__(self, widget)
        self.widget = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_widget_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self, *arg))

class CameraFile(gphoto2_file._CameraFile):
    """CameraFile helper class.

    Wraps all gp_file_*(file, ...) function calls. For example
        gp_file_save(file, filename)
    becomes
        CameraFile.save(filename)

    The file attribute stores the low-level CameraFile object created
    by the helper class.
    
    """
    def __init__(self):
        gphoto2_file._CameraFile.__init__(self)
        self.file = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_file_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self, *arg))

class CameraAbilitiesList(gphoto2_abilities_list._CameraAbilitiesList):
    """CameraAbilitiesList helper class.

    Wraps all gp_abilities_list_*(list, ...) function calls. For example
        gp_abilities_list_lookup_model(list, model)
    becomes
        CameraAbilitiesList.lookup_model(model)

    The list attribute stores the low-level CameraAbilitiesList object
    created by the helper class.
    
    """
    def __init__(self):
        gphoto2_abilities_list._CameraAbilitiesList.__init__(self)
        self.list = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_abilities_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self, *arg))

class CameraList(gphoto2_list._CameraList):
    """CameraList helper class.

    Wraps all gp_list_*(list, ...) function calls. For example
        gp_list_get_name(list, index)
    becomes
        CameraList.get_name(index)

    The list attribute stores the low-level CameraList object created
    by the helper class.
    
    """
    def __init__(self):
        gphoto2_list._CameraList.__init__(self)
        self.list = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self, *arg))

class PortInfoList(gphoto2_port_info_list._GPPortInfoList):
    """PortInfoList helper class.

    Wraps all gp_port_info_list_*(list, ...) function calls. For example
        gp_port_info_list_lookup_path(list, path)
    becomes
        PortInfoList.lookup_path(path)

    The list attribute stores the low-level GPPortInfoList object
    created by the helper class.
    
    """
    def __init__(self):
        gphoto2_port_info_list._GPPortInfoList.__init__(self)
        self.list = self

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        self._next_call = getattr(lib, 'gp_port_info_list_%s' % name)
        return self._call

    def _call(self, *arg):
        return check_result((self._next_call)(self, *arg))
