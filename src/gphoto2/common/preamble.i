// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2017-25  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

// Stuff to go at the top of every gphoto2 .i file

// C header file
%{
#include "gphoto2/gphoto2.h"
%}

// Include our macros and swig's typemaps
%include "common/macros.i"
%include "typemaps.i"

// Include doxygen documentation
#if defined(DOC_FILE)
%include DOC_FILE
#endif
%feature("autodoc", "2");

// Provide our own version of macros added in SWIG 4.3.0
#if SWIG_VERSION < 0x040300
%{
#define SWIG_Py_INCREF Py_INCREF
#define SWIG_Py_XINCREF Py_XINCREF
#define SWIG_Py_DECREF Py_DECREF
#define SWIG_Py_XDECREF Py_XDECREF
%}
#endif

// Improve documentation of some parameter types
%typemap(doc) char const * "$1_name: str"
%typemap(doc) uint64_t "$1_name: int"

// Convert all char ** parameters to string return value
%typemap(in, numinputs=0) char ** (char *temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) char ** {
  $result = SWIG_AppendOutput($result,
    *$1 ? PyString_FromString(*$1) : SWIG_Py_Void());
}

// Get PyExc_GPhoto2Error object
%{
PyObject *PyExc_GPhoto2Error = NULL;
%}
%init %{
{
  PyObject *module = PyImport_ImportModule("gphoto2");
  if (module != NULL) {
    PyExc_GPhoto2Error = PyObject_GetAttrString(module, "GPhoto2Error");
    SWIG_Py_DECREF(module);
  }
  if (PyExc_GPhoto2Error == NULL)
#if SWIG_VERSION >= 0x040400
    return -1;
#elif PY_VERSION_HEX >= 0x03000000
    return NULL;
#else
    return;
#endif
}
%}
