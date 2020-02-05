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

%module(package="gphoto2") context

%include "common/preamble.i"

%rename(Context) _GPContext;

#ifndef SWIGIMPORTED

// Make docstring parameter types more Pythonic
%typemap(doc) GPContext * "$1_name: gphoto2.$*1_type";

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

// Struct to store callback details
%ignore CallbackDetails::context;
%ignore CallbackDetails::func;
%ignore CallbackDetails::data;
%ignore CallbackDetails::remove;
%ignore del_CallbackDetails;
%inline %{
typedef void (*RemoveFunc) (GPContext *context, void *func, void *data);
typedef struct CallbackDetails {
    GPContext   *context;
    PyObject    *func;
    PyObject    *data;
    RemoveFunc  remove;
} CallbackDetails;

// Add destructor
static int del_CallbackDetails(struct CallbackDetails *this) {
    if (this->context)
        this->remove(this->context, NULL, NULL);
    Py_XDECREF(this->func);
    Py_XDECREF(this->data);
    free(this);
    return GP_OK;
};
%}
DEFAULT_DTOR(CallbackDetails, del_CallbackDetails);

// Macro for the six single callback function variants
%define SINGLE_CALLBACK_FUNCTION(cb_func_type, install_func, cb_wrapper)

// Define typemaps
%typemap(arginit) cb_func_type (CallbackDetails *_global_callbacks) {
    _global_callbacks = malloc(sizeof(CallbackDetails));
    if (!_global_callbacks) {
        PyErr_SetNone(PyExc_MemoryError);
        SWIG_fail;
    }
    _global_callbacks->context = NULL;
    _global_callbacks->func = NULL;
    _global_callbacks->data = NULL;
    _global_callbacks->remove = (RemoveFunc) install_func;
}
%typemap(freearg) cb_func_type {
    if (_global_callbacks)
        del_CallbackDetails(_global_callbacks);
}
%typemap(in) cb_func_type {
    if (!PyCallable_Check($input)) {
        SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
    }
    _global_callbacks->func = $input;
    Py_INCREF(_global_callbacks->func);
    $1 = (cb_func_type) cb_wrapper;
}
%typemap(argout) cb_func_type {
    $result = SWIG_Python_AppendOutput($result,
        SWIG_NewPointerObj(_global_callbacks, SWIGTYPE_p_CallbackDetails, SWIG_POINTER_OWN));
    _global_callbacks = NULL;
}
%typemap(doc) cb_func_type "$1_name: callable function"
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
%ignore ProgressCallbacks::context;
%ignore ProgressCallbacks::func_1;
%ignore ProgressCallbacks::func_2;
%ignore ProgressCallbacks::func_3;
%ignore ProgressCallbacks::data;
%ignore del_ProgressCallbacks;

%inline %{
typedef struct ProgressCallbacks {
    GPContext   *context;
    PyObject    *func_1;
    PyObject    *func_2;
    PyObject    *func_3;
    PyObject    *data;
} ProgressCallbacks;

static int del_ProgressCallbacks(struct ProgressCallbacks *this) {
    if (this->context)
        gp_context_set_progress_funcs(this->context, NULL, NULL, NULL, NULL);
    Py_XDECREF(this->func_1);
    Py_XDECREF(this->func_2);
    Py_XDECREF(this->func_3);
    Py_XDECREF(this->data);
    free(this);
    return GP_OK;
};
%}
DEFAULT_DTOR(ProgressCallbacks, del_ProgressCallbacks);

// Macros for wrappers around Python callbacks
%define CB_PREAMBLE
%{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *result = NULL;
    PyObject *arglist = NULL;
    PyObject *function = NULL;
    PyObject *self = NULL;
    PyObject *py_context = SWIG_NewPointerObj(SWIG_as_voidptr(context), SWIGTYPE_p__GPContext, 0);
%}
%enddef

%define CB_CALLFUNC
%{
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
%enddef

%define CB_POSTAMBLE
%{
    Py_DECREF(result);
fail:
    PyGILState_Release(gstate);
%}
%enddef

%{
// Call Python callbacks from C callbacks
static void wrap_idle_func(GPContext *context, void *data) {
    CallbackDetails *this = data;
%}
CB_PREAMBLE
%{
    function = this->func;
    arglist = Py_BuildValue("(OO)", py_context, this->data);
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

static void wrap_error_func(GPContext *context, const char *text, void *data) {
    CallbackDetails *this = data;
%}
CB_PREAMBLE
%{
    function = this->func;
#if PY_VERSION_HEX >= 0x03000000
    arglist = Py_BuildValue("(OyO)", py_context, text, this->data);
#else
    arglist = Py_BuildValue("(OsO)", py_context, text, this->data);
#endif
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

static void wrap_status_func(GPContext *context, const char *text, void *data) {
    CallbackDetails *this = data;
%}
CB_PREAMBLE
%{
    function = this->func;
#if PY_VERSION_HEX >= 0x03000000
    arglist = Py_BuildValue("(OyO)", py_context, text, this->data);
#else
    arglist = Py_BuildValue("(OsO)", py_context, text, this->data);
#endif
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

static void wrap_message_func(GPContext *context, const char *text, void *data) {
    CallbackDetails *this = data;
%}
CB_PREAMBLE
%{
    function = this->func;
#if PY_VERSION_HEX >= 0x03000000
    arglist = Py_BuildValue("(OyO)", py_context, text, this->data);
#else
    arglist = Py_BuildValue("(OsO)", py_context, text, this->data);
#endif
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

static GPContextFeedback wrap_question_func(GPContext *context, const char *text, void *data) {
    CallbackDetails *this = data;
    GPContextFeedback c_result = GP_CONTEXT_FEEDBACK_OK;
%}
CB_PREAMBLE
%{
    function = this->func;
#if PY_VERSION_HEX >= 0x03000000
    arglist = Py_BuildValue("(OyO)", py_context, text, this->data);
#else
    arglist = Py_BuildValue("(OsO)", py_context, text, this->data);
#endif
%}
CB_CALLFUNC
%{
    c_result = PyInt_AsLong(result);
%}
CB_POSTAMBLE
%{
    return c_result;
};

static GPContextFeedback wrap_cancel_func(GPContext *context, void *data) {
    CallbackDetails *this = data;
    GPContextFeedback c_result = GP_CONTEXT_FEEDBACK_OK;
%}
CB_PREAMBLE
%{
    function = this->func;
    arglist = Py_BuildValue("(OO)", py_context, this->data);
%}
CB_CALLFUNC
%{
    c_result = PyInt_AsLong(result);
%}
CB_POSTAMBLE
%{
    return c_result;
};

static int py_progress_start(GPContext *context, float target, const char *text, void *data) {
    ProgressCallbacks *this = data;
    int c_result = 0;
%}
CB_PREAMBLE
%{
    function = this->func_1;
#if PY_VERSION_HEX >= 0x03000000
    arglist = Py_BuildValue("(OfyO)", py_context, target, text, this->data);
#else
    arglist = Py_BuildValue("(OfsO)", py_context, target, text, this->data);
#endif
%}
CB_CALLFUNC
%{
    c_result = PyInt_AsLong(result);
    if ((c_result == -1) && PyErr_Occurred()) {
        PyErr_Print();
    }
%}
CB_POSTAMBLE
%{
    return c_result;
};

static void py_progress_update(GPContext *context, unsigned int id, float current, void *data) {
    ProgressCallbacks *this = data;
%}
CB_PREAMBLE
%{
    function = this->func_2;
    arglist = Py_BuildValue("(OifO)", py_context, id, current, this->data);
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

static void py_progress_stop(GPContext *context, unsigned int id, void *data) {
    ProgressCallbacks *this = data;
%}
CB_PREAMBLE
%{
    function = this->func_3;
    arglist = Py_BuildValue("(OiO)", py_context, id, this->data);
%}
CB_CALLFUNC
CB_POSTAMBLE
%{
};

%}

// Use typemaps to install callbacks
%typemap(arginit) GPContextProgressStartFunc (ProgressCallbacks *_global_callbacks) {
    _global_callbacks = malloc(sizeof(ProgressCallbacks));
    if (!_global_callbacks) {
        PyErr_SetNone(PyExc_MemoryError);
        SWIG_fail;
    }
    _global_callbacks->context = NULL;
    _global_callbacks->func_1 = NULL;
    _global_callbacks->func_2 = NULL;
    _global_callbacks->func_3 = NULL;
    _global_callbacks->data = NULL;
}
%typemap(freearg) GPContextProgressStartFunc {
    if (_global_callbacks)
        del_ProgressCallbacks(_global_callbacks);
}

%typemap(in) void *data {
    _global_callbacks->data = $input;
    Py_INCREF(_global_callbacks->data);
    $1 = _global_callbacks;
}
%typemap(doc) void *data "$1_name: object"

%typemap(check) GPContext *context {
    _global_callbacks->context = $1;
}

%typemap(in) GPContextProgressStartFunc {
    if (!PyCallable_Check($input)) {
        SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
    }
    _global_callbacks->func_1 = $input;
    Py_INCREF(_global_callbacks->func_1);
    $1 = (GPContextProgressStartFunc) py_progress_start;
}
%typemap(doc) GPContextProgressStartFunc "$1_name: callable function"

%typemap(in) GPContextProgressUpdateFunc {
    if (!PyCallable_Check($input)) {
        SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
    }
    _global_callbacks->func_2 = $input;
    Py_INCREF(_global_callbacks->func_2);
    $1 = (GPContextProgressUpdateFunc) py_progress_update;
}
%typemap(doc) GPContextProgressUpdateFunc "$1_name: callable function"

%typemap(in) GPContextProgressStopFunc {
    if (!PyCallable_Check($input)) {
        SWIG_exception_fail(SWIG_TypeError, "in method '" "$symname" "', argument " "$argnum" " is not callable");
    }
    _global_callbacks->func_3 = $input;
    Py_INCREF(_global_callbacks->func_3);
    $1 = (GPContextProgressStopFunc) py_progress_stop;
}
%typemap(doc) GPContextProgressStopFunc "$1_name: callable function"

%typemap(argout) GPContextProgressStartFunc {
    $result = SWIG_Python_AppendOutput($result,
        SWIG_NewPointerObj(_global_callbacks, SWIGTYPE_p_ProgressCallbacks, SWIG_POINTER_OWN));
    _global_callbacks = NULL;
}

// Add member methods to _GPContext
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

// Add default constructor and destructor
struct _GPContext {};
%extend _GPContext {
  _GPContext() {
    return gp_context_new();
  }
  ~_GPContext() {
    gp_context_unref($self);
  }
};
%ignore _GPContext;
%newobject gp_context_new;
%delobject gp_context_unref;

%include "gphoto2/gphoto2-context.h"
