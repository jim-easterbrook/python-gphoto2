// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-24  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This file is part of python-gphoto2.
//
// python-gphoto2 is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// python-gphoto2 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with python-gphoto2.  If not, see <https://www.gnu.org/licenses/>.

%module(package="gphoto2") list

%include "common/preamble.i"

%rename(CameraList) _CameraList;

// Deprecate some functions intended for camera drivers (2023-08-01)
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
%typemap(argout) int *index {
  $result = SWIG_AppendOutput($result, PyInt_FromLong(*$1));
}

// Code fragments used later on
%fragment("CameraList_accessor", "header") {
  %#include "gphoto2/gphoto2.h"
  typedef PyObject* (CameraList_get_func) (CameraList *, int);
  typedef struct _CameraList_accessor {
    CameraList *list;
    CameraList_get_func *func;
  } CameraList_accessor;
}
%fragment("new_CameraList_accessor", "header",
          fragment="CameraList_accessor") {
  // Constructor defined outside %extend as not callable from Python
  static CameraList_accessor
  *new_CameraList_accessor(CameraList *list, CameraList_get_func *func) {
    CameraList_accessor *self = malloc(sizeof(CameraList_accessor));
    if (!self) return NULL;
    if (gp_list_ref(list) < GP_OK) {
      free(self);
      return NULL;
    }
    self->list = list;
    self->func = func;
    return self;
  }
}
%fragment("CameraList_get_key", "header") {
  static PyObject* CameraList_get_key(CameraList *list, int idx) {
    const char *name = NULL;
    int error = gp_list_get_name(list, idx, &name);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error);
      return NULL;
    }
    return name ? PyUnicode_FromString(name) : SWIG_Py_Void();
  }
}
%fragment("CameraList_get_value", "header") {
  static PyObject* CameraList_get_value(CameraList *list, int idx) {
    const char *value = NULL;
    int error = gp_list_get_value(list, idx, &value);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error);
      return NULL;
    }
    return value ? PyUnicode_FromString(value) : SWIG_Py_Void();
  }
}
%fragment("CameraList_get_item", "header",
          fragment="CameraList_get_key", fragment="CameraList_get_value") {
  static PyObject* CameraList_get_item(CameraList *list, int idx) {
    PyObject *name = CameraList_get_key(list, idx);
    if (!name) return NULL;
    PyObject *value = CameraList_get_value(list, idx);
    if (!value) {
      SWIG_Py_DECREF(name);
      return NULL;
    }
    return PyTuple_Pack(2, name, value);
  }
}

// Add constructor and destructor to _CameraList
struct _CameraList {};
DEFAULT_CTOR(_CameraList, gp_list_new)
DEFAULT_DTOR(_CameraList, gp_list_unref)

// Simple accessor object
%feature("docstring") _CameraList_accessor
"List-like access to CameraList keys, values, or (key, value) items.

This can be accessed or iterated over like any Python list or tuple."
%feature("python:slot", "sq_length", functype="lenfunc")
  _CameraList_accessor::__len__;
%feature("python:slot", "sq_item", functype="ssizeargfunc")
  _CameraList_accessor::__getitem__;
// SWIG doesn't need to know about CameraList_accessor internals
typedef struct _CameraList_accessor {} CameraList_accessor;
%extend _CameraList_accessor {
  ~_CameraList_accessor() {
    gp_list_unref($self->list);
    free($self);
  }
  int __len__() {
    return gp_list_count($self->list);
  }
  PyObject* __getitem__(int idx) {
    if (idx < 0 || idx >= gp_list_count($self->list)) {
      PyErr_SetString(PyExc_IndexError,
                      "CameraList_accessor index out of range");
      return NULL;
    }
    return self->func($self->list, idx);
  }
};

// Turn off default exception handling
%noexception;

// Make CameraList more like a Python list and/or dict
%feature("python:slot", "mp_subscript", functype="binaryfunc")
  _CameraList::__getitem__;
%feature("docstring") _CameraList::keys "Return an accessor for the names in the list."
%feature("docstring") _CameraList::values "Return an accessor for the values in the list."
%feature("docstring") _CameraList::items "Return an accessor for the (name, value) pairs in the list."
%newobject _CameraList::keys;
%newobject _CameraList::values;
%newobject _CameraList::items;
%extend _CameraList {
  %fragment("new_CameraList_accessor");
  %fragment("CameraList_get_key");
  %fragment("CameraList_get_value");
  %fragment("CameraList_get_item");
  PyObject *__getitem__(int idx) {
    if (idx < 0)
      idx += gp_list_count($self);
    if (idx < 0 || idx >= gp_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "CameraList index out of range");
      return NULL;
    }
    return CameraList_get_item($self, idx);
  }
  PyObject *__getitem__(const char *name) {
    int idx = 0;
    if (gp_list_find_by_name($self, &idx, name) < GP_OK) {
      PyErr_SetString(PyExc_KeyError, name);
      return NULL;
    }
    return CameraList_get_value($self, idx);
  }
  CameraList_accessor* keys() {
    return new_CameraList_accessor($self, CameraList_get_key);
  }
  CameraList_accessor* values() {
    return new_CameraList_accessor($self, CameraList_get_value);
  }
  CameraList_accessor* items() {
    return new_CameraList_accessor($self, CameraList_get_item);
  }
};

// Turn on default exception handling
DEFAULT_EXCEPTION

// Add member methods to _CameraList
LEN_MEMBER_FUNCTION(_CameraList, gp_list_count)
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
