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
  if (PyInt_AS_LONG($result) == GP_OK)
    $result = SWIG_Python_AppendOutput(
      $result, SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraWidget, SWIG_POINTER_NEW));
  else {
    Py_INCREF(Py_None);
    $result = SWIG_Python_AppendOutput($result, Py_None);
  }
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

// Replacement gp_widget_get_value() that returns correct type
%rename(gp_widget_get_value) wrap_gp_widget_get_value;
%inline %{
PyObject *wrap_gp_widget_get_value(CameraWidget *widget) {
  CameraWidgetType type;
  int error = gp_widget_get_type(widget, &type);
  PyObject *result = PyList_New(2);
  if (error != GP_OK)
    goto fail;
  char *char_value = NULL;
  float float_value;
  int int_value;
  PyObject *py_value;
  switch (type) {
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
    case GP_WIDGET_MENU:
      error = gp_widget_get_value(widget, &char_value);
      if (error != GP_OK || char_value == NULL)
        goto fail;
      py_value = PyString_FromString(char_value);
      break;
    case GP_WIDGET_RANGE:
      error = gp_widget_get_value(widget, &float_value);
      if (error != GP_OK)
        goto fail;
      py_value = PyFloat_FromDouble(float_value);
      break;
    case GP_WIDGET_TOGGLE:
    case GP_WIDGET_DATE:
      error = gp_widget_get_value(widget, &int_value);
      if (error != GP_OK)
        goto fail;
      py_value = PyInt_FromLong(int_value);
      break;
    default:
      goto fail;
  }
  PyList_SetItem(result, 0, PyInt_FromLong(error));
  PyList_SetItem(result, 1, py_value);
  return result;
fail:
  PyList_SetItem(result, 0, PyInt_FromLong(error));
  Py_INCREF(Py_None);
  PyList_SetItem(result, 1, Py_None);
  return result;
}
%}

// Replacement gp_widget_set_value() that accepts correct type
%rename(gp_widget_set_value) wrap_gp_widget_set_value;
%inline %{
PyObject *wrap_gp_widget_set_value(CameraWidget *widget, PyObject *py_value) {
  CameraWidgetType type;
  int error = gp_widget_get_type(widget, &type);
  if (error != GP_OK)
    goto gp_error;
  char *char_value = NULL;
  int char_count = 0;
  float float_value;
  int int_value;
  int ecode = 0;
  switch (type) {
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
    case GP_WIDGET_MENU:
      ecode = SWIG_AsCharPtrAndSize(py_value, &char_value, NULL, &char_count);
      if (!SWIG_IsOK(ecode)) {
        SWIG_exception_fail(SWIG_ArgError(ecode),
          "in method '" "gp_widget_set_value" "', argument " "2"" of type '" "char *""'");
      }
      error = gp_widget_set_value(widget, char_value);
      break;
    case GP_WIDGET_RANGE:
      ecode = SWIG_AsVal_float(py_value, &float_value);
      if (!SWIG_IsOK(ecode)) {
        SWIG_exception_fail(SWIG_ArgError(ecode),
          "in method '" "gp_widget_set_value" "', argument " "2"" of type '" "float""'");
      }
      error = gp_widget_set_value(widget, &float_value);
      break;
    case GP_WIDGET_TOGGLE:
    case GP_WIDGET_DATE:
      ecode = SWIG_AsVal_int(py_value, &int_value);
      if (!SWIG_IsOK(ecode)) {
        SWIG_exception_fail(SWIG_ArgError(ecode),
          "in method '" "gp_widget_set_value" "', argument " "2"" of type '" "int""'");
      }
      error = gp_widget_set_value(widget, &int_value);
      break;
    default:
      break;
  }
gp_error:
  return SWIG_From_int(error);
fail:
  return NULL;
}
%}
