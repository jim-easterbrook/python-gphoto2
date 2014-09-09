%define STRING_ARGOUT()
%typemap(in, numinputs=0) char ** (char *temp) {
  $1 = &temp;
}
%typemap(argout) char ** {
  if (*$1) {
    $result = SWIG_Python_AppendOutput($result, PyString_FromString(*$1));
  }
  else {
    Py_INCREF(Py_None);
    $result = SWIG_Python_AppendOutput($result, Py_None);
  }
}
%enddef

%define PLAIN_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern ($*1_type temp) {
  $1 = &temp;
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $*1_descriptor, SWIG_POINTER_OWN));
}
%enddef

%define CALLOC_ARGOUT(typepattern)
%typemap(in, numinputs=0) typepattern () {
  $1 = ($1_type)calloc(1, sizeof($*1_type));
  if ($1 == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Cannot allocate " "$*1_type");
    goto fail;
  }
}
%typemap(freearg) typepattern {
  free($1);
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define NEW_ARGOUT(typepattern, alloc_func, free_func)
%typemap(in, numinputs=0) typepattern () {
  $1 = NULL;
  int error = alloc_func(&$1);
  if (error != GP_OK) {
    PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
    goto fail;
  }
}
%typemap(freearg) typepattern {
  if ($1 != NULL) {
    int error = free_func($1);
    if (error != GP_OK) {
      PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(error));
    }
  }
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define DECLARE_GP_ERROR()
%ignore _gp_error;
%inline %{
static int _gp_error = GP_OK;
%}
%enddef

%define DEFAULT_CTOR(name, alloc_func)
%exception name {
  $action
  if (_gp_error != GP_OK) {
    PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(_gp_error));
    _gp_error = GP_OK;
    result = NULL;
  }
}
%extend name {
  name() {
    struct name *result;
    _gp_error = alloc_func(&result);
    return result;
  }
};
%enddef

%define COPY_CTOR(name, ref_func)
%extend name {
  name(struct name *other) {
    struct name *result = other;
    _gp_error = ref_func(other);
    return result;
  }
};
%enddef

%define DEFAULT_DTOR(name, free_func)
%delobject free_func;
%exception ~name {
  $action
  if (_gp_error != GP_OK) {
    PyErr_SetString(PyExc_RuntimeError, gp_result_as_string(_gp_error));
    _gp_error = GP_OK;
    return NULL;
  }
}
%extend name {
  ~name() {
    _gp_error = free_func($self);
  }
};
%enddef
