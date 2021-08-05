// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-21  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

%module(package="gphoto2") port_log

%include "common/preamble.i"

// Make docstring parameter types more Pythonic
%typemap(doc) enum GPLogLevel "$1_name: $1_type (gphoto2.GP_LOG_ERROR etc.)"

#ifndef SWIGIMPORTED

// Turn on default exception handling
DEFAULT_EXCEPTION

// SWIG can't wrap functions with var args
%ignore gp_logv;

// gp_log_xxx functions are not consistent between versions of libgphoto2
// they aren't needed by "front end" programs anyway, so just ignore them
%ignore gp_log_data;
%ignore gp_log_with_source_location;

// gp_log_remove_func is called when LogFuncItem is deleted
%ignore gp_log_remove_func;

// Object to store details of callback
%ignore LogFuncItem::id;
%ignore LogFuncItem::func;
%ignore LogFuncItem::data;
%ignore del_LogFuncItem;

%inline %{
typedef struct LogFuncItem {
    int      id;
    PyObject *func;
    PyObject *data;
} LogFuncItem;

// call gp_log_remove_func when LogFuncItem object is deleted
static int del_LogFuncItem(struct LogFuncItem *this) {
    int error = GP_OK;
    if (this->id >= 0)
        error = gp_log_remove_func(this->id);
    Py_XDECREF(this->func);
    Py_XDECREF(this->data);
    free(this);
    return error;
};
%}

DEFAULT_DTOR(LogFuncItem, del_LogFuncItem);

// Call Python function from C callback
%{
static void gp_log_call_python(GPLogLevel level, const char *domain,
                               const char *str, void *data) {
    if (!Py_IsInitialized()) {
        return;
    }
    PyGILState_STATE gstate = PyGILState_Ensure();
    LogFuncItem *this = data;
    PyObject *result = NULL;
    PyObject *arglist = NULL;
    if (this->data) {
        arglist = Py_BuildValue("(iyyO)", level, domain, str, this->data);
    } else {
        arglist = Py_BuildValue("(iyy)", level, domain, str);
    }
    if (arglist == NULL) {
        PyErr_Print();
    } else {
        result = PyObject_CallObject(this->func, arglist);
        Py_DECREF(arglist);
        if (result == NULL) {
            PyErr_Print();
        } else {
            Py_DECREF(result);
        }
    }
    PyGILState_Release(gstate);
};
%}

// Use typemaps to replace Python callback & data with gp_log_call_python
%typemap(arginit) GPLogFunc (LogFuncItem *_global_callback) {
    _global_callback = malloc(sizeof(LogFuncItem));
    if (!_global_callback) {
        PyErr_SetNone(PyExc_MemoryError);
        SWIG_fail;
    }
    _global_callback->id = GP_ERROR;
    _global_callback->func = NULL;
    _global_callback->data = NULL;
}
%typemap(freearg) GPLogFunc {
    if (_global_callback)
        del_LogFuncItem(_global_callback);
}
%typemap(in) GPLogFunc {
    if (!PyCallable_Check($input)) {
        %argument_fail(SWIG_TypeError, callable, $symname, $argnum);
    }
    _global_callback->func = $input;
    Py_INCREF(_global_callback->func);
    $1 = gp_log_call_python;
}
%typemap(argout) GPLogFunc {
    _global_callback->id = result;
    $result = SWIG_Python_AppendOutput($result,
        SWIG_NewPointerObj(_global_callback, SWIGTYPE_p_LogFuncItem, SWIG_POINTER_OWN));
    _global_callback = NULL;
}
%typemap(doc) GPLogFunc "$1_name: callable function";

// make data optional and pass LogFuncItem object to gp_log_add_func
%typemap(default) void *data {
    $1 = _global_callback;
}
%typemap(in) void *data {
    _global_callback->data = $input;
    Py_INCREF(_global_callback->data);
}
%typemap(doc) void *data "$1_name: object (default=None)";

// define use_python_logging function
%pythoncode %{
import logging
import sys

def _gphoto2_logger_cb(level, domain, msg, data):
    log_func, mapping = data
    if sys.version_info[0] >= 3:
        # decode bytes to str
        if domain:
            domain = domain.decode(errors='replace')
        if msg:
            msg = msg.decode(errors='replace')
    if level in mapping:
        log_func(mapping[level], '(%s) %s', domain, msg)
    else:
        log_func(logging.ERROR, '%d (%s) %s', level, domain, msg)

def use_python_logging(mapping={}):
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    The return value is a tuple containing an error code and a Python object
    containing details of the callback. Deleting this object will uninstall
    the callback.

    Parameters
    ----------
    * `mapping` :
        a dictionary mapping any of the four gphoto2 logging severity
        levels to a Python logging level. Note that anything below Python
        DEBUG level will not be forwarded.

    Returns
    -------
    a tuple containing an id or error code and a callback reference object.

    """
    full_mapping = {
        GP_LOG_ERROR   : logging.WARNING,
        GP_LOG_VERBOSE : logging.INFO,
        GP_LOG_DEBUG   : logging.DEBUG,
        GP_LOG_DATA    : logging.DEBUG - 5,
        }
    full_mapping.update(mapping)
    log_func = logging.getLogger('gphoto2').log
    for level in (GP_LOG_DATA, GP_LOG_DEBUG, GP_LOG_VERBOSE, GP_LOG_ERROR):
        if full_mapping[level] >= logging.DEBUG:
            break
    return gp_log_add_func(level, _gphoto2_logger_cb, (log_func, full_mapping))
%}

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-port-log.h"
