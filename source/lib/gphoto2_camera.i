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

%module(package="gphoto2.lib") gphoto2_camera

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_abilities_list.i"
%import "gphoto2_filesys.i"
%import "gphoto2_port.i"
%import "gphoto2_result.i"
%import "gphoto2_widget.i"

%feature("autodoc", "2");

%include "typemaps.i"

// gp_camera_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) Camera ** (Camera *temp) {
  $1 = &temp;
}
%typemap(argout) Camera ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__Camera, 0));
}

// gp_camera_get_config() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  $1 = &temp;
}
%typemap(argout) CameraWidget ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, 0));
}

// gp_camera_get_storageinfo() returns an allocated array in an output parameter
%typemap(in, numinputs=0) CameraStorageInformation ** (CameraStorageInformation* temp) {
  $1 = &temp;
}
%typemap(argout) (CameraStorageInformation **, int *) {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyObject* out_list = PyList_New(*$2);
  int n;
  for (n = 0; n < *$2; n++) {
    PyList_SetItem(out_list, n,
                   SWIG_NewPointerObj($1[n], SWIGTYPE_p__CameraStorageInformation, n == 0));
  }
  PyList_Append($result, out_list);
}

%include "gphoto2/gphoto2-camera.h"
