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
%ignore logging_callback;

%inline %{
static PyObject *log_error = NULL;
static PyObject *log_info  = NULL;
static PyObject *log_debug = NULL;

static void logging_callback(GPLogLevel level, const char *domain, const char *format,
                             va_list args, void *data) {
  PyObject *log;
  if (level == GP_LOG_ERROR) {
    log = log_error;
  }
  else if (level == GP_LOG_VERBOSE) {
    log = log_info;
  }
  else {
    log = log_debug;
  }
  if (!log) {
    return;
  }
  char message[1024];
  snprintf(message, sizeof(message), format, args);
  PyGILState_STATE gstate = PyGILState_Ensure();
  PyObject *arglist = Py_BuildValue("(sss)", "%s: %s", domain, &message);
  PyObject *result = PyObject_CallObject(log, arglist);
  Py_DECREF(arglist);
  if (result) {
    Py_DECREF(result);
  }
  else {
    PyErr_Clear();
  }
  PyGILState_Release(gstate);
};

static int use_python_logging() {
  if (log_error) {
    return GP_OK;
  }
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
  return gp_log_add_func(GP_LOG_DATA, (GPLogFunc) logging_callback, NULL);
};
%}

%include "gphoto2/gphoto2-port-log.h"
