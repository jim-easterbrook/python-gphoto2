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
%typemap(in, numinputs=0) GPPortInfoList ** (GPPortInfoList *temp) {
  $1 = &temp;
}
%typemap(argout) GPPortInfoList ** {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__GPPortInfoList, SWIG_POINTER_NEW));
}

// Add default constructor and destructor to _GPPortInfoList
DECLARE_GP_ERROR()
struct _GPPortInfoList {};
DEFAULT_CTOR(_GPPortInfoList, gp_port_info_list_new)
DEFAULT_DTOR(_GPPortInfoList, gp_port_info_list_free)
%ignore _GPPortInfoList;

// In libgphoto2 version 2.4 GPPortInfo is a structure, in version 2.5 it's a
// pointer to a structure.
#ifdef GPHOTO2_24
%typemap(in, numinputs=0) GPPortInfo * () {
  $1 = (GPPortInfo *)calloc(1, sizeof(GPPortInfo));
}
%typemap(argout) GPPortInfo * {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, SWIGTYPE_p__GPPortInfo, SWIG_POINTER_NEW));
}
#endif
#ifdef GPHOTO2_25
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

// Don't wrap internal functions
%ignore gp_port_info_new;
%ignore gp_port_info_set_name;
%ignore gp_port_info_set_path;
%ignore gp_port_info_set_type;

%include "gphoto2/gphoto2-port-info-list.h"
