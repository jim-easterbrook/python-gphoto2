// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-17  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

%import "list.i"

IMPORT_GPHOTO2_ERROR()

%rename(Context) _GPContext;

// Make docstring parameter types more Pythonic
%typemap(doc) GPContext * "$1_name: Context";

// gp_camera_autodetect() returns a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// Mark gp_context_new as constructor
%newobject gp_context_new;

// Mark gp_context_unref as destructor
%delobject gp_context_unref;

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
%ignore gp_context_ref;
%ignore gp_context_unref;

#if GPHOTO2_VERSION >= 0x020500
// Add member methods to _GPContext
MEMBER_FUNCTION(_GPContext, Context,
    camera_autodetect, (CameraList *list),
    gp_camera_autodetect, (list, $self))
#endif

%include "gphoto2/gphoto2-context.h"
