// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This file is part of python-gphoto2.
//
// python-gphoto2 is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// python-gphoto2 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with python-gphoto2.  If not, see <https://www.gnu.org/licenses/>.

%module(package="gphoto2") result

%include "common/preamble.i"

%include "gphoto2/gphoto2-port-result.h"
%include "gphoto2/gphoto2-result.h"

%pythoncode %{
import logging

from gphoto2 import GPhoto2Error

# user adjustable check_result lookup table
error_severity = {
    GP_ERROR_CANCEL           : logging.INFO,
    GP_ERROR_DIRECTORY_EXISTS : logging.WARNING,
    }
error_exception = logging.ERROR

_return_logger = logging.getLogger('gphoto2.returnvalue')

def check_result(result):
    """Pops gphoto2 'error' value from 'result' list and checks it.

    If there is no error the remaining result is returned. For other
    errors a severity level is taken from the error_severity dict, or
    set to logging.CRITICAL if the error is not in error_severity.

    If the severity >= error_exception an exception is raised.
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
%}
