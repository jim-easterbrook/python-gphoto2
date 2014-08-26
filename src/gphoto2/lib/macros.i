%define RESULT_APPEND(value)
  {
    if (!PyList_Check($result)) {
      PyObject* temp = $result;
      $result = PyList_New(1);
      PyList_SetItem($result, 0, temp);
    }
    PyObject* temp = value;
    PyList_Append($result, temp);
    Py_DECREF(temp);
  }
%enddef

%define STRING_ARGOUT()
%typemap(in, numinputs=0) char ** (char *temp) {
  $1 = &temp;
}
%typemap(argout) char ** {
  if (*$1) {
    RESULT_APPEND(PyString_FromString(*$1))
  }
  else {
    Py_INCREF(Py_None);
    RESULT_APPEND(Py_None)
  }
}
%enddef

%define DECLARE_GP_ERROR()
%ignore _gp_error;
%inline %{
static int _gp_error = GP_OK;
%}
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
