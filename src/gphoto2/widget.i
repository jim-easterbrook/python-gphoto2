// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-24  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This file is part of python-gphoto2.
//
// python-gphoto2 is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// python-gphoto2 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with python-gphoto2.  If not, see <https://www.gnu.org/licenses/>.

%module(package="gphoto2") widget

%include "common/preamble.i"

%rename(CameraWidget) _CameraWidget;

// Deprecate some functions intended for camera drivers (2023-07-20)
DEPRECATED(gp_widget_add_choice,)
DEPRECATED(_CameraWidget::add_choice, 1)
DEPRECATED(gp_widget_set_info,)
DEPRECATED(_CameraWidget::set_info, 1)
DEPRECATED(gp_widget_set_name,)
DEPRECATED(_CameraWidget::set_name, 1)
DEPRECATED(gp_widget_set_range,)
DEPRECATED(_CameraWidget::set_range, 1)
DEPRECATED(gp_widget_set_readonly,)
DEPRECATED(_CameraWidget::set_readonly, 1)

/* These are the only wrapped functions that return a CameraWidget:
gp_widget_get_child(..., CameraWidget **child)
gp_widget_get_child_by_label(..., CameraWidget **child)
gp_widget_get_child_by_id(..., CameraWidget **child)
gp_widget_get_child_by_name(..., CameraWidget **child)
gp_widget_get_root(..., CameraWidget **root)
gp_widget_get_parent(..., CameraWidget **parent)
gp_camera_get_config(..., CameraWidget **window, ...)
gp_camera_get_single_config(..., CameraWidget **widget, ...)

The gp_camera_get_xxx functions return a new widget, which may be the root of a
tree. The others all return a pointer to an existing widget. To ensure this
pointer remains valid the function must increment the ref count of the root
widget, then decrement it when the returned pointer is destroyed.

Fortunately the function signatures use different names for the CameraWidget
result, so it's easy to use different typemaps for the different functions.
Beware of changes in the libgphoto2 definitions though.
*/

%typemap(in, numinputs=0) CameraWidget ** (CameraWidget *temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) CameraWidget **window, CameraWidget **widget {
  // Append result to output object
  $result = SWIG_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}
%typemap(argout) CameraWidget **child, CameraWidget **root, CameraWidget **parent {
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
  $result = SWIG_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}

// Make docstring parameter types more Pythonic
%typemap(doc) (CameraWidget *) "$1_name: gphoto2.$*1_type"

%apply int *OUTPUT { CameraWidgetType * };
%apply int *OUTPUT { int * };
%apply float *OUTPUT { float * };

// Use typemaps to convert result of gp_widget_get_value
%{
typedef union {
    int int_val;
    float flt_val;
    char* str_val;
} VoidValue;
%}
%typemap(in, numinputs=0) (void *value_out) (VoidValue temp) {
  temp.str_val = NULL;
  $1 = &temp;
}
%typemap(argout) (CameraWidget *widget, void *value_out),
                 (struct _CameraWidget *self, void *value_out) {
  CameraWidgetType type;
  PyObject* py_value = NULL;
  VoidValue* value = (VoidValue*) $2;
  int error = gp_widget_get_type($1, &type);
  if (error < GP_OK) {
    GPHOTO2_ERROR(error);
    SWIG_fail;
  }
  switch (type) {
    case GP_WIDGET_DATE:
    case GP_WIDGET_TOGGLE:
      py_value = SWIG_From_int(value->int_val);
      break;
    case GP_WIDGET_RANGE:
      py_value = SWIG_From_float(value->flt_val);
      break;
    case GP_WIDGET_MENU:
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
      if (value->str_val) {
        py_value = PyString_FromString(value->str_val);
      } else {
        SWIG_Py_INCREF(Py_None);
        py_value = Py_None;
      }
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError, "Unsupported widget type");
      SWIG_fail;
  }
  $result = SWIG_AppendOutput($result, py_value);
}
%typemap(doc) (void *value) "$1_name: int/float/str"

// Redefine signature of gp_widget_get_value to select correct typemaps
int gp_widget_get_value(CameraWidget *widget, void *value_out);
%ignore gp_widget_get_value;

// Use typemaps to convert input to gp_widget_set_value
%typemap(in, noblock=1) const void *value
    (VoidValue value, int alloc = 0, int res = 0, CameraWidgetType type) {
  // Camera widget is stored in arg1 as it's definitely the first argument to gp_widget_set_value
  res = gp_widget_get_type(arg1, &type);
  if (res < GP_OK) {
    GPHOTO2_ERROR(res);
    SWIG_fail;
  }
  switch (type) {
    case GP_WIDGET_DATE:
    case GP_WIDGET_TOGGLE:
      res = SWIG_AsVal_int($input, &value.int_val);
      if (!SWIG_IsOK(res)) {
        %argument_fail(res, int, $symname, $argnum);
      }
      $1 = &value.int_val;
      break;
    case GP_WIDGET_RANGE:
      res = SWIG_AsVal_float($input, &value.flt_val);
      if (!SWIG_IsOK(res)) {
        %argument_fail(res, float, $symname, $argnum);
      }
      $1 = &value.flt_val;
      break;
    case GP_WIDGET_MENU:
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
      res = SWIG_AsCharPtrAndSize($input, &value.str_val, NULL, &alloc);
      if (!SWIG_IsOK(res)) {
        %argument_fail(res, str, $symname, $argnum);
      }
      // Note this is a pointer set by SWIG_AsCharPtrAndSize, not the address of value
      $1 = value.str_val;
      break;
    default:
      PyErr_SetString(PyExc_RuntimeError, "Unsupported widget type");
      SWIG_fail;
  }
}
%typemap(freearg) const void *value {
  if (alloc$argnum == SWIG_NEWOBJ) free($1);
}

// Turn on default exception handling
DEFAULT_EXCEPTION

#ifndef SWIGIMPORTED

// Typemaps for iterator return values
%typemap(in, numinputs=0) PyObject **iter (PyObject* temp=NULL) {
    $1 = &temp;
}
%typemap(argout) PyObject **iter {
    if (!*$1)
        *$1 = SWIG_Py_Void();
    $result = SWIG_AppendOutput($result, *$1);
}

// Add gp_widget_get_children() method that returns an iterator
%feature("docstring") gp_widget_get_children "Gets all the child widgets of a CameraWidget. The return value is a list
containing a gphoto2 error code and a Python iterator. The iterator can
be used to get each child in sequence.

Parameters
----------
* `widget` :
    a CameraWidget

Returns
-------
a gphoto2 error code and a Python iterator.

See also gphoto2.CameraWidget.get_children"

%feature("docstring") _CameraWidget::get_children "Gets all the child widgets of a CameraWidget. The return value is a
Python iterator which can be used to get each child in sequence.

Returns
-------
a Python iterator.

See also gphoto2.gp_widget_get_children"

%noexception gp_widget_get_children;
%inline %{
static int gp_widget_get_children(CameraWidget* widget, PyObject **iter) {
    PyObject* py_self = SWIG_Python_NewPointerObj(
        NULL, widget, SWIGTYPE_p__CameraWidget, 0);
    *iter = PySeqIter_New(py_self);
    SWIG_Py_DECREF(py_self);
    return GP_OK;
};
%}

// Add gp_widget_get_choices() method that returns an iterator
%feature("docstring") gp_widget_get_choices "Gets all the choice values of a CameraWidget. The return value is a list
containing a gphoto2 error code and a Python iterator. The iterator can
be used to get each choice in sequence.

Parameters
----------
* `widget` :
    a CameraWidget

Returns
-------
a gphoto2 error code and a Python iterator.

See also gphoto2.CameraWidget.get_choices"

%feature("docstring") _CameraWidget::get_choices "Gets all the choice values of a CameraWidget. The return value is a
Python iterator which can be used to get each choice in sequence.

Returns
-------
a Python iterator.

See also gphoto2.gp_widget_get_choices"

%noexception gp_widget_get_choices;
%inline %{
int gp_widget_get_choices(CameraWidget* widget, PyObject **iter) {
    int result = GP_OK;
    int len = gp_widget_count_choices(widget);
    if (len < GP_OK)
        return len;
    PyObject* list = PyTuple_New(len);
    const char *choice = NULL;
    for (int idx = 0; idx < len; idx++) {
        result = gp_widget_get_choice(widget, idx, &choice);
        if (result != GP_OK) {
            SWIG_Py_DECREF(list);
            return result;
        }
        PyTuple_SET_ITEM(list, idx, PyUnicode_FromString(choice));
    }
    *iter = PySeqIter_New(list);
    SWIG_Py_DECREF(list);
    return result;
};
%}

#endif //ifndef SWIGIMPORTED

// Add default destructor to _CameraWidget
// Destructor decrefs root widget
%{
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


// Make _CameraWidget more like a list
%feature("python:slot", "sq_item", functype="ssizeargfunc")
    _CameraWidget::__getitem__;
%extend _CameraWidget {
    void __getitem__(int child_number, CameraWidget **child) {
        if ((child_number < 0) ||
            (child_number >= gp_widget_count_children($self))) {
            PyErr_SetNone(PyExc_IndexError);
            return;
        }
        int result = gp_widget_get_child($self, child_number, child);
        if (result < GP_OK) GPHOTO2_ERROR(result)
    }
};

// Add member methods to _CameraWidget
LEN_MEMBER_FUNCTION(_CameraWidget, gp_widget_count_children)
MEMBER_FUNCTION(_CameraWidget,
    int, count_children, (),
    gp_widget_count_children, ($self), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_child, (int child_number, CameraWidget **child),
    gp_widget_get_child, ($self, child_number, child), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_children, (PyObject** iter),
    gp_widget_get_children, ($self, iter), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_child_by_label, (const char *label, CameraWidget **child),
    gp_widget_get_child_by_label, ($self, label, child), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_child_by_id, (int id, CameraWidget **child),
    gp_widget_get_child_by_id, ($self, id, child), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_child_by_name, (const char *name, CameraWidget **child),
    gp_widget_get_child_by_name, ($self, name, child), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_root, (CameraWidget **root),
    gp_widget_get_root, ($self, root), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_parent, (CameraWidget **parent),
    gp_widget_get_parent, ($self, parent), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_value, (const void *value),
    gp_widget_set_value, ($self, value), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_value, (void *value_out),
    gp_widget_get_value, ($self, value_out), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_name, (const char *name),
    gp_widget_set_name, ($self, name), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_name, (const char **name),
    gp_widget_get_name, ($self, name), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_info, (const char *info),
    gp_widget_set_info, ($self, info), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_info, (const char **info),
    gp_widget_get_info, ($self, info), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_id, (int *id),
    gp_widget_get_id, ($self, id), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_type, (CameraWidgetType *type),
    gp_widget_get_type, ($self, type), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_label, (const char **label),
    gp_widget_get_label, ($self, label), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_range, (float min, float max, float increment),
    gp_widget_set_range, ($self, min, max, increment), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_range, (float *min, float *max, float *increment),
    gp_widget_get_range, ($self, min, max, increment), )
MEMBER_FUNCTION(_CameraWidget,
    void, add_choice, (const char *choice),
    gp_widget_add_choice, ($self, choice), )
MEMBER_FUNCTION(_CameraWidget,
    int, count_choices, (),
    gp_widget_count_choices, ($self), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_choices, (PyObject **iter),
    gp_widget_get_choices, ($self, iter), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_choice, (int choice_number, const char **choice),
    gp_widget_get_choice, ($self, choice_number, choice), )
MEMBER_FUNCTION(_CameraWidget,
    int, changed, (),
    gp_widget_changed, ($self), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_changed, (int changed),
    gp_widget_set_changed, ($self, changed), )
MEMBER_FUNCTION(_CameraWidget,
    void, set_readonly, (int readonly),
    gp_widget_set_readonly, ($self, readonly), )
MEMBER_FUNCTION(_CameraWidget,
    void, get_readonly, (int *readonly),
    gp_widget_get_readonly, ($self, readonly), )

// Ignore some functions
%ignore gp_widget_new;
%ignore gp_widget_free;
%ignore gp_widget_ref;
%ignore gp_widget_unref;

// Turn off default exception handling
%noexception;

%include "gphoto2/gphoto2-widget.h"
