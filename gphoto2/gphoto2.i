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

%module gphoto2

%{
#define SWIG_FILE_WITH_INIT

#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "3");

%include "typemaps.i"

// image dimensions use uint32_t
%typemap(in) uint32_t {
  $1 = PyInt_AsLong($input);
}
%typemap(out) uint32_t {
  $result = PyInt_FromLong($1);
}

// image mtime uses time_t
%typemap(in) time_t {
  $1 = PyInt_AsLong($input);
}
%typemap(out) time_t {
  $result = PyInt_FromLong($1);
}

// gp_camera_get_config() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  $1 = &temp;
}
%typemap(argout) CameraWidget ** {
  $result = PyTuple_Pack(2, $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, 0));
}

// gp_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraList ** (CameraList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraList ** {
  $result = PyTuple_Pack(2, $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraList, 0));
}

// gp_camera_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) Camera ** (Camera *temp) {
  $1 = &temp;
}
%typemap(argout) Camera ** {
  $result = PyTuple_Pack(2, $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__Camera, 0));
}

// gp_abilities_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraAbilitiesList ** (CameraAbilitiesList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraAbilitiesList ** {
  $result = PyTuple_Pack(
    2, $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraAbilitiesList, 0));
}

// gp_port_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) GPPort ** (GPPort *temp) {
  $1 = &temp;
}
%typemap(argout) GPPort ** {
  $result = PyTuple_Pack(
    2, $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__GPPort, 0));
}

// gp_list_get_name() and gp_list_get_value() return string pointers in output params
%typemap(in, numinputs=0) char ** (char *temp) {
  $1 = &temp;
}
%typemap(argout) char ** {
  $result = PyTuple_Pack(2, $result, PyString_FromString(*$1));
}

// Some things are defined in .h files but are not in the library
%ignore gp_filesystem_get_storageinfo;

// Create interfaces to things in these files
%include "gphoto2/gphoto2-context.h"
%include "gphoto2/gphoto2-list.h"
%include "gphoto2/gphoto2-file.h"
%include "gphoto2/gphoto2-port-result.h"

%include "gphoto2/gphoto2-abilities-list.h"
%include "gphoto2/gphoto2-port.h"
%include "gphoto2/gphoto2-widget.h"
%include "gphoto2/gphoto2-filesys.h"
%include "gphoto2/gphoto2-result.h"

%include "gphoto2/gphoto2-camera.h"

// Add a python result error checking function
%pythoncode %{
def check_result(status):
    if isinstance(status, tuple):
        status, result = status
    else:
        result = None
    if status == GP_OK:
        return result
    raise RuntimeError(gp_result_as_string(status))
%}
