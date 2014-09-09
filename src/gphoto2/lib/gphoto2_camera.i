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

%include "macros.i"

// gp_camera_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) Camera ** (Camera *temp) {
  $1 = &temp;
}
%typemap(argout) Camera ** {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__Camera, SWIG_POINTER_OWN));
}

// gp_camera_get_summary() etc. return a pointer in an output parameter
%typemap(in, numinputs=0) CameraText *summary, CameraText *manual, CameraText *about () {
  $1 = (CameraText *)calloc(1, sizeof(CameraText));
}
%typemap(argout) CameraText *summary, CameraText *manual, CameraText *about {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, SWIGTYPE_p_CameraText, SWIG_POINTER_OWN));
}

// gp_camera_folder_list_files() etc. return a pointer in an output parameter
RETURN_CameraList(CameraList *)

// gp_camera_capture_preview() returns a pointer in an output parameter
RETURN_CameraFile(CameraFile *file_out)
// Redefine signature so other functions that take CameraFile *file aren't affected
int gp_camera_capture_preview(Camera *camera, CameraFile *file_out, GPContext *context);

// gp_camera_capture() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraFilePath *path () {
  $1 = (CameraFilePath *)calloc(1, sizeof(CameraFilePath));
}
%typemap(argout) CameraFilePath *path {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, SWIGTYPE_p_CameraFilePath, SWIG_POINTER_OWN));
}

// Add default constructor and destructor to _Camera
DECLARE_GP_ERROR()
DEFAULT_CTOR(_Camera, gp_camera_new)
DEFAULT_DTOR(_Camera, gp_camera_unref)

// gp_camera_get_storageinfo() returns an allocated array in an output parameter
%typemap(in, numinputs=0)
    CameraStorageInformation ** (CameraStorageInformation* temp) {
  $1 = &temp;
}
%typemap(argout) (CameraStorageInformation **, int *) {
  PyObject* out_list = PyList_New(*$2);
  int n;
  int own = SWIG_POINTER_OWN;
  for (n = 0; n < *$2; n++) {
    PyList_SetItem(out_list, n,
        SWIG_NewPointerObj($1[n], SWIGTYPE_p__CameraStorageInformation, own));
    own = 0;
  }
  $result = SWIG_Python_AppendOutput($result, out_list);
}

// gp_camera_wait_for_event() returns two pointers in output parameters
%typemap(in, numinputs=0) CameraEventType * (CameraEventType temp) {
  $1 = &temp;
}
%typemap(in, numinputs=0) void ** eventdata (void* temp) {
  $1 = &temp;
}
%typemap(argout) CameraEventType * {
  $result = SWIG_Python_AppendOutput($result, PyInt_FromLong(*$1));
}

// Add __str__ method to CameraText
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "tp_str", functype="reprfunc") CameraText::__str__;
#endif // SWIGPYTHON_BUILTIN
%extend CameraText {
  char *__str__() {
    return $self->text;
  }
};

// Don't wrap deprecated functions
%ignore gp_camera_free;

// These structures are private
%ignore _CameraFunctions;

// Other structures are read only
%immutable;

%include "gphoto2/gphoto2-camera.h"
