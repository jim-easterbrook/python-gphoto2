// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-17  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%define AUTODOC()
#if defined(DOC_FILE)
%include DOC_FILE
%feature("autodoc", "1");
#else
%feature("autodoc", "2");
#endif

// Make docstring parameter types more Pythonic
%typemap(doc) char const * "$1_name: str"
%typemap(doc) void * "$1_name: object"
%enddef

%define IMPORT_GPHOTO2_ERROR()
%{
PyObject *PyExc_GPhoto2Error = NULL;
%}
%init %{
{
  PyObject *module = PyImport_ImportModule("gphoto2.result");
  if (module != NULL) {
    PyExc_GPhoto2Error = PyObject_GetAttrString(module, "GPhoto2Error");
    Py_DECREF(module);
  }
  if (PyExc_GPhoto2Error == NULL)
#if PY_VERSION_HEX >= 0x03000000
    return NULL;
#else
    return;
#endif
}
%}
%enddef

%define GPHOTO2_ERROR(error)
PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
%enddef

%define STRING_ARGOUT()
%typemap(in, numinputs=0) char ** (char *temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) char ** {
  if (*$1) {
    $result = SWIG_Python_AppendOutput($result, PyString_FromString(*$1));
  }
  else {
    Py_INCREF(Py_None);
    $result = SWIG_Python_AppendOutput($result, Py_None);
  }
}
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

%define DEFAULT_CTOR(type, py_type, function)
%exception type {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend type {
  type() {
    struct type *result;
    int error = function(&result);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
    return result;
  }
};
//%feature("docstring") function "See also: gphoto2." #py_type
%enddef

%define DEFAULT_DTOR(name, free_func)
%delobject free_func;
%exception ~name {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend name {
  ~name() {
    free_func($self);
  }
};
%enddef

// Macros to add member functions to structs
%define MEMBER_FUNCTION(type, py_type, member, member_args, function, function_args)
%exception type::member {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend type {
%feature("docstring") "See also: gphoto2." #function
  void member member_args {
    int error = function function_args;
    if (error < GP_OK) GPHOTO2_ERROR(error)
  }
};
//%feature("docstring") function "See also: gphoto2." #py_type "." #member
%enddef

%define MEMBER_FUNCTION_THREAD(type, py_type, member, member_args, function, function_args)
%exception type::member {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend type {
%feature("docstring") "See also: gphoto2." #function
  void member member_args {
    SWIG_PYTHON_THREAD_BEGIN_ALLOW;
    int error = function function_args;
    SWIG_PYTHON_THREAD_END_ALLOW;
    if (error < GP_OK) GPHOTO2_ERROR(error)
  }
};
//%feature("docstring") function "See also: gphoto2." #py_type "." #member
%enddef

%define INT_MEMBER_FUNCTION(type, py_type, member, member_args, function, function_args)
%{
int (*type ## _ ## member)() = function;
int (*struct ## _ ## type ## _ ## member)() = function;
%}
%exception type::member {
  $action
  if (result < GP_OK) {
    GPHOTO2_ERROR(result)
    goto fail;
  }
}
%extend type {
//%feature("docstring") "See also: gphoto2." #function
  int member member_args;
};
//%feature("docstring") function "See also: gphoto2." #py_type "." #member
%enddef

%define LEN_MEMBER_FUNCTION(type, py_type, function)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc") type::__len__;
#endif
INT_MEMBER_FUNCTION(type, py_type, __len__, (), function, ())
%enddef
