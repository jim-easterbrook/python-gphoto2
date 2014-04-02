// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module gphoto2_port_log

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

// SWIG can't wrap functions with var args
%ignore gp_logv;

%typemap(in) PyObject *func {
  if (!PyCallable_Check($input)) {
      PyErr_SetString(PyExc_TypeError, "Object not callable");
      return NULL;
  }
  $1 = $input;
}

%inline %{
// Python logging callback
static PyObject *log_error = NULL;
static PyObject *log_info  = NULL;
static PyObject *log_debug = NULL;

static void logging_callback(GPLogLevel level, const char *domain,
                             const char *str, void *data) {
  PyObject *log;
  if (level == GP_LOG_ERROR)
    log = log_error;
  else if (level == GP_LOG_VERBOSE)
    log = log_info;
  else
    log = log_debug;
  if (!log)
    return;
  PyGILState_STATE gstate = PyGILState_Ensure();
  PyObject *arglist = Py_BuildValue("(sss)", "%s: %s", domain, str);
  PyObject *result = PyObject_CallObject(log, arglist);
  Py_DECREF(arglist);
  if (result)
    Py_DECREF(result);
  else
    PyErr_Clear();
  PyGILState_Release(gstate);
};

static int use_python_logging(void) {
  if (log_error)
    return GP_OK;
  PyObject *logging = PyImport_ImportModule("logging");
  if (logging) {
    PyObject *get_logger = PyObject_GetAttrString(logging, "getLogger");
    if (get_logger) {
      PyObject *arglist = Py_BuildValue("(s)", "gphoto2");
      PyObject *logger = PyObject_CallObject(get_logger, arglist);
      Py_DECREF(arglist);
      if (logger) {
        log_error = PyObject_GetAttrString(logger, "error");
        log_info  = PyObject_GetAttrString(logger, "info");
        log_debug = PyObject_GetAttrString(logger, "debug");
        Py_DECREF(logger);
      }
      Py_DECREF(get_logger);
    }
    Py_DECREF(logging);
  }
  return gp_log_add_func(GP_LOG_DATA, logging_callback, NULL);
};

// General Python function callback
static void _callback_wrapper(GPLogLevel level, const char *domain,
                              const char *str, void *data) {
  PyGILState_STATE gstate = PyGILState_Ensure();
  PyObject *result = NULL;
  PyObject *arglist = Py_BuildValue("(ss)", domain, str);
  result = PyObject_CallObject(data, arglist);
  Py_DECREF(arglist);
  if (result == NULL)
    PyErr_Clear();
  else
    Py_DECREF(result);
  PyGILState_Release(gstate);
};

struct LogFuncItem {
  int id;
  PyObject *func;
  struct LogFuncItem *next;
};

static struct LogFuncItem *func_list = NULL;

static int gp_log_add_func_py(GPLogLevel level, PyObject *func) {
  int id = gp_log_add_func(level, _callback_wrapper, func);
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

%include "gphoto2/gphoto2-port-log.h"
