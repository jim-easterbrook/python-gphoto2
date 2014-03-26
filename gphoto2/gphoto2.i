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

%feature("autodoc", "2");

%include "typemaps.i"

// Some simple results are passed as pointers
%apply int *OUTPUT { CameraWidgetType * };
%apply int *OUTPUT { int * };
%apply float *OUTPUT { float * };

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
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, 0));
}

// gp_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraList ** (CameraList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraList ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraList, 0));
}

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

// gp_abilities_list_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraAbilitiesList ** (CameraAbilitiesList *temp) {
  $1 = &temp;
}
%typemap(argout) CameraAbilitiesList ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraAbilitiesList, 0));
}

// gp_port_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) GPPort ** (GPPort *temp) {
  $1 = &temp;
}
%typemap(argout) GPPort ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  PyList_Append($result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__GPPort, 0));
}

// gp_list_get_name() and gp_list_get_value() return string pointers in output params
%typemap(in, numinputs=0) char ** (char *temp) {
  $1 = &temp;
}
%typemap(argout) char ** {
  if (!PyList_Check($result)) {
    PyObject* temp = $result;
    $result = PyList_New(1);
    PyList_SetItem($result, 0, temp);
  }
  if (*$1)
    PyList_Append($result, PyString_FromString(*$1));
  else
    PyList_Append($result, Py_None);
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

// Add type specific gp_widget_get_value methods
%inline %{
static int gp_widget_get_value_text(CameraWidget *widget, char **value) {
  return gp_widget_get_value(widget, value);
  };

static int gp_widget_get_value_int(CameraWidget *widget, int *value) {
  return gp_widget_get_value(widget, value);
  };

static int gp_widget_get_value_float(CameraWidget *widget, float *value) {
  return gp_widget_get_value(widget, value);
  };
%}

// Add a python result error checking function
%pythoncode %{
class GPhoto2Error(EnvironmentError):
    pass

def check_result(result):
    if not isinstance(result, (tuple, list)):
        error = result
    elif len(result) == 2:
        error, result = result
    else:
        error = result[0]
        result = result[1:]
    if error < 0:
        raise GPhoto2Error(error, gp_result_as_string(error))
    return result
%}
