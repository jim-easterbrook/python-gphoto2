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

%module(package="gphoto2.lib") gphoto2_port_log

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

// SWIG can't wrap functions with var args
%ignore gp_logv;

// Should not directly call Python from C
%ignore gp_log_add_func;

// List of python callbacks is private
%ignore func_list;
%ignore callback_wrapper;
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
#ifdef GPHOTO2_24
static void callback_wrapper(GPLogLevel level, const char *domain,
                             const char *format, va_list args, void *data) {
  char str[1024];
  vsnprintf(str, sizeof(str), format, args);
#else
static void callback_wrapper(GPLogLevel level, const char *domain,
                             const char *str, void *data) {
#endif
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

// Keep list of Python callback function associated with each id
struct LogFuncItem {
  int id;
  PyObject *func;
  struct LogFuncItem *next;
};

static struct LogFuncItem *func_list = NULL;

// Add Python callback to front of list
static int gp_log_add_func_py(GPLogLevel level, PyObject *func) {
  int id = gp_log_add_func(level, callback_wrapper, func);
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

%include "gphoto2/gphoto2-port-log.h"
