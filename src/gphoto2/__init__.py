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

# Define GPhoto2Error before importing sub-modules, as they import GPhoto2Error
class GPhoto2Error(Exception):
    """Exception raised by gphoto2 library errors

    Attributes:
        code   (int): the gphoto2 error code
        string (str): corresponding error message
    """
    def __init__(self, code):
        string = gp_result_as_string(code)
        Exception.__init__(self, '[%d] %s' % (code, string))
        self.code = code
        self.string = string

# make all SWIG objects available at top level
from .lib import *
from .lib import __version__

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
        raise GPhoto2Error(error)
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
