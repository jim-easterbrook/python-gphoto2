// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2017-20  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

// Stuff to go at the top of every gphoto2 .i file

// C header file
%{
#include "gphoto2/gphoto2.h"
%}

// Include macros and typemaps
%include "macros.i"
%include "typemaps.i"

// Import all modules to ensure all type definitions are shared
#ifndef SWIGIMPORTED
%import "abilities_list.i"
%import "camera.i"
%import "context.i"
%import "file.i"
%import "filesys.i"
%import "list.i"
%import "port_info_list.i"
%import "port_log.i"
%import "result.i"
%import "version.i"
%import "widget.i"
#endif //ifndef SWIGIMPORTED

// Include doxygen documentation
#if defined(DOC_FILE)
%include DOC_FILE
#endif
%feature("autodoc", "2");

// Improve documentation of some parameter types
%typemap(doc) char const * "$1_name: str"
%typemap(doc) uint64_t "$1_name: int"

// Convert all char ** parameters to string return value
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

// Get PyExc_GPhoto2Error object
%{
PyObject *PyExc_GPhoto2Error = NULL;
%}
%init %{
{
  PyObject *module = PyImport_ImportModule("gphoto2");
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
