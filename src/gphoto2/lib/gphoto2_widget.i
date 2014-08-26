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

// several methods return a CameraWidget pointer in an output parameter
// most of them do not create a new object
%inline %{
#define OWN_gp_widget_new                SWIG_POINTER_NEW
#define OWN_gp_widget_get_child          0
#define OWN_gp_widget_get_child_by_id    0
#define OWN_gp_widget_get_child_by_label 0
#define OWN_gp_widget_get_child_by_name  0
#define OWN_gp_widget_get_parent         0
#define OWN_gp_widget_get_root           0
%}
%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  $1 = &temp;
}
%typemap(argout) CameraWidget ** {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, OWN_$symname));
}

// Add default constructor and destructor to _CameraWidget
DECLARE_GP_ERROR()
struct _CameraWidget {};
// Constructor is a copy constructor
%extend _CameraWidget {
  _CameraWidget(struct _CameraWidget *widget) {
    gp_widget_ref(widget);
    return widget;
  }
};
DEFAULT_DTOR(_CameraWidget, gp_widget_unref)
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
