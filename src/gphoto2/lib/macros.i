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

