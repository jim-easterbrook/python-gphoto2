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

%module(package="gphoto2") list

%include "common/preamble.i"

%rename(CameraList) _CameraList;

// Make docstring parameter types more Pythonic
%typemap(doc) CameraList * "$1_name: gphoto2.$*1_type"

#ifndef SWIGIMPORTED

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraList **)

// Add constructor and destructor to _CameraList
struct _CameraList {};
DEFAULT_CTOR(_CameraList, gp_list_new)
DEFAULT_DTOR(_CameraList, gp_list_unref)

// Make CameraList more like a Python list
LEN_MEMBER_FUNCTION(_CameraList, gp_list_count)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_item",   functype="ssizeargfunc") _CameraList::__getitem__;
#endif
%noexception _CameraList::__getitem__;
%extend _CameraList {
  PyObject *__getitem__(int idx) {
    int error = 0;
    const char *name = NULL;
    const char *value = NULL;
    PyObject* result = NULL;
    if (idx < 0 || idx >= gp_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "CameraList index out of range");
      return NULL;
    }
    error = gp_list_get_name($self, idx, &name);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
      return NULL;
    }
    error = gp_list_get_value($self, idx, &value);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
      return NULL;
    }
    result = PyList_New(2);
    if (name == NULL) {
      Py_INCREF(Py_None);
      PyList_SetItem(result, 0, Py_None);
    }
    else {
      PyList_SetItem(result, 0, PyString_FromString(name));
    }
    if (value == NULL) {
      Py_INCREF(Py_None);
      PyList_SetItem(result, 1, Py_None);
    }
    else {
      PyList_SetItem(result, 1, PyString_FromString(value));
    }
    return result;
  }
};

// Add member methods to _CameraList
MEMBER_FUNCTION(_CameraList,
    int, count, (),
    gp_list_count, ($self), )
MEMBER_FUNCTION(_CameraList,
    void, append, (const char *name, const char *value),
    gp_list_append, ($self, name, value), )
MEMBER_FUNCTION(_CameraList,
    void, reset, (),
    gp_list_reset, ($self), )
MEMBER_FUNCTION(_CameraList,
    void, sort, (),
    gp_list_sort, ($self), )
MEMBER_FUNCTION(_CameraList,
    void, find_by_name, (int *index, const char *name),
    gp_list_find_by_name, ($self, index, name), )
MEMBER_FUNCTION(_CameraList,
    void, get_name, (int index, const char **name),
    gp_list_get_name, ($self, index, name), )
MEMBER_FUNCTION(_CameraList,
    void, get_value, (int index, const char **value),
    gp_list_get_value, ($self, index, value), )
MEMBER_FUNCTION(_CameraList,
    void, set_name, (int index, const char *name),
    gp_list_set_name, ($self, index, name), )
MEMBER_FUNCTION(_CameraList,
    void, set_value, (int index, const char *value),
    gp_list_set_value, ($self, index, value), )
MEMBER_FUNCTION(_CameraList,
    void, populate, (const char *format, int count),
    gp_list_populate, ($self, format, count), )

// Ignore some functions
%ignore gp_list_free;
%ignore gp_list_ref;
%ignore gp_list_unref;

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-list.h"
