// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-21  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") context

%include "common/preamble.i"

%rename(Context) _GPContext;

#ifndef SWIGIMPORTED

// Make docstring parameter types more Pythonic
%typemap(doc) GPContext * "$1_name: gphoto2.$*1_type";

// gp_camera_autodetect() returns a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// Ignore "backend" functions
%ignore gp_context_cancel;
%ignore gp_context_error;
%ignore gp_context_idle;
%ignore gp_context_message;
%ignore gp_context_progress_start;
%ignore gp_context_progress_stop;
%ignore gp_context_progress_update;
%ignore gp_context_question;
%ignore gp_context_ref;
%ignore gp_context_status;
%ignore gp_context_unref;

// Structs to store callback details
%ignore CallbackDetails::context;
%ignore CallbackDetails::func;
%ignore CallbackDetails::data;
%ignore CallbackDetails::remove;
%ignore del_CallbackDetails;

%inline %{
typedef void (*RemoveFunc) (GPContext *context, void *func, void *data);

typedef struct CallbackDetails {
    GPContext   *context;
    PyObject    *func_1;
    PyObject    *func_2;
    PyObject    *func_3;
    PyObject    *data;
    RemoveFunc  remove;
} CallbackDetails;

// Function to remove progress callbacks, compatible with RemoveFunc
static void unset_progress_funcs(GPContext *context,
                                 GPContextProgressStartFunc start_func,
                                 void *data) {
    gp_context_set_progress_funcs(context, NULL, NULL, NULL, NULL);
};

// Destructor
static int del_CallbackDetails(struct CallbackDetails *this) {
    if (this->context)
        this->remove(this->context, NULL, NULL);
    Py_XDECREF(this->func_1);
    Py_XDECREF(this->func_2);
    Py_XDECREF(this->func_3);
    Py_XDECREF(this->data);
    free(this);
    return GP_OK;
};
%}
DEFAULT_DTOR(CallbackDetails, del_CallbackDetails);

// Define wrapper functions to call Python callbacks from C callbacks
%define CB_WRAPPER(rtn_type, cb_name, cb_args, py3_arglist, py2_arglist, function)
%{
static rtn_type cb_name cb_args {
    PyGILState_STATE gstate = PyGILState_Ensure();
    CallbackDetails *this = data;
    PyObject *result = NULL;
    PyObject *arglist = NULL;
    PyObject *self = NULL;
%}
#if #rtn_type == "int"
%{
    rtn_type c_result = 0;
%}
#elif #rtn_type == "GPContextFeedback"
%{
    rtn_type c_result = GP_CONTEXT_FEEDBACK_OK;
%}
#endif
%{
    PyObject *py_context = SWIG_NewPointerObj(
        SWIG_as_voidptr(context), SWIGTYPE_p__GPContext, 0);
    arglist = Py_BuildValue py3_arglist;
    if (arglist == NULL) {
        PyErr_Print();
        goto fail;
    }
    result = PyObject_CallObject(function, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        PyErr_Print();
        goto fail;
    }
%}
#if #rtn_type != "void"
%{
    c_result = PyInt_AsLong(result);
%}
#endif
%{
    Py_DECREF(result);
fail:
    PyGILState_Release(gstate);
%}
#if #rtn_type != "void"
%{
    return c_result;
%}
#endif
%{
};
%}
%enddef // CB_WRAPPER

CB_WRAPPER(void, wrap_idle_func, (GPContext *context, void *data),
           ("(OO)", py_context, this->data),
           ("(OO)", py_context, this->data),
           this->func_1)

CB_WRAPPER(void, wrap_error_func, (GPContext *context, const char *text, void *data),
           ("(OyO)", py_context, text, this->data),
           ("(OsO)", py_context, text, this->data),
           this->func_1)

CB_WRAPPER(void, wrap_status_func, (GPContext *context, const char *text, void *data),
           ("(OyO)", py_context, text, this->data),
           ("(OsO)", py_context, text, this->data),
           this->func_1)

CB_WRAPPER(void, wrap_message_func, (GPContext *context, const char *text, void *data),
           ("(OyO)", py_context, text, this->data),
           ("(OsO)", py_context, text, this->data),
           this->func_1)

CB_WRAPPER(GPContextFeedback, wrap_question_func,
           (GPContext *context, const char *text, void *data),
           ("(OyO)", py_context, text, this->data),
           ("(OsO)", py_context, text, this->data),
           this->func_1)

CB_WRAPPER(GPContextFeedback, wrap_cancel_func, (GPContext *context, void *data),
           ("(OO)", py_context, this->data),
           ("(OO)", py_context, this->data),
           this->func_1)

CB_WRAPPER(int, py_progress_start,
           (GPContext *context, float target, const char *text, void *data),
           ("(OfyO)", py_context, target, text, this->data),
           ("(OfsO)", py_context, target, text, this->data),
           this->func_1)

CB_WRAPPER(void, py_progress_update,
           (GPContext *context, unsigned int id, float current, void *data),
           ("(OifO)", py_context, id, current, this->data),
           ("(OifO)", py_context, id, current, this->data),
           this->func_2)

CB_WRAPPER(void, py_progress_stop, (GPContext *context, unsigned int id, void *data),
           ("(OiO)", py_context, id, this->data),
           ("(OiO)", py_context, id, this->data),
           this->func_3)

// Typemaps for all callback setting functions
%typemap(in) void *data {
    _global_callbacks->data = $input;
    Py_INCREF(_global_callbacks->data);
    $1 = _global_callbacks;
}
%typemap(doc) void *data "$1_name: object"

%typemap(check) GPContext *context {
    _global_callbacks->context = $1;
}

// Macro to define typemaps for the six single callback function variants
%define SINGLE_CALLBACK_FUNCTION(cb_func_type, remove_func, cb_wrapper)

%typemap(arginit) cb_func_type (CallbackDetails *_global_callbacks) {
    _global_callbacks = malloc(sizeof(CallbackDetails));
    if (!_global_callbacks) {
        PyErr_SetNone(PyExc_MemoryError);
        SWIG_fail;
    }
    _global_callbacks->context = NULL;
    _global_callbacks->func_1 = NULL;
    _global_callbacks->func_2 = NULL;
    _global_callbacks->func_3 = NULL;
    _global_callbacks->data = NULL;
    _global_callbacks->remove = (RemoveFunc) remove_func;
}
%typemap(freearg) cb_func_type {
    if (_global_callbacks)
        del_CallbackDetails(_global_callbacks);
}
%typemap(in) cb_func_type {
    if (!PyCallable_Check($input)) {
        %argument_fail(SWIG_TypeError, callable, $symname, $argnum);
    }
    _global_callbacks->func_1 = $input;
    Py_INCREF(_global_callbacks->func_1);
    $1 = (cb_func_type) cb_wrapper;
}
%typemap(doc) cb_func_type "$1_name: callable function"

%typemap(argout) cb_func_type {
    $result = SWIG_Python_AppendOutput($result,
        SWIG_NewPointerObj(_global_callbacks, SWIGTYPE_p_CallbackDetails, SWIG_POINTER_OWN));
    _global_callbacks = NULL;
}

%enddef // SINGLE_CALLBACK_FUNCTION

SINGLE_CALLBACK_FUNCTION(GPContextIdleFunc,
                         gp_context_set_idle_func, wrap_idle_func)
SINGLE_CALLBACK_FUNCTION(GPContextErrorFunc,
                         gp_context_set_error_func, wrap_error_func)
SINGLE_CALLBACK_FUNCTION(GPContextStatusFunc,
                         gp_context_set_status_func, wrap_status_func)
SINGLE_CALLBACK_FUNCTION(GPContextMessageFunc,
                         gp_context_set_message_func, wrap_message_func)
SINGLE_CALLBACK_FUNCTION(GPContextQuestionFunc,
                         gp_context_set_question_func, wrap_question_func)
SINGLE_CALLBACK_FUNCTION(GPContextCancelFunc,
                         gp_context_set_cancel_func, wrap_cancel_func)

// Progress callbacks are more complicated
// Use macro for first function
SINGLE_CALLBACK_FUNCTION(GPContextProgressStartFunc,
                         unset_progress_funcs, py_progress_start)

// Use typemaps for other two functions
%typemap(in) GPContextProgressUpdateFunc {
    if (!PyCallable_Check($input)) {
        %argument_fail(SWIG_TypeError, callable, $symname, $argnum);
    }
    _global_callbacks->func_2 = $input;
    Py_INCREF(_global_callbacks->func_2);
    $1 = (GPContextProgressUpdateFunc) py_progress_update;
}
%typemap(doc) GPContextProgressUpdateFunc "$1_name: callable function"

%typemap(in) GPContextProgressStopFunc {
    if (!PyCallable_Check($input)) {
        %argument_fail(SWIG_TypeError, callable, $symname, $argnum);
    }
    _global_callbacks->func_3 = $input;
    Py_INCREF(_global_callbacks->func_3);
    $1 = (GPContextProgressStopFunc) py_progress_stop;
}
%typemap(doc) GPContextProgressStopFunc "$1_name: callable function"

// Add default constructor and destructor to _GPContext
struct _GPContext {};
%extend _GPContext {
  _GPContext() {
    return gp_context_new();
  }
  ~_GPContext() {
    gp_context_unref($self);
  }
};
%newobject gp_context_new;
%delobject gp_context_unref;

// Add member methods to _GPContext
%exception _GPContext::camera_autodetect {
  if (PyErr_WarnEx(PyExc_DeprecationWarning,
      "Camera.autodetect replaces Context().camera_autodetect", 1) < 0) SWIG_fail;
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend _GPContext {
  void camera_autodetect(CameraList *list) {
    int error = gp_camera_autodetect(list, $self);
    if (error < GP_OK) GPHOTO2_ERROR(error)
  }
};
VOID_MEMBER_FUNCTION(_GPContext,
    set_idle_func, (GPContextIdleFunc func, void *data),
    gp_context_set_idle_func, ($self, func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_error_func, (GPContextErrorFunc func, void *data),
    gp_context_set_error_func, ($self, func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_message_func, (GPContextMessageFunc func, void *data),
    gp_context_set_message_func, ($self, func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_question_func, (GPContextQuestionFunc func, void *data),
    gp_context_set_question_func, ($self, func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_cancel_func, (GPContextCancelFunc func, void *data),
    gp_context_set_cancel_func, ($self, func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_progress_funcs, (GPContextProgressStartFunc start_func,
                         GPContextProgressUpdateFunc update_func,
                         GPContextProgressStopFunc stop_func,
                         void *data),
    gp_context_set_progress_funcs, ($self, start_func, update_func, stop_func, data))
VOID_MEMBER_FUNCTION(_GPContext,
    set_status_func, (GPContextStatusFunc func, void *data),
    gp_context_set_status_func, ($self, func, data))

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-context.h"
