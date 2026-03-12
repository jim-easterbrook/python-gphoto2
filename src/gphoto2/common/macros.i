// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-26  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%define DEFAULT_EXCEPTION
%exception {
  $action
  if (PyErr_Occurred()) SWIG_fail;
}
%enddef

%define DEPRECATED(func_name, check_result)
%feature("docstring") func_name
  "This function is deprecated and will be removed in a future release."
%exception func_name {
  if (PyErr_WarnEx(PyExc_DeprecationWarning, #func_name ## " is deprecated and"
    " will be removed in a future release", 1) < 0) SWIG_fail;
  $action
#if #check_result != ""
  if (PyErr_Occurred()) SWIG_fail;
#endif
}
%enddef

// Get PyExc_GPhoto2Error object
%fragment("_declare_GPhoto2Error", "header") {
PyObject *PyExc_GPhoto2Error = NULL;
}
%fragment("_import_GPhoto2Error", "init", fragment="_declare_GPhoto2Error") {
{
  PyObject *module = PyImport_ImportModule("gphoto2");
  if (module) {
    PyExc_GPhoto2Error = PyObject_GetAttrString(module, "GPhoto2Error");
    SWIG_Py_DECREF(module);
  }
  if (!PyExc_GPhoto2Error)
#if SWIG_VERSION >= 0x040400
    return -1;
#else
    return NULL;
#endif
}
}

// Set Python exception if result is a failure
%fragment("gphoto2_error", "header", fragment="_import_GPhoto2Error") {
static int gphoto2_error(int error) {
  if (error < GP_OK) {
    PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
    return 1;
  }
  return 0;
};
}

%define PLAIN_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern ($*1_type temp = NULL) {
  $1 = &temp;
}
%typemap(argout) typepattern {
  $result = SWIG_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}
%enddef

%define CALLOC_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern () {
  $1 = ($1_type)calloc(1, sizeof($*1_type));
  if (!$1) {
    PyErr_SetString(PyExc_MemoryError, "Cannot allocate " "$*1_type");
    SWIG_fail;
  }
}
%typemap(freearg) typepattern {
  free($1);
}
%typemap(argout) typepattern {
  $result = SWIG_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define NEW_ARGOUT(typepattern, alloc_func, free_func)
%typemap(in, numinputs=0, fragment="gphoto2_error") typepattern () {
  if (gphoto2_error(alloc_func(&$1))) {
    $1 = NULL;
    SWIG_fail;
  }
}
%typemap(freearg) typepattern {
  if ($1) {
    free_func($1);
  }
}
%typemap(argout) typepattern {
  $result = SWIG_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define DEFAULT_CTOR(type, function)
%extend type {
  %fragment("gphoto2_error");
  type() {
    struct type *result;
    gphoto2_error(function(&result));
    return result;
  }
};
%enddef

%define DEFAULT_DTOR(name, free_func)
%delobject free_func;
%extend name {
  %fragment("gphoto2_error");
  ~name() {
    gphoto2_error(free_func($self));
  }
};
%enddef

// Macros to add member functions to structs
%define MEMBER_FUNCTION(type, member_rtn, member, member_args,
                        function, function_args, thread_allow)
%extend type {
  %fragment("gphoto2_error");
  member_rtn member member_args {
#if #thread_allow != ""
    SWIG_PYTHON_THREAD_BEGIN_ALLOW;
#endif
    int result = function function_args;
#if #thread_allow != ""
    SWIG_PYTHON_THREAD_END_ALLOW;
#endif
    gphoto2_error(result);
#if #member_rtn == "int" || #member_rtn == "static int"
    return result;
#endif
  }
};
%enddef

%define LEN_MEMBER_FUNCTION(type, function)
%feature("python:slot", "sq_length", functype="lenfunc") type::__len__;
MEMBER_FUNCTION(type, int, __len__, (), function, ($self), )
%enddef

%define VOID_MEMBER_FUNCTION(type, member, member_args, function, function_args)
%extend type {
  void member member_args {
    function function_args;
  }
};
%enddef

%define DEFAULT_CONTEXT
// For functions that accept NULL context value
%typemap(default) (GPContext *) {
  $1 = NULL;
}
%typemap(doc) GPContext * "$1_name: gphoto2.Context (default=None)";
%enddef
