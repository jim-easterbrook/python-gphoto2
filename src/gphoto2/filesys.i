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

%module(package="gphoto2") filesys

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

%import "context.i"
%import "file.i"
%import "list.i"

%include "typemaps.i"

// image dimensions use uint32_t and storage info uses uint64_t
%include "stdint.i"

IMPORT_GPHOTO2_ERROR()

// Make docstring parameter types more Pythonic
%typemap(doc) CameraFilesystem * "$1_name: $*1_type"

// gp_filesystem_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFilesystem **)

// gp_filesystem_list_files() etc. return a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// gp_camera_file_get_info() etc. return a pointer in an output parameter
CALLOC_ARGOUT(CameraFileInfo *info)

// Add default constructor and destructor to _CameraFilesystem
struct _CameraFilesystem {};
DEFAULT_CTOR(_CameraFilesystem, CameraFilesystem, gp_filesystem_new)
DEFAULT_DTOR(_CameraFilesystem, gp_filesystem_free)
%ignore _CameraFilesystem;
%ignore gp_filesystem_free;

// Some things are defined in .h files but are not in the library
%ignore gp_filesystem_get_storageinfo;

// Structures are read only
%immutable;

%include "gphoto2/gphoto2-filesys.h"
