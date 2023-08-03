// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

// Deprecate some functions intended for camera drivers
DEPRECATED(gp_list_populate,)
DEPRECATED(_CameraList::populate, 1)

// Make docstring parameter types more Pythonic
%typemap(doc) CameraList * "$1_name: gphoto2.$*1_type"

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraList **)

// gp_list_find_by_name() returns the result in an integer, or NULL
%typemap(in, numinputs=0) int *index (int temp=0) %{
  $1 = &temp;
%}
%typemap(argout) int *index %{
  $result = SWIG_Python_AppendOutput($result, PyInt_FromLong(*$1));
%}

// Add constructor and destructor to _CameraList
struct _CameraList {};
DEFAULT_CTOR(_CameraList, gp_list_new)
DEFAULT_DTOR(_CameraList, gp_list_unref)

// Make CameraList more like a Python list and/or dict
LEN_MEMBER_FUNCTION(_CameraList, gp_list_count)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "mp_subscript", functype="binaryfunc")
  _CameraList::__getitem__;
#endif
%feature("docstring") _CameraList::keys "Return a tuple of all the names in the list."
%feature("docstring") _CameraList::values "Return a tuple of all the values in the list."
%feature("docstring") _CameraList::items "Return a tuple of all the (name, value) pairs in the list."
%noexception _CameraList::__getitem__;
%noexception _CameraList::keys;
%noexception _CameraList::values;
%noexception _CameraList::items;
%extend _CameraList {
  PyObject *__getitem__(int idx) {
    int error = GP_OK;
    const char *name = NULL;
    const char *value = NULL;
    int count = gp_list_count($self);
    if (count < GP_OK) {
      GPHOTO2_ERROR(count)
      return NULL;
    }
    if (idx < 0)
      idx += count;
    if (idx < 0 || idx >= count) {
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
    return PyTuple_Pack(2,
      PyUnicode_FromString(name), PyUnicode_FromString(value));
  }
  PyObject *__getitem__(const char *name) {
    int error = GP_OK;
    const char *value = NULL;
    int idx = 0;
    error = gp_list_find_by_name($self, &idx, name);
    if (error < GP_OK) {
      PyErr_SetString(PyExc_KeyError, name);
      return NULL;
    }
    error = gp_list_get_value($self, idx, &value);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
      return NULL;
    }
    return PyUnicode_FromString(value);
  }
  PyObject *keys() {
    PyObject *result = NULL;
    int error = GP_OK;
    const char *name = NULL;
    int count = gp_list_count($self);
    if (count < GP_OK) {
      GPHOTO2_ERROR(count)
      return NULL;
    }
    result = PyTuple_New(count);
    for (int i = 0; i < count; i++) {
      error = gp_list_get_name($self, i, &name);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return NULL;
      }
      PyTuple_SET_ITEM(result, i, PyUnicode_FromString(name));
    }
    return result;
  }
  PyObject *values() {
    PyObject *result = NULL;
    int error = GP_OK;
    const char *value = NULL;
    int count = gp_list_count($self);
    if (count < GP_OK) {
      GPHOTO2_ERROR(count)
      return NULL;
    }
    result = PyTuple_New(count);
    for (int i = 0; i < count; i++) {
      error = gp_list_get_value($self, i, &value);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return NULL;
      }
      PyTuple_SET_ITEM(result, i, PyUnicode_FromString(value));
    }
    return result;
  }
  PyObject *items() {
    PyObject *result = NULL;
    int error = GP_OK;
    const char *name = NULL;
    const char *value = NULL;
    int count = gp_list_count($self);
    if (count < GP_OK) {
      GPHOTO2_ERROR(count)
      return NULL;
    }
    result = PyTuple_New(count);
    for (int i = 0; i < count; i++) {
      error = gp_list_get_name($self, i, &name);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return NULL;
      }
      error = gp_list_get_value($self, i, &value);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return NULL;
      }
      PyTuple_SET_ITEM(result, i, PyTuple_Pack(2,
        PyUnicode_FromString(name), PyUnicode_FromString(value)));
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

%include "gphoto2/gphoto2-list.h"
