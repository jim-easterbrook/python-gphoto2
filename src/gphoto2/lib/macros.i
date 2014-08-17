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
