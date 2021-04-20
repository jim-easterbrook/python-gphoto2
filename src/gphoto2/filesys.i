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

%module(package="gphoto2") filesys

%include "common/preamble.i"

// gp_camera_file_get_info() etc. return a pointer in an output parameter
CALLOC_ARGOUT(CameraFileInfo *info)

// Make docstring parameter types more Pythonic
%typemap(doc) CameraFileInfo "$1_name: gphoto2.$1_type"
%typemap(doc) CameraFilesystem * "$1_name: gphoto2.$*1_type"

#ifndef SWIGIMPORTED

// Turn on default exception handling
DEFAULT_EXCEPTION

// image dimensions use uint32_t and storage info uses uint64_t
%include "stdint.i"

// Many functions accept NULL context value
DEFAULT_CONTEXT

// gp_filesystem_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFilesystem **)

// gp_filesystem_list_files() etc. return a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// Ignore some functions
%ignore gp_filesystem_get_storageinfo;
%ignore gp_filesystem_free;

// Structures are read only
%immutable;

// Add default constructor and destructor to _CameraFilesystem
struct _CameraFilesystem {};
DEFAULT_CTOR(_CameraFilesystem, gp_filesystem_new)
DEFAULT_DTOR(_CameraFilesystem, gp_filesystem_free)

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-filesys.h"
