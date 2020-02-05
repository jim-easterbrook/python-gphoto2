// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-20  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") widget

%include "common/preamble.i"

%rename(CameraWidget) _CameraWidget;

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
  $result = SWIG_Python_AppendOutput(
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
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}

// Make docstring parameter types more Pythonic
%typemap(doc) (CameraWidget *) "$1_name: gphoto2.$*1_type"

#ifndef SWIGIMPORTED

%apply int *OUTPUT { CameraWidgetType * };
%apply int *OUTPUT { int * };
%apply float *OUTPUT { float * };

// gp_widget_set_value uses float* and int* as input values
%apply float *INPUT {const float *value}
%apply int   *INPUT {const int   *value}
%typemap(argout) const float *value {}
%typemap(argout) const int   *value {}

// Use typechecks to select gp_widget_set_value according to widget type
%typecheck(SWIG_TYPECHECK_STRING) (CameraWidget *widget, const char *value),
                                  (struct _CameraWidget *self, char const *value)  {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = ((type == GP_WIDGET_MENU) || (type == GP_WIDGET_TEXT) || (type == GP_WIDGET_RADIO)) ? 1 : 0;
        }
    }
}

%typecheck(SWIG_TYPECHECK_FLOAT) (CameraWidget *widget, const float *value),
                                 (struct _CameraWidget *self, float const *value) {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = (type == GP_WIDGET_RANGE) ? 1 : 0;
        }
    }
}

%typecheck(SWIG_TYPECHECK_INTEGER) (CameraWidget *widget, const int *value),
                                   (struct _CameraWidget *self, int const *value)  {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = ((type == GP_WIDGET_DATE) || (type == GP_WIDGET_TOGGLE)) ? 1 : 0;
        }
    }
}

// Create overloaded gp_widget_set_value
int gp_widget_set_value(CameraWidget *widget, const char *value);
int gp_widget_set_value(CameraWidget *widget, const float *value);
int gp_widget_set_value(CameraWidget *widget, const int *value);

// Ignore original void* version
%ignore gp_widget_set_value(CameraWidget *widget, const void *value);

// Use typechecks to select gp_widget_get_value according to widget type
%typecheck(SWIG_TYPECHECK_STRING) (CameraWidget *widget, char **value),
                                  (struct _CameraWidget *self, char **value)  {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = ((type == GP_WIDGET_MENU) || (type == GP_WIDGET_TEXT) || (type == GP_WIDGET_RADIO)) ? 1 : 0;
        }
    }
}

%typecheck(SWIG_TYPECHECK_FLOAT) (CameraWidget *widget, float *value),
                                 (struct _CameraWidget *self, float *value) {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = (type == GP_WIDGET_RANGE) ? 1 : 0;
        }
    }
}

%typecheck(SWIG_TYPECHECK_INTEGER) (CameraWidget *widget, int *value),
                                   (struct _CameraWidget *self, int *value)  {
    CameraWidget     *widget;
    CameraWidgetType type;
    int              error;

    $1 = 0;
    error = SWIG_ConvertPtr($input, (void **)&widget, SWIGTYPE_p__CameraWidget, 0);
    if (SWIG_IsOK(error)) {
        error = gp_widget_get_type(widget, &type);
        if (error >= GP_OK) {
            $1 = ((type == GP_WIDGET_DATE) || (type == GP_WIDGET_TOGGLE)) ? 1 : 0;
        }
    }
}

// Create overloaded gp_widget_get_value
int gp_widget_get_value(CameraWidget *widget, char **value);
int gp_widget_get_value(CameraWidget *widget, float *value);
int gp_widget_get_value(CameraWidget *widget, int *value);

// Ignore original void* version
%ignore gp_widget_get_value(CameraWidget *widget, void *value);

// function to allow python iter() to be called with python object
#if defined(SWIGPYTHON_BUILTIN)
%ignore make_iterator;
%inline %{
static PyObject* make_iterator(PyObject* self)
{
  Py_INCREF(self);
  return self;
}
%}
#endif

// macro to implement iterator objects
%define ITERATOR(iter_type, function, result_type)

#if defined(SWIGPYTHON_BUILTIN)
  %feature("python:tp_iter") iter_type "make_iterator";
  %feature("python:slot", "tp_iternext", functype="iternextfunc") iter_type::__next__;
#else
  %extend iter_type {
    %pythoncode {
      def __iter__(self):
          return self
      def next(self):
          return self.__next__()
    }
  }
#endif

%ignore iter_type::parent;
%ignore iter_type::idx;
%ignore iter_type::len;
%inline %{
typedef struct iter_type {
  CameraWidget* parent;
  int           idx;
  int           len;
} iter_type;
%}

CALLOC_ARGOUT(iter_type*)

%exception iter_type::__next__ {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend iter_type {
  result_type* __next__() {
    result_type* result;
    int error;
    if ($self->idx >= $self->len)
    {
      PyErr_SetString(PyExc_StopIteration, "End of iteration");
      return NULL;
    }
    error = function($self->parent, $self->idx, &result);
    $self->idx++;
    if (error < GP_OK)
    {
      GPHOTO2_ERROR(error)
      return NULL;
    }
    return result;
  }
}
%enddef

// Add gp_widget_get_children() method that returns an iterator
ITERATOR(CameraWidgetChildIter, gp_widget_get_child, CameraWidget)

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

%inline %{
int gp_widget_get_children(CameraWidget* widget, CameraWidgetChildIter* iter) {
  iter->parent = widget;
  iter->idx = 0;
  iter->len = gp_widget_count_children(widget);
  if (iter->len < GP_OK)
    return iter->len;
  return GP_OK;
};
%}

// Add gp_widget_get_choices() method that returns an iterator
ITERATOR(CameraWidgetChoiceIter, gp_widget_get_choice, const char)

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

%inline %{
int gp_widget_get_choices(CameraWidget* widget, CameraWidgetChoiceIter* iter) {
  iter->parent = widget;
  iter->idx = 0;
  iter->len = gp_widget_count_choices(widget);
  if (iter->len < GP_OK)
    return iter->len;
  return GP_OK;
};
%}

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

// Add member methods to _CameraWidget
INT_MEMBER_FUNCTION(_CameraWidget,
    count_children, (),
    gp_widget_count_children, ($self))
MEMBER_FUNCTION(_CameraWidget,
    get_child, (int child_number, CameraWidget **child),
    gp_widget_get_child, ($self, child_number, child))
MEMBER_FUNCTION(_CameraWidget,
    get_children, (CameraWidgetChildIter* iter),
    gp_widget_get_children, ($self, iter))
MEMBER_FUNCTION(_CameraWidget,
    get_child_by_label, (const char *label, CameraWidget **child),
    gp_widget_get_child_by_label, ($self, label, child))
MEMBER_FUNCTION(_CameraWidget,
    get_child_by_id, (int id, CameraWidget **child),
    gp_widget_get_child_by_id, ($self, id, child))
MEMBER_FUNCTION(_CameraWidget,
    get_child_by_name, (const char *name, CameraWidget **child),
    gp_widget_get_child_by_name, ($self, name, child))
MEMBER_FUNCTION(_CameraWidget,
    get_root, (CameraWidget **root),
    gp_widget_get_root, ($self, root))
MEMBER_FUNCTION(_CameraWidget,
    get_parent, (CameraWidget **parent),
    gp_widget_get_parent, ($self, parent))
MEMBER_FUNCTION(_CameraWidget,
    set_value, (const char *value),
    gp_widget_set_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    set_value, (const float *value),
    gp_widget_set_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    set_value, (const int *value),
    gp_widget_set_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    get_value, (char **value),
    gp_widget_get_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    get_value, (float *value),
    gp_widget_get_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    get_value, (int *value),
    gp_widget_get_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget,
    set_name, (const char *name),
    gp_widget_set_name, ($self, name))
MEMBER_FUNCTION(_CameraWidget,
    get_name, (const char **name),
    gp_widget_get_name, ($self, name))
MEMBER_FUNCTION(_CameraWidget,
    set_info, (const char *info),
    gp_widget_set_info, ($self, info))
MEMBER_FUNCTION(_CameraWidget,
    get_info, (const char **info),
    gp_widget_get_info, ($self, info))
MEMBER_FUNCTION(_CameraWidget,
    get_id, (int *id),
    gp_widget_get_id, ($self, id))
MEMBER_FUNCTION(_CameraWidget,
    get_type, (CameraWidgetType *type),
    gp_widget_get_type, ($self, type))
MEMBER_FUNCTION(_CameraWidget,
    get_label, (const char **label),
    gp_widget_get_label, ($self, label))
MEMBER_FUNCTION(_CameraWidget,
    set_range, (float min, float max, float increment),
    gp_widget_set_range, ($self, min, max, increment))
MEMBER_FUNCTION(_CameraWidget,
    get_range, (float *min, float *max, float *increment),
    gp_widget_get_range, ($self, min, max, increment))
MEMBER_FUNCTION(_CameraWidget,
    add_choice, (const char *choice),
    gp_widget_add_choice, ($self, choice))
INT_MEMBER_FUNCTION(_CameraWidget,
    count_choices, (),
    gp_widget_count_choices, ($self))
MEMBER_FUNCTION(_CameraWidget,
    get_choices, (CameraWidgetChoiceIter* iter),
    gp_widget_get_choices, ($self, iter))
MEMBER_FUNCTION(_CameraWidget,
    get_choice, (int choice_number, const char **choice),
    gp_widget_get_choice, ($self, choice_number, choice))
INT_MEMBER_FUNCTION(_CameraWidget,
    changed, (),
    gp_widget_changed, ($self))
MEMBER_FUNCTION(_CameraWidget,
    set_changed, (int changed),
    gp_widget_set_changed, ($self, changed))
MEMBER_FUNCTION(_CameraWidget,
    set_readonly, (int readonly),
    gp_widget_set_readonly, ($self, readonly))
MEMBER_FUNCTION(_CameraWidget,
    get_readonly, (int *readonly),
    gp_widget_get_readonly, ($self, readonly))

// Ignore some functions
%ignore gp_widget_new;
%ignore gp_widget_free;
%ignore gp_widget_ref;
%ignore gp_widget_unref;

#endif //ifndef SWIGIMPORTED

struct _CameraWidget {};
DEFAULT_DTOR(_CameraWidget, widget_dtor)
%ignore _CameraWidget;

%include "gphoto2/gphoto2-widget.h"
