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

%module(package="gphoto2.lib") gphoto2_abilities_list

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_context.i"
%import "gphoto2_list.i"
%import "gphoto2_port_info_list.i"
%import "gphoto2_port_log.i"

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

// gp_abilities_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraAbilitiesList ** (CameraAbilitiesList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraAbilitiesList ** {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraAbilitiesList, SWIG_POINTER_NEW));
}

// Add default constructor and destructor to _CameraAbilitiesList
DECLARE_GP_ERROR()
struct _CameraAbilitiesList {};
DEFAULT_CTOR(_CameraAbilitiesList, gp_abilities_list_new)
DEFAULT_DTOR(_CameraAbilitiesList, gp_abilities_list_free)
%ignore _CameraAbilitiesList;

// Structures are read only
%immutable;

%include "gphoto2/gphoto2-abilities-list.h"
