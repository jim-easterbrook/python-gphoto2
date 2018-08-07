// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-18  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

#ifndef SWIGIMPORTED

// SWIG can't wrap functions with var args
%ignore gp_logv;

// gp_log_xxx functions are not consistent between versions of libgphoto2
// they aren't needed by "front end" programs anyway, so just ignore them
%ignore gp_log_data;
%ignore gp_log_with_source_location;

%{
// Keep list of Python callback function associated with each id
typedef struct LogFuncItem {
  int                id;
  PyObject           *func;
  PyObject           *data;
  struct LogFuncItem *next;
} LogFuncItem;

static LogFuncItem *func_list = NULL;

// Call Python function from C callback
%}
#if GPHOTO2_VERSION < 0x020500
%{
static void gp_log_call_python(GPLogLevel level, const char *domain,
                               const char *format, va_list args, void *data) {
    char str[1024];
    vsnprintf(str, sizeof(str), format, args);
%}
#else
%{
static void gp_log_call_python(GPLogLevel level, const char *domain,
                               const char *str, void *data) {
%}
#endif
%{
    if (!Py_IsInitialized()) {
        return;
    }
    PyGILState_STATE gstate = PyGILState_Ensure();
    LogFuncItem *this = data;
    PyObject *result = NULL;
    PyObject *arglist = NULL;
#if PY_VERSION_HEX >= 0x03000000
    if (this->data) {
        arglist = Py_BuildValue("(iyyO)", level, domain, str, this->data);
    } else {
        arglist = Py_BuildValue("(iyy)", level, domain, str);
    }
#else
    if (this->data) {
        arglist = Py_BuildValue("(issO)", level, domain, str, this->data);
    } else {
        arglist = Py_BuildValue("(iss)", level, domain, str);
    }
#endif
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
// Allocate an empty LogFuncItem and make data optional
%typemap(default) void *data (LogFuncItem *_global_new_func) {
    _global_new_func = malloc(sizeof(LogFuncItem));
    if (!_global_new_func) {
        PyErr_SetNone(PyExc_MemoryError);
        SWIG_fail;
    }
    _global_new_func->id = 0;
    _global_new_func->func = NULL;
    _global_new_func->data = NULL;
    _global_new_func->next = func_list;
    $1 = _global_new_func;
}
// Store Python callback in LogFuncItem and use gp_log_call_python
%typemap(in) GPLogFunc func {
    if (!PyCallable_Check($input)) {
        SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
    }
    _global_new_func->func = $input;
    $1 = gp_log_call_python;
}
// Store user data (if present) in LogFuncItem
%typemap(in) void *data {
    _global_new_func->data = $input;
}
// Add LogFuncItem to func_list if gp_log_add_func succeeded
%exception gp_log_add_func {
    $action
    if (result >= GP_OK) {
        _global_new_func->id = result;
        Py_INCREF(_global_new_func->func);
        if (_global_new_func->data) {
            Py_INCREF(_global_new_func->data);
        }
        func_list = _global_new_func;
        _global_new_func = NULL;
    }
}
// Deallocate LogFuncItem if gp_log_add_func failed
%typemap(freearg) void *data {
    free(_global_new_func);
}

// Note id when gp_log_remove_func is called
%typemap(check) int id (int _global_id) {
    _global_id = $1;
}
// Remove LogFuncItem from func_list if gp_log_remove_func succeeded
%exception gp_log_remove_func {
    $action
    if (result >= GP_OK) {
        LogFuncItem *last = NULL;
        LogFuncItem *this = func_list;
        while (this) {
            if (this->id == _global_id) {
                Py_DECREF(this->func);
                if (this->data) {
                    Py_DECREF(this->data);
                }
                if (last) {
                    last->next = this->next;
                } else {
                    func_list = this->next;
                }
                free(this);
                break;
            }
            last = this;
            this = this->next;
        }
    }
}

%pythoncode %{
import logging

def _gphoto2_logger_cb(level, domain, msg, data):
    log_func, mapping = data
    if level in mapping:
        log_func(mapping[level], '(%s) %s', domain, msg)
    else:
        log_func(logging.ERROR, '%d (%s) %s', level, domain, msg)

def use_python_logging(mapping={}):
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    The return value is an id you can use to remove the logging callback
    with gp_log_remove_func.

    Parameters
    ----------
    * `mapping` :
        a dictionary mapping any of the four gphoto2 logging severity
        levels to a Python logging level. Note that anything below Python
        DEBUG level will not be forwarded.

    Returns
    -------
    an id or a gphoto2 error code.

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

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-port-log.h"
