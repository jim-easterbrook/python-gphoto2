# This file was automatically generated by SWIG (https://www.swig.org).
# Version 4.3.0
#
# Do not make changes to this file unless you know what you are doing - modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
# Pull in all the attributes from the low-level C/C++ module
if __package__ or "." in __name__:
    from ._result import *
else:
    from _result import *


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


