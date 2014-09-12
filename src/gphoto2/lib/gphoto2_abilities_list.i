// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2.lib") gphoto2_abilities_list

%{
#include "gphoto2/gphoto2.h"
%}

%import "gphoto2_context.i"
%import "gphoto2_list.i"
%import "gphoto2_port_info_list.i"
%import "gphoto2_port_log.i"

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

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
%ignore _CameraAbilitiesList;

// Make CameraAbilitiesList more like a Python list
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_length", functype="lenfunc")
    _CameraAbilitiesList::__len__;
%feature("python:slot", "sq_item",   functype="ssizeargfunc")
    _CameraAbilitiesList::__getitem__;
#endif // SWIGPYTHON_BUILTIN

%exception __getitem__ {
  $action
  if (PyErr_Occurred() != NULL) {
    goto fail;
  }
}
%{
int (*_CameraAbilitiesList___len__)(CameraAbilitiesList *) = gp_abilities_list_count;
%}
%extend _CameraAbilitiesList {
  int __len__();
  void __getitem__(int idx, CameraAbilities *abilities) {
    if (idx < 0 || idx >= gp_abilities_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "CameraAbilitiesList index out of range");
      return;
    }
    int error = gp_abilities_list_get_abilities($self, idx, abilities);
    if (error < GP_OK) {
      GPHOTO2_ERROR(error)
      return;
    }
  }
};

// Structures are read only
%immutable;

%include "gphoto2/gphoto2-abilities-list.h"
