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
