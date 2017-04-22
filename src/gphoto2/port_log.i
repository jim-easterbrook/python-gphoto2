// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-17  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

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
#if GPHOTO2_VERSION < 0x020500
static void gp_log_call_python(
    GPLogLevel level, const char *domain, const char *format, va_list args, void *data) {
  char str[1024];
  vsnprintf(str, sizeof(str), format, args);
#else
static void gp_log_call_python(
    GPLogLevel level, const char *domain, const char *str, void *data) {
#endif
  if (Py_IsInitialized()) {
    PyGILState_STATE gstate = PyGILState_Ensure();
    LogFuncItem *this = data;
    PyObject *result = NULL;
    PyObject *arglist = NULL;
    if (this->data)
      arglist = Py_BuildValue("(issO)", level, domain, str, this->data);
    else
      arglist = Py_BuildValue("(iss)", level, domain, str);
    result = PyObject_CallObject(this->func, arglist);
    Py_DECREF(arglist);
    if (result == NULL)
      PyErr_Print();
    else
      Py_DECREF(result);
    PyGILState_Release(gstate);
  }
};
%}

// Add callable check to gp_log_add_func
%typemap(doc)           PyObject *func "$1_name: callable"
%typemap(in, noblock=1) PyObject *func {
  if (!PyCallable_Check($input)) {
    SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
  }
  $1 = $input;
}

// Make data an optional parameter to gp_log_add_func
%typemap(doc)     PyObject *data "$1_name: object (optional)"
%typemap(default) PyObject *data {
  $1 = NULL;
}

// Redefine gp_log_add_func
%ignore gp_log_add_func;
%rename(gp_log_add_func) gp_log_add_func_wrapper;
%inline %{
static int gp_log_add_func_wrapper(GPLogLevel level, PyObject *func, PyObject *data)
{
  LogFuncItem *this = malloc(sizeof(LogFuncItem));
  if (this) {
    int id = gp_log_add_func(level, gp_log_call_python, this);
    if (id >= 0) {
      // Add Python callback to front of func_list
      this->id = id;
      this->func = func;
      this->data = data;
      this->next = func_list;
      func_list = this;
      Py_INCREF(this->func);
      if (this->data)
        Py_INCREF(this->data);
    } else {
      free(this);
    }
    return id;
  } else {
    return GP_ERROR_NO_MEMORY;
  }
}
%}

// Redefine gp_log_remove_func
%ignore gp_log_remove_func;
%rename(gp_log_remove_func) gp_log_remove_func_wrapper;
%inline %{
static int gp_log_remove_func_wrapper(int id)
{
  // Remove Python callback from func_list
  LogFuncItem *last = NULL;
  LogFuncItem *this = func_list;
  while (this) {
    if (this->id == id) {
      Py_DECREF(this->func);
      if (this->data)
        Py_DECREF(this->data);
      if (last)
        last->next = this->next;
      else
        func_list = this->next;
      free(this);
      break;
    }
    last = this;
    this = this->next;
  }
  return gp_log_remove_func(id);
}
%}

// Deprecated older versions
%inline %{
static int gp_log_add_func_py(GPLogLevel level, PyObject *func) {
  int id = gp_log_add_func_wrapper(level, func, NULL);
  gp_log(GP_LOG_ERROR, "gphoto2.port_log",
      "gp_log_add_func_py is deprecated. Please use gp_log_add_func instead.");
  return id;
};

// Remove Python callback from list
static int gp_log_remove_func_py(int id) {
  gp_log(GP_LOG_ERROR, "gphoto2.port_log",
      "gp_log_remove_func_py is deprecated. Please use gp_log_remove_func instead.");
  return gp_log_remove_func_wrapper(id);
};
%}

%include "gphoto2/gphoto2-port-log.h"

%pythoncode %{
import logging

from gphoto2.result import check_result, GP_OK

class _GPhoto2Logger(object):
    def __init__(self):
        self.log = None
        self.log_id = -1
        self.mapping = {}

    def callback(self, level, domain, msg):
        self.log(self.mapping[level], '(%s) %s', domain, msg)

    def install(self, mapping):
        self.mapping.update(mapping)
        if not self.log:
            self.log = logging.getLogger('gphoto2').log
        if self.log_id >= GP_OK:
            check_result(gp_log_remove_func(self.log_id))
        self.log_id = gp_log_add_func(GP_LOG_DATA, self.callback)
        return self.log_id

_gphoto2_logger = None

def use_python_logging(mapping={}):
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    The mapping parameter is a dictionary mapping any of the four
    gphoto2 logging severity levels to a Python logging level.

    """
    global _gphoto2_logger
    if not _gphoto2_logger:
        _gphoto2_logger = _GPhoto2Logger()
    full_mapping = {
        GP_LOG_ERROR   : logging.WARNING,
        GP_LOG_VERBOSE : logging.INFO,
        GP_LOG_DEBUG   : logging.DEBUG,
        GP_LOG_DATA    : logging.DEBUG - 5,
        }
    full_mapping.update(mapping)
    return _gphoto2_logger.install(full_mapping)
%}
