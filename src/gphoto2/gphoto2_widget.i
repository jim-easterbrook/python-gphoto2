// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") gphoto2_widget

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_camera.i"
%import "gphoto2_context.i"

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

%rename(CameraWidget) _CameraWidget;

%apply int *OUTPUT { CameraWidgetType * };
%apply int *OUTPUT { int * };
%apply float *OUTPUT { float * };

%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) CameraWidget ** {
  if (*$1 != NULL) {
    // Increment refcount on root widget
    CameraWidget *root;
    int error = gp_widget_get_root(*$1, &root);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error);
      SWIG_fail;
    }
    error = gp_widget_ref(root);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error);
      SWIG_fail;
    }
  }
  // Append result to output object
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}

// Add default destructor to _CameraWidget
// Destructor decrefs root widget
%inline %{
static int widget_dtor(CameraWidget *widget) {
  if (widget == NULL)
    return GP_OK;
  {
    CameraWidget *root;
    int error = gp_widget_get_root(widget, &root);
    if (error < GP_OK)
      return error;
    return gp_widget_unref(root);
  }
}
%}
struct _CameraWidget {};
DEFAULT_DTOR(_CameraWidget, widget_dtor)
%ignore _CameraWidget;

// Define set_value and get_value _CameraWidget member methods
%{
PyObject *_CameraWidget_set_value(CameraWidget *widget, PyObject *py_value) {
  CameraWidgetType type;
  char *char_value = NULL;
  int char_count = 0;
  float float_value;
  int int_value;
  int ecode = 0;
  int error = gp_widget_get_type(widget, &type);
  if (error < GP_OK)
    goto gp_error;
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
  if (error < GP_OK)
    goto gp_error;
  Py_INCREF(Py_None);
  return Py_None;
gp_error:
  PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
fail:
  return NULL;
}
PyObject* (*struct__CameraWidget_set_value)() = _CameraWidget_set_value;

PyObject *_CameraWidget_get_value(CameraWidget *widget) {
  CameraWidgetType type;
  char *char_value = NULL;
  float float_value;
  int int_value;
  PyObject *py_value;
  int error = gp_widget_get_type(widget, &type);
  if (error < GP_OK)
    goto fail;
  switch (type) {
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
    case GP_WIDGET_MENU:
      error = gp_widget_get_value(widget, &char_value);
      if (error < GP_OK)
        goto fail;
      if (char_value != NULL)
        py_value = PyString_FromString(char_value);
      else {
        py_value = Py_None;
        Py_INCREF(Py_None);
        }
      break;
    case GP_WIDGET_RANGE:
      error = gp_widget_get_value(widget, &float_value);
      if (error < GP_OK)
        goto fail;
      py_value = PyFloat_FromDouble(float_value);
      break;
    case GP_WIDGET_TOGGLE:
    case GP_WIDGET_DATE:
      error = gp_widget_get_value(widget, &int_value);
      if (error < GP_OK)
        goto fail;
      py_value = PyInt_FromLong(int_value);
      break;
    default:
      py_value = Py_None;
      Py_INCREF(Py_None);
  }
  return py_value;
fail:
  PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
  return NULL;
}
PyObject* (*struct__CameraWidget_get_value)() = _CameraWidget_get_value;
%}

// Add member methods to _CameraWidget
INT_MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    count_children, (),
    gp_widget_count_children, ($self))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_child, (int child_number, CameraWidget **child),
    gp_widget_get_child, ($self, child_number, child))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_child_by_label, (const char *label, CameraWidget **child),
    gp_widget_get_child_by_label, ($self, label, child))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_child_by_id, (int id, CameraWidget **child),
    gp_widget_get_child_by_id, ($self, id, child))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_child_by_name, (const char *name, CameraWidget **child),
    gp_widget_get_child_by_name, ($self, name, child))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_root, (CameraWidget **root),
    gp_widget_get_root, ($self, root))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_parent, (CameraWidget **parent),
    gp_widget_get_parent, ($self, parent))
PYOBJECT_MEMBER_FUNCTION(_CameraWidget,
    set_value, (PyObject *py_value))
PYOBJECT_MEMBER_FUNCTION(_CameraWidget,
    get_value, ())
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_name, (const char *name),
    gp_widget_set_name, ($self, name))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_name, (const char **name),
    gp_widget_get_name, ($self, name))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_info, (const char *info),
    gp_widget_set_info, ($self, info))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_info, (const char **info),
    gp_widget_get_info, ($self, info))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_id, (int *id),
    gp_widget_get_id, ($self, id))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_type, (CameraWidgetType *type),
    gp_widget_get_type, ($self, type))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_label, (const char **label),
    gp_widget_get_label, ($self, label))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_range, (float min, float max, float increment),
    gp_widget_set_range, ($self, min, max, increment))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_range, (float *min, float *max, float *increment),
    gp_widget_get_range, ($self, min, max, increment))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    add_choice, (const char *choice),
    gp_widget_add_choice, ($self, choice))
INT_MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    count_choices, (),
    gp_widget_count_choices, ($self))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_choice, (int choice_number, const char **choice),
    gp_widget_get_choice, ($self, choice_number, choice))
INT_MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    changed, (),
    gp_widget_changed, ($self))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_changed, (int changed),
    gp_widget_set_changed, ($self, changed))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_readonly, (int readonly),
    gp_widget_set_readonly, ($self, readonly))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_readonly, (int *readonly),
    gp_widget_get_readonly, ($self, readonly))

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
  char *char_value = NULL;
  float float_value;
  int int_value;
  PyObject *py_value;
  int error = gp_widget_get_type(widget, &type);
  PyObject *result = PyList_New(2);
  if (error != GP_OK)
    goto fail;
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
  char *char_value = NULL;
  int char_count = 0;
  float float_value;
  int int_value;
  int ecode = 0;
  int error = gp_widget_get_type(widget, &type);
  if (error != GP_OK)
    goto gp_error;
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
