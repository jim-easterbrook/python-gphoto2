// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

// Forward declarations
%runtime %{
#include "gphoto2/gphoto2.h"
static PyObject* CameraList_item(CameraList *list, int type, int idx);
typedef struct _CameraList_iterator CameraList_iterator;
CameraList_iterator *new_CameraList_iterator(CameraList *list, int type);
%}

#ifndef SWIGIMPORTED

// Simple iterator object
%feature("docstring") _CameraList_iterator "Iterator over CameraList keys, values, or (key, value) pairs.

In addition to the usual iterator methods the values can be read by
indexing, for example iterator[4] gets the 4th value."
%ignore _CameraList_iterator::list;
%ignore _CameraList_iterator::type;
%ignore _CameraList_iterator::idx;
%ignore _CameraList_iterator::count;
%feature("python:slot", "sq_length", functype="lenfunc")
  _CameraList_iterator::__len__;
%feature("python:slot", "sq_item", functype="ssizeargfunc")
  _CameraList_iterator::__getitem__;
%feature("python:slot", "tp_iter", functype="getiterfunc")
  _CameraList_iterator::__iter__;
%feature("python:slot", "tp_iternext", functype="iternextfunc")
  _CameraList_iterator::__next__;
%inline %{
typedef struct _CameraList_iterator {
  CameraList *list;
  int type; // 0 = keys, 1 = values, 2 = items
  int idx;
  int count;
} CameraList_iterator;
%}
%extend _CameraList_iterator {
  ~_CameraList_iterator() {
    int error = gp_list_unref($self->list);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
    }
    free($self);
  }
  int __len__() {
    return $self->count;
  }
  PyObject* __getitem__(int idx) {
    if (idx < 0)
      idx += $self->count;
    if (idx < 0 || idx >= $self->count) {
      PyErr_SetString(PyExc_IndexError,
                      "CameraList_iterator index out of range");
      return NULL;
    }
    return CameraList_item($self->list, $self->type, idx);
  }
  CameraList_iterator* __iter__() {
    return $self;
  }
  PyObject* __next__() {
    if ($self->idx >= $self->count) {
      PyErr_SetNone(PyExc_StopIteration);
      return NULL;
    }
    return CameraList_item($self->list, $self->type, $self->idx++);
  }
};

#endif //ifndef SWIGIMPORTED

// Helper functions
%{
static PyObject* CameraList_item(CameraList *list, int type, int idx) {
  int error = GP_OK;
  const char *name = NULL;
  const char *value = NULL;
  PyObject *py_name = NULL;
  PyObject *py_value = NULL;
  if (type != 1) {
    error = gp_list_get_name(list, idx, &name);
    if (error < GP_OK) {
      PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
      return NULL;
    }
    py_name = PyUnicode_FromString(name);
  }
  if (type == 0)
    return py_name;
  error = gp_list_get_value(list, idx, &value);
  if (error < GP_OK) {
    PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
    return NULL;
  }
  py_value = PyUnicode_FromString(value);
  if (type == 1)
    return py_value;
  return PyTuple_Pack(2, py_name, py_value);
}
CameraList_iterator *new_CameraList_iterator(CameraList *list, int type) {
  int error = GP_OK;
  CameraList_iterator *self = malloc(sizeof(CameraList_iterator));
  if (!self) {
    PyErr_SetString(
      PyExc_MemoryError, "cannot allocate CameraList_iterator");
    goto fail;
  }
  self->list = list;
  self->type = type;
  self->idx = 0;
  self->count = gp_list_count(list);
  if (self->count < GP_OK) {
    PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(self->count));
    goto fail;
  }
  error = gp_list_ref(list);
  if (error < GP_OK) {
    PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
    goto fail;
  }
  return self;
fail:
  if (self)
    free(self);
  return NULL;
}
%}

// Turn off default exception handling
%noexception;

// Make CameraList more like a Python list and/or dict
%feature("python:slot", "mp_subscript", functype="binaryfunc")
  _CameraList::__getitem__;
%feature("python:slot", "tp_iter", functype="getiterfunc")
  _CameraList::__iter__;
%feature("docstring") _CameraList::keys "Return an iterator over the names in the list."
%feature("docstring") _CameraList::values "Return an iterator over the values in the list."
%feature("docstring") _CameraList::items "Return an iterator over the (name, value) pairs in the list."
%extend _CameraList {
  PyObject *__getitem__(int idx) {
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
    return CameraList_item($self, 2, idx);
  }
  PyObject *__getitem__(const char *name) {
    int idx = 0;
    if (gp_list_find_by_name($self, &idx, name) < GP_OK) {
      PyErr_SetString(PyExc_KeyError, name);
      return NULL;
    }
    return CameraList_item($self, 1, idx);
  }
  CameraList_iterator* keys() {
    return new_CameraList_iterator($self, 0);
  }
  CameraList_iterator* values() {
    return new_CameraList_iterator($self, 1);
  }
  CameraList_iterator* items() {
    return new_CameraList_iterator($self, 2);
  }
  CameraList_iterator* __iter__() {
    return new_CameraList_iterator($self, 2);
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
