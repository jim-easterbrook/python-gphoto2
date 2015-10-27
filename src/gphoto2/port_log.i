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

%module(package="gphoto2") port_log

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

%{
// Call Python function from C callback
#ifdef GPHOTO2_24
static void gp_log_call_python(
    GPLogLevel level, const char *domain, const char *format, va_list args, void *data) {
  char str[1024];
  vsnprintf(str, sizeof(str), format, args);
#else
static void gp_log_call_python(
    GPLogLevel level, const char *domain, const char *str, void *data) {
#endif
  PyGILState_STATE gstate = PyGILState_Ensure();
  PyObject *result = NULL;
  PyObject *arglist = Py_BuildValue("(iss)", level, domain, str);
  result = PyObject_CallObject(data, arglist);
  Py_DECREF(arglist);
  if (result == NULL)
    PyErr_Print();
  else
    Py_DECREF(result);
  PyGILState_Release(gstate);
};
%}

// Import extended int type
%{
static PyObject *AugmentedInt_class = NULL;
%}
%init %{
{
  PyObject *module = PyImport_ImportModule("gphoto2.types");
  if (module != NULL) {
    AugmentedInt_class = PyObject_GetAttrString(module, "AugmentedInt");
    Py_DECREF(module);
  }
  if (AugmentedInt_class == NULL)
#if PY_VERSION_HEX >= 0x03000000
    return NULL;
#else
    return;
#endif
}
%}

// Add callable check to gp_log_add_func_py
%typemap(in) (PyObject *callable) {
  if (!PyCallable_Check($input)) {
    SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
  }
  $1 = $input;
}

// Add gp_log_call_python to gp_log_add_func's parameters
%typemap(in, numinputs=1) (GPLogFunc func, PyObject *callable) () {
  if (!PyCallable_Check($input)) {
    SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
  }
  $1 = gp_log_call_python;
  $2 = $input;
}

// Store a reference to the callable in gp_log_add_func result
%typemap(argout) (GPLogFunc func, PyObject *callable) () {
  if (result >= GP_OK) {
    Py_DECREF($result);
    PyObject *args = Py_BuildValue("(iO)", result, $2);
    $result = PyObject_CallObject(AugmentedInt_class, args);
    Py_DECREF(args);
    Py_INCREF($2); // Add a reference in case user deletes gp_log_add_func result
  }
}

%inline %{
typedef int augmented_int;
%}

// Remove reference to the callable from gp_log_remove_func input
%typemap(in) (augmented_int id) (int val, int ecode = 0) {
  // Check and convert input
  ecode = SWIG_AsVal_int($input, &val);
  if (!SWIG_IsOK(ecode)) {
    SWIG_exception_fail(SWIG_ArgError(ecode), "in method '" "$symname" "', argument " "$argnum"" of type '" "augmented_int""'");
  }
  $1 = (augmented_int)(val);
  // Unref callback if input is an AugmentedInt
  if (PyObject_IsInstance($input, AugmentedInt_class) > 0) {
    PyObject *callable = PyObject_GetAttrString($input, "data");
    Py_DECREF(callable); // Reference added by PyObject_GetAttrString
    Py_DECREF(callable); // Reference added by gp_log_add_func
  }
}

// Redefine signature of gp_log_add_func
augmented_int gp_log_add_func(GPLogLevel level, GPLogFunc func, PyObject *callable);
%ignore gp_log_add_func;

// Redefine signature of gp_log_remove_func
int gp_log_remove_func(augmented_int id);
%ignore gp_log_remove_func;

%{
// Keep list of Python callback function associated with each id
struct LogFuncItem {
  int id;
  PyObject *func;
  struct LogFuncItem *next;
};

static struct LogFuncItem *func_list = NULL;
%}

%inline %{
static int gp_log_add_func_py(GPLogLevel level, PyObject *callable) {
  int id = gp_log_add_func(level, gp_log_call_python, callable);
  if (id >= 0) {
    // Add Python callback to front of func_list
    struct LogFuncItem *list_item = malloc(sizeof(struct LogFuncItem));
    list_item->id = id;
    list_item->func = callable;
    list_item->next = func_list;
    func_list = list_item;
    Py_INCREF(callable);
    }
  gp_log(GP_LOG_ERROR, "gphoto2.port_log",
      "gp_log_add_func_py is deprecated. Please use gp_log_add_func instead.");
  return id;
};

// Remove Python callback from list
static int gp_log_remove_func_py(int id) {
  gp_log(GP_LOG_ERROR, "gphoto2.port_log",
      "gp_log_remove_func_py is deprecated. Please use gp_log_remove_func instead.");
  {
    // Remove Python callback from func_list
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
  }
  return gp_log_remove_func(id);
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
