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

%module(package="gphoto2") abilities_list

%include "common/preamble.i"

%rename(CameraAbilitiesList) _CameraAbilitiesList;

// Make docstring parameter types more Pythonic
%typemap(doc) CameraAbilities "$1_name: gphoto2.$1_type"
%typemap(doc) CameraAbilitiesList * "$1_name: gphoto2.$*1_type"

#ifndef SWIGIMPORTED

// Turn on default exception handling
DEFAULT_EXCEPTION

// Many functions accept NULL context value
DEFAULT_CONTEXT

// gp_abilities_list_get_abilities() returns a pointer in an output parameter
CALLOC_ARGOUT(CameraAbilities *abilities)

// gp_abilities_list_detect() returns a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// gp_abilities_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraAbilitiesList **)

// Add default constructor and destructor to _CameraAbilitiesList
struct _CameraAbilitiesList {};
DEFAULT_CTOR(_CameraAbilitiesList, gp_abilities_list_new)
DEFAULT_DTOR(_CameraAbilitiesList, gp_abilities_list_free)
%ignore gp_abilities_list_free;

// Make CameraAbilitiesList more like a Python list
LEN_MEMBER_FUNCTION(_CameraAbilitiesList, gp_abilities_list_count)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_item",   functype="ssizeargfunc")
    _CameraAbilitiesList::__getitem__;
#endif
%exception __getitem__ {
  $action
  if (PyErr_Occurred() != NULL) goto fail;
}
%extend _CameraAbilitiesList {
  void __getitem__(int idx, CameraAbilities *abilities) {
    if (idx < 0 || idx >= gp_abilities_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "CameraAbilitiesList index out of range");
      return;
    }
    {
      int error = gp_abilities_list_get_abilities($self, idx, abilities);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return;
      }
    }
  }
};

// Convert array of serial port speeds to Python list
%typemap(out) int speed [64] {
  int *value = $1;
  $result = PyList_New(0);
  while (*value) {
    PyObject* temp = PyInt_FromLong(*value);
    PyList_Append($result, temp);
    Py_DECREF(temp);
    value++;
  }
}

// Add member methods to _CameraAbilitiesList
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, load, (GPContext *context),
    gp_abilities_list_load, ($self, context), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, load_dir, (const char *dir, GPContext *context),
    gp_abilities_list_load_dir, ($self, dir, context), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, reset, (),
    gp_abilities_list_reset, ($self), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, detect, (GPPortInfoList *info_list, CameraList *l, GPContext *context),
    gp_abilities_list_detect, ($self, info_list, l, context), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, append, (CameraAbilities abilities),
    gp_abilities_list_append, ($self, abilities), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    int, count, (),
    gp_abilities_list_count, ($self), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    int, lookup_model, (const char *model),
    gp_abilities_list_lookup_model, ($self, model), )
MEMBER_FUNCTION(_CameraAbilitiesList,
    void, get_abilities, (int index, CameraAbilities *abilities),
    gp_abilities_list_get_abilities, ($self, index, abilities), )

// Structures are read only
%immutable;

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-abilities-list.h"
