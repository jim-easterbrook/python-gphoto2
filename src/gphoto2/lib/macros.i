%define IMPORT_GPHOTO2_ERROR()
%{
PyObject *PyExc_GPhoto2Error = NULL;
%}
%init %{
{
  PyObject *module = PyImport_ImportModuleLevel("", PyEval_GetGlobals(), NULL, NULL, 2);
  if (module != NULL)
    PyExc_GPhoto2Error = PyObject_GetAttrString(module, "GPhoto2Error");
  if (PyExc_GPhoto2Error == NULL)
    return;
}
%}
%enddef

%define GPHOTO2_ERROR(error)
PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
%enddef

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
    SWIG_fail;
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
  if (error < GP_OK) {
    GPHOTO2_ERROR(error)
    SWIG_fail;
  }
}
%typemap(freearg) typepattern {
  if ($1 != NULL) {
    int error = free_func($1);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
    }
  }
}
%typemap(argout) typepattern {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj($1, $1_descriptor, SWIG_POINTER_OWN));
  $1 = NULL;
}
%enddef

%define DEFAULT_CTOR(name, alloc_func)
%exception name {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend name {
  name() {
    struct name *result;
    int error = alloc_func(&result);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
    return result;
  }
};
%enddef

%define COPY_CTOR(name, ref_func)
%extend name {
  name(struct name *other) {
    struct name *result = other;
    int error = ref_func(other);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
    return result;
  }
};
%enddef

%define DEFAULT_DTOR(name, free_func)
%delobject free_func;
%exception ~name {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend name {
  ~name() {
    int error = free_func($self);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
  }
};
%enddef
