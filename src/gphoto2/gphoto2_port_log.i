// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") gphoto2_port_log

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

// SWIG can't wrap functions with var args
%ignore gp_logv;

// gp_log_xxx functions are not consistent between versions of libgphoto2
// they aren't needed by "front end" programs anyway, so just ignore them
%ignore gp_log_data;
%ignore gp_log_with_source_location;

// Should not directly call Python from C
%ignore gp_log_add_func;

// List of python callbacks is private
%ignore func_list;
%ignore callback_wrapper_24;
%ignore callback_wrapper_25;
%ignore LogFuncItem;

// Check user supplies a callable Python function
%typemap(in) PyObject *func {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Object not callable");
      return NULL;
  }
  $1 = $input;
}

%inline %{
// General Python function callback
static void callback_wrapper_25(GPLogLevel level, const char *domain,
                                const char *str, void *data) {
  PyGILState_STATE gstate = PyGILState_Ensure();
  PyObject *result = NULL;
  PyObject *arglist = Py_BuildValue("(iss)", level, domain, str);
  result = PyObject_CallObject(data, arglist);
  Py_DECREF(arglist);
  if (result == NULL)
    PyErr_Clear();
  else
    Py_DECREF(result);
  PyGILState_Release(gstate);
};
%}

#ifdef GPHOTO2_24
%inline %{
static void callback_wrapper_24(GPLogLevel level, const char *domain,
                                const char *format, va_list args, void *data) {
  char str[1024];
  vsnprintf(str, sizeof(str), format, args);
  callback_wrapper_25(level, domain, str, data);
};

#define CALLBACK_WRAPPER callback_wrapper_24
%}
#else
%inline %{
#define CALLBACK_WRAPPER callback_wrapper_25
%}
#endif

%inline %{
// Keep list of Python callback function associated with each id
struct LogFuncItem {
  int id;
  PyObject *func;
  struct LogFuncItem *next;
};

static struct LogFuncItem *func_list = NULL;

// Add Python callback to front of list
static int gp_log_add_func_py(GPLogLevel level, PyObject *func) {
  int id = gp_log_add_func(level, CALLBACK_WRAPPER, func);
  if (id >= 0) {
    struct LogFuncItem *list_item = malloc(sizeof(struct LogFuncItem));
    list_item->id = id;
    list_item->func = func;
    list_item->next = func_list;
    func_list = list_item;
    Py_INCREF(func);
    }
  return id;
};

// Remove Python callback from list
static int gp_log_remove_func_py(int id) {
  struct LogFuncItem *last_item = NULL;
  struct LogFuncItem *this_item = func_list;
  while (this_item) {
    if (this_item->id == id) {
      Py_DECREF(this_item->func);
      if (last_item)
        last_item->next = this_item->next;
      else
        func_list = this_item->next;
      free(this_item);
      break;
    }
    last_item = this_item;
    this_item = this_item->next;
  }
  return gp_log_remove_func(id);
};
%}

%pythoncode %{
import logging

from gphoto2.gphoto2_result import check_result, GP_OK

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
        self.log_id = gp_log_add_func_py(GP_LOG_DATA, self.callback)
        return self.log_id

_gphoto2_logger = _GPhoto2Logger()

def use_python_logging(
    mapping = {
        GP_LOG_ERROR   : logging.WARNING,
        GP_LOG_VERBOSE : logging.INFO,
        GP_LOG_DEBUG   : logging.DEBUG,
        GP_LOG_DATA    : logging.DEBUG - 5,
        }):
    """Install a callback to receive gphoto2 errors and forward them
    to Python's logging system.

    The mapping parameter is a dictionary mapping each of the four
    gphoto2 logging severity levels to a Python logging level.

    """
    return _gphoto2_logger.install(mapping)
%}

%include "gphoto2/gphoto2-port-log.h"
