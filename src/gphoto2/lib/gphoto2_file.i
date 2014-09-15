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

%module(package="gphoto2.lib") gphoto2_file

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

// gp_file_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFile **)

// Add default constructor and destructor to _CameraFile
struct _CameraFile {};
DEFAULT_CTOR(_CameraFile, gp_file_new)
DEFAULT_DTOR(_CameraFile, gp_file_unref)
%ignore _CameraFile;

// Add member methods to _CameraFile
MEMBER_FUNCTION(_CameraFile,
    set_name, (const char *name),
    gp_file_set_name, ($self, name))
MEMBER_FUNCTION(_CameraFile,
    get_name, (const char **name),
    gp_file_get_name, ($self, name))
MEMBER_FUNCTION(_CameraFile,
    set_mime_type, (const char *mime_type),
    gp_file_set_mime_type, ($self, mime_type))
MEMBER_FUNCTION(_CameraFile,
    get_mime_type, (const char **mime_type),
    gp_file_get_mime_type, ($self, mime_type))
MEMBER_FUNCTION(_CameraFile,
    set_mtime, (time_t mtime),
    gp_file_set_mtime, ($self, mtime))
MEMBER_FUNCTION(_CameraFile,
    get_mtime, (time_t *mtime),
    gp_file_get_mtime, ($self, mtime))
MEMBER_FUNCTION(_CameraFile,
    detect_mime_type, (),
    gp_file_detect_mime_type, ($self))
MEMBER_FUNCTION(_CameraFile,
    adjust_name_for_mime_type, (),
    gp_file_adjust_name_for_mime_type, ($self))
MEMBER_FUNCTION(_CameraFile,
    get_name_by_type, (const char *basename, CameraFileType type, char **newname),
    gp_file_get_name_by_type, ($self, basename, type, newname))
MEMBER_FUNCTION(_CameraFile,
    set_data_and_size, (char *data, unsigned long int size),
    gp_file_set_data_and_size, ($self, data, size))
MEMBER_FUNCTION(_CameraFile,
    get_data_and_size, (const char **data, unsigned long int *size),
    gp_file_get_data_and_size, ($self, data, size))
MEMBER_FUNCTION(_CameraFile,
    open, (const char *filename),
    gp_file_open, ($self, filename))
MEMBER_FUNCTION(_CameraFile,
    save, (const char *filename),
    gp_file_save, ($self, filename))
MEMBER_FUNCTION(_CameraFile,
    clean, (),
    gp_file_clean, ($self))
MEMBER_FUNCTION(_CameraFile,
    copy, (CameraFile *source),
    gp_file_copy, ($self, source))
MEMBER_FUNCTION(_CameraFile,
    append, (const char *data, unsigned long int size),
    gp_file_append, ($self, data, size))
MEMBER_FUNCTION(_CameraFile,
    slurp, (char *data, size_t size, size_t *readlen),
    gp_file_slurp, ($self, data, size, readlen))

// These structures are private
%ignore _CameraFileHandler;

%include "gphoto2/gphoto2-file.h"
