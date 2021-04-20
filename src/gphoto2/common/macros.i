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

%define DEFAULT_EXCEPTION
%exception {
  $action
  if (PyErr_Occurred()) SWIG_fail;
}
%enddef

%define GPHOTO2_ERROR(error)
PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
%enddef

%define PLAIN_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern ($*1_type temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}
%enddef

%define CALLOC_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern () {
  $1 = ($1_type)calloc(1, sizeof($*1_type));
  if ($1 == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Cannot allocate " "$*1_type");
    SWIG_fail;
  }
}
%typemap(freearg) typepattern {
  free($1);
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define NEW_ARGOUT(typepattern, alloc_func, free_func)
%typemap(in, numinputs=0) typepattern () {
  int error = alloc_func(&$1);
  if (error < GP_OK) {
    $1 = NULL;
    GPHOTO2_ERROR(error)
    SWIG_fail;
  }
}
%typemap(freearg) typepattern {
  if ($1 != NULL) {
    free_func($1);
  }
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define DEFAULT_CTOR(type, function)
%extend type {
  type() {
    struct type *result;
    int error = function(&result);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
    return result;
  }
};
%enddef

%define DEFAULT_DTOR(name, free_func)
%delobject free_func;
%extend name {
  ~name() {
    int error = free_func($self);
    if (error < GP_OK) GPHOTO2_ERROR(error)
  }
};
%enddef

// Macros to add member functions to structs
%define MEMBER_FUNCTION(type, member_rtn, member, member_args,
                        function, function_args, thread_allow)
%extend type {
  member_rtn member member_args {
#if #thread_allow != ""
    SWIG_PYTHON_THREAD_BEGIN_ALLOW;
#endif
    int result = function function_args;
#if #thread_allow != ""
    SWIG_PYTHON_THREAD_END_ALLOW;
#endif
    if (result < GP_OK) GPHOTO2_ERROR(result)
#if #member_rtn == "int"
    return result;
#endif
  }
};
%enddef

%define LEN_MEMBER_FUNCTION(type, function)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc") type::__len__;
#endif
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
