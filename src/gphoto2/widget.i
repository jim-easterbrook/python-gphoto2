// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-17  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

%import "camera.i"
%import "context.i"

%include "typemaps.i"

IMPORT_GPHOTO2_ERROR()

%rename(CameraWidget) _CameraWidget;

// Make docstring parameter types more Pythonic
%typemap(doc) (CameraWidget *) "$1_name: $*1_type"

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

// Union to hold widget value as a void pointer
%{
typedef union {
  float f_val;
  int   i_val;
  char  *s_val;
} widget_value;
%}

// Use typemaps to check/convert input to gp_widget_set_value
%typemap(in) (const void *value)
             (void *argp=0, int res=0, widget_value temp, int alloc=0) {
  // Slightly dodgy use of first argument to get expected type
  CameraWidgetType type;
  int error = gp_widget_get_type(arg1, &type);
  if (error < GP_OK) {
    GPHOTO2_ERROR(error);
    SWIG_fail;
  }
  switch (type) {
    case GP_WIDGET_MENU:
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
      temp.s_val = NULL;
      res = SWIG_AsCharPtrAndSize($input, &temp.s_val, NULL, &alloc);
      if (!SWIG_IsOK(res)) {
        SWIG_exception_fail(SWIG_ArgError(res),
          "in method '$symname', argument $argnum of type 'char *'");
      }
      $1 = temp.s_val;
      break;
    case GP_WIDGET_RANGE:
      res = SWIG_AsVal_float($input, &temp.f_val);
      if (!SWIG_IsOK(res)) {
        SWIG_exception_fail(SWIG_ArgError(res),
          "in method '$symname', argument $argnum of type 'float'");
      }
      $1 = &temp;
      break;
    case GP_WIDGET_DATE:
    case GP_WIDGET_TOGGLE:
      res = SWIG_AsVal_int($input, &temp.i_val);
      if (!SWIG_IsOK(res)) {
        SWIG_exception_fail(SWIG_ArgError(res),
          "in method '$symname', argument $argnum of type 'int'");
      }
      $1 = &temp;
      break;
    default:
      SWIG_exception_fail(SWIG_ERROR,
        "in method '$symname', cannot set value of widget");
      break;
  }
}
%typemap(freearg, noblock=1) (const void *value) {
  if (alloc$argnum == SWIG_NEWOBJ)
    free(temp$argnum.s_val);
}
%typemap(argout, noblock=1) (CameraWidget *widget, const void *value),
                            (struct _CameraWidget *self, const void *value) {
}

// Use typemaps to convert result of gp_widget_get_value
%typemap(in, noblock=1, numinputs=0) (void *value) {
  widget_value temp;
  $1 = &temp;
}
%typemap(argout) (CameraWidget *widget, void *value),
                 (struct _CameraWidget *self, void *value) {
  PyObject *py_value;
  CameraWidgetType type;
  int error = gp_widget_get_type($1, &type);
  if (error < GP_OK) {
    GPHOTO2_ERROR(error);
    SWIG_fail;
  }
  switch (type) {
    case GP_WIDGET_MENU:
    case GP_WIDGET_TEXT:
    case GP_WIDGET_RADIO:
      if (temp.s_val)
        py_value = PyString_FromString(temp.s_val);
      else {
        Py_INCREF(Py_None);
        py_value = Py_None;
      }
      break;
    case GP_WIDGET_RANGE:
      py_value = PyFloat_FromDouble(temp.f_val);
      break;
    case GP_WIDGET_DATE:
    case GP_WIDGET_TOGGLE:
      py_value = PyInt_FromLong(temp.i_val);
      break;
    default:
      Py_INCREF(Py_None);
      py_value = Py_None;
  }
  $result = SWIG_Python_AppendOutput($result, py_value);
}

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

%feature("docstring") gp_widget_get_children "
Gets all the child widgets of a CameraWidget. The return value is a list
containing a gphoto2 error code and a Python iterator. The iterator can
be used to get each child in sequence.

Parameters
----------
* `widget` :
    a CameraWidget

Returns
-------
a gphoto2 error code and a Python iterator.
";

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

%feature("docstring") gp_widget_get_choices "
Gets all the choice values of a CameraWidget. The return value is a list
containing a gphoto2 error code and a Python iterator. The iterator can
be used to get each choice in sequence.

Parameters
----------
* `widget` :
    a CameraWidget

Returns
-------
a gphoto2 error code and a Python iterator.
";

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
struct _CameraWidget {};
DEFAULT_DTOR(_CameraWidget, widget_dtor)
%ignore _CameraWidget;
%ignore gp_widget_free;
%ignore gp_widget_ref;
%ignore gp_widget_unref;

// Add member methods to _CameraWidget
INT_MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    count_children, (),
    gp_widget_count_children, ($self))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_child, (int child_number, CameraWidget **child),
    gp_widget_get_child, ($self, child_number, child))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_children, (CameraWidgetChildIter* iter),
    gp_widget_get_children, ($self, iter))
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
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    set_value, (const void *value),
    gp_widget_set_value, ($self, value))
MEMBER_FUNCTION(_CameraWidget, CameraWidget,
    get_value, (void *value),
    gp_widget_get_value, ($self, value))
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
    get_choices, (CameraWidgetChoiceIter* iter),
    gp_widget_get_choices, ($self, iter))
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
static int gp_widget_set_value_text(CameraWidget *widget, const char *value) {
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
