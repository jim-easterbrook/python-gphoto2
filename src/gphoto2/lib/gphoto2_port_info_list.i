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

%module(package="gphoto2.lib") gphoto2_port_info_list

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_port.i"

%feature("autodoc", "2");

%ignore gp_port_info_get_library_filename;
%ignore gp_port_info_set_library_filename;

%include "typemaps.i"

%include "macros.i"

// gp_port_info_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(GPPortInfoList **)

// Add default constructor and destructor to _GPPortInfoList
DECLARE_GP_ERROR()
struct _GPPortInfoList {};
DEFAULT_CTOR(_GPPortInfoList, gp_port_info_list_new)
DEFAULT_DTOR(_GPPortInfoList, gp_port_info_list_free)
%ignore _GPPortInfoList;

// In libgphoto2 version 2.4 GPPortInfo is a structure, in version 2.5 it's a
// pointer to a structure.
#ifdef GPHOTO2_24
CALLOC_ARGOUT(GPPortInfo *)
#else
%typemap(in, numinputs=0) GPPortInfo * (GPPortInfo temp) {
  $1 = &temp;
}
%typemap(argout) GPPortInfo * {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__GPPortInfo, 0));
}
#endif

// several getter functions return string pointers in output params
STRING_ARGOUT()

// Make _GPPortInfoList more like a Python list
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc")      _GPPortInfoList::__len__;
%feature("python:slot", "sq_item",   functype="ssizeargfunc") _GPPortInfoList::__getitem__;
#endif // SWIGPYTHON_BUILTIN
%extend _GPPortInfoList {
  size_t __len__() {
    return gp_port_info_list_count($self);
  }
  PyObject *__getitem__(int idx) {
    if (idx < 0 || idx >= gp_port_info_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "GPPortInfoList index out of range");
      return NULL;
    }
    int error = 0;
    int own = 0;
#ifdef GPHOTO2_24
    own = SWIG_POINTER_OWN;
    GPPortInfo *result = (GPPortInfo *)calloc(1, sizeof(GPPortInfo));
    error = gp_port_info_list_get_info($self, idx, result);
#else
    GPPortInfo result = NULL;
    error = gp_port_info_list_get_info($self, idx, &result);
#endif
    if (error != GP_OK) {
      PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
#ifdef GPHOTO2_24
      free(result);
#endif
      return NULL;
    }
    return SWIG_Python_NewPointerObj(NULL, result, SWIGTYPE_p__GPPortInfo, own);
  }
};

// Don't wrap internal functions
%ignore gp_port_info_new;
%ignore gp_port_info_set_name;
%ignore gp_port_info_set_path;
%ignore gp_port_info_set_type;

%include "gphoto2/gphoto2-port-info-list.h"
