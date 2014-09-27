%define IMPORT_GPHOTO2_ERROR()
%{
PyObject *PyExc_GPhoto2Error = NULL;
%}
%init %{
{
  PyObject *mod_dict = PyImport_GetModuleDict();
  PyObject *module = PyDict_GetItemString(mod_dict, "gphoto2");
  if (module != NULL)
    PyExc_GPhoto2Error = PyObject_GetAttrString(module, "GPhoto2Error");
  if (PyExc_GPhoto2Error == NULL)
#if PY_VERSION_HEX >= 0x03000000
    return NULL;
#else
    return;
#endif
}
%}
%enddef

%define GPHOTO2_ERROR(error)
PyErr_SetObject(PyExc_GPhoto2Error, PyInt_FromLong(error));
%enddef

%define STRING_ARGOUT()
%typemap(in, numinputs=0) char ** (char *temp) {
  temp = NULL;
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
  temp = NULL;
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

// Macros to add member functions to structs
%define MEMBER_FUNCTION(type, py_type, member, member_args, function, function_args)
%exception type::member {
  $action
  if (PyErr_Occurred() != NULL) SWIG_fail;
}
%extend type {
%feature("docstring") "See also: gphoto2." #function
  void member member_args {
    int error = function function_args;
    if (error < GP_OK) GPHOTO2_ERROR(error)
  }
};
%feature("docstring") function "See also: gphoto2." #py_type "." #member
%enddef

%define INT_MEMBER_FUNCTION(type, py_type, member, member_args, function, function_args)
%{
int (*type ## _ ## member)() = function;
%}
%exception type::member {
  $action
  if (result < GP_OK) {
    GPHOTO2_ERROR(result)
    goto fail;
  }
}
%extend type {
%feature("docstring") "See also: gphoto2." #function
  int member member_args;
};
%feature("docstring") function "See also: gphoto2." #py_type "." #member
%enddef

%define PYOBJECT_MEMBER_FUNCTION(type, member, member_args)
%extend type {
  PyObject *member member_args;
};
%enddef

%define LEN_MEMBER_FUNCTION(type, py_type, function)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc") type::__len__;
#endif
INT_MEMBER_FUNCTION(type, py_type, __len__, (), function, ())
%enddef
