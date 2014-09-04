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

%module(package="gphoto2.lib") gphoto2_widget

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_camera.i"
%import "gphoto2_context.i"

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

%apply int *OUTPUT { CameraWidgetType * };
%apply int *OUTPUT { int * };
%apply float *OUTPUT { float * };

%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  $1 = &temp;
}
%typemap(argout) CameraWidget ** {
  // Increment refcount on root widget
  CameraWidget *root;
  if (PyInt_AS_LONG($result) == GP_OK)
    $result = SWIG_From_int(gp_widget_get_root(*$1, &root));
  if (PyInt_AS_LONG($result) == GP_OK)
    $result = SWIG_From_int(gp_widget_ref(root));
  // Append result to output object
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, SWIG_POINTER_NEW));
}

// Add default constructor and destructor to _CameraWidget
DECLARE_GP_ERROR()
// Destructor decrefs root widget
%inline %{
static int widget_dtor(CameraWidget *widget) {
  CameraWidget *root;
  int error;
  error = gp_widget_get_root(widget, &root);
  if (error != GP_OK)
    return error;
  return gp_widget_unref(root);
}
%}
struct _CameraWidget {};
// Constructor is a copy constructor that increfs root widget
%extend _CameraWidget {
  _CameraWidget(struct _CameraWidget *widget) {
    CameraWidget *root;
    if (gp_widget_get_root(widget, &root) != GP_OK)
      return NULL;
    if (gp_widget_ref(root) != GP_OK)
      return NULL;
    return widget;
  }
};
DEFAULT_DTOR(_CameraWidget, widget_dtor)
%ignore _CameraWidget;

// some methods return string pointers in output params
STRING_ARGOUT()

%inline %{
// Add type specific gp_widget_get_value methods
static int gp_widget_get_value_text(CameraWidget *widget, char **value) {
  return gp_widget_get_value(widget, value);
  };

static int gp_widget_get_value_int(CameraWidget *widget, int *value) {
  return gp_widget_get_value(widget, value);
  };

static int gp_widget_get_value_float(CameraWidget *widget, float *value) {
  return gp_widget_get_value(widget, value);
  };

// Add type specific gp_widget_set_value methods
static int gp_widget_set_value_text(CameraWidget *widget, char *value) {
  return gp_widget_set_value(widget, value);
  };

static int gp_widget_set_value_int(CameraWidget *widget, const int value) {
  return gp_widget_set_value(widget, &value);
  };

static int gp_widget_set_value_float(CameraWidget *widget, const float value) {
  return gp_widget_set_value(widget, &value);
  };
%}

%include "gphoto2/gphoto2-widget.h"
