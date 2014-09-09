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

%module(package="gphoto2.lib") gphoto2_list

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

// gp_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraList ** (CameraList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraList ** {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraList, SWIG_POINTER_OWN));
}

// Macro for functions that return a CameraList value
%define RETURN_CameraList(typepattern)
%typemap(in, numinputs=0) typepattern () {
  int error = gp_list_new(&$1);
  if (error != GP_OK) {
    PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
    goto fail;
  }
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, SWIGTYPE_p__CameraList, SWIG_POINTER_OWN));
}
%enddef

// Add constructors and destructor to _CameraList
DECLARE_GP_ERROR()
struct _CameraList {};
DEFAULT_CTOR(_CameraList, gp_list_new)
COPY_CTOR(_CameraList, gp_list_ref)
DEFAULT_DTOR(_CameraList, gp_list_unref)
%ignore _CameraList;

// Make CameraList more like a Python list
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc")      _CameraList::__len__;
%feature("python:slot", "sq_item",   functype="ssizeargfunc") _CameraList::__getitem__;
#endif // SWIGPYTHON_BUILTIN
%extend _CameraList {
  size_t __len__() {
    return gp_list_count($self);
  }
  PyObject *__getitem__(int idx) {
    if (idx < 0 || idx >= gp_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "CameraList index out of range");
      return NULL;
    }
    int error = 0;
    const char *name = NULL;
    const char *value = NULL;
    error = gp_list_get_name($self, idx, &name);
    if (error != GP_OK) {
      PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
      return NULL;
    }
    error = gp_list_get_value($self, idx, &value);
    if (error != GP_OK) {
      PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
      return NULL;
    }
    PyObject* result = PyList_New(2);
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

// gp_list_get_name() & gp_list_get_value() return pointers in output params
STRING_ARGOUT()

%include "gphoto2/gphoto2-list.h"
