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

%module(package="gphoto2") gphoto2_file
#pragma SWIG nowarn=321

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

%rename(CameraFile) _CameraFile;

// gp_file_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFile **)

// gp_file_get_data_and_size() returns a pointer to some data
%typemap(in, numinputs=0) const char ** data (char *temp) {
  $1 = &temp;
}
%typemap(in, numinputs=0) unsigned long int * size (unsigned long temp) {
  $1 = &temp;
}
%typemap(argout) (const char ** data, unsigned long * size) {
  // Make a copy of the data - persists after CameraFile object is destroyed
%#if PY_VERSION_HEX >= 0x03000000
  PyObject* array = PyBytes_FromStringAndSize(*$1, *$2);
%#else
  PyObject* array = PyString_FromStringAndSize(*$1, *$2);
%#endif
  if (array) {
    $result = SWIG_Python_AppendOutput($result, array);
  }
  else {
    Py_INCREF(Py_None);
    $result = SWIG_Python_AppendOutput($result, Py_None);
  }
}

// Add default constructor and destructor to _CameraFile
struct _CameraFile {};
DEFAULT_CTOR(_CameraFile, gp_file_new)
DEFAULT_DTOR(_CameraFile, gp_file_unref)
%ignore _CameraFile;

// Add member methods to _CameraFile
MEMBER_FUNCTION(_CameraFile, CameraFile,
    set_name, (const char *name),
    gp_file_set_name, ($self, name))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    get_name, (const char **name),
    gp_file_get_name, ($self, name))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    set_mime_type, (const char *mime_type),
    gp_file_set_mime_type, ($self, mime_type))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    get_mime_type, (const char **mime_type),
    gp_file_get_mime_type, ($self, mime_type))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    set_mtime, (time_t mtime),
    gp_file_set_mtime, ($self, mtime))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    get_mtime, (time_t *mtime),
    gp_file_get_mtime, ($self, mtime))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    detect_mime_type, (),
    gp_file_detect_mime_type, ($self))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    adjust_name_for_mime_type, (),
    gp_file_adjust_name_for_mime_type, ($self))
#ifndef GPHOTO2_24
MEMBER_FUNCTION(_CameraFile, CameraFile,
    get_name_by_type, (const char *basename, CameraFileType type, char **newname),
    gp_file_get_name_by_type, ($self, basename, type, newname))
#endif
MEMBER_FUNCTION(_CameraFile, CameraFile,
    set_data_and_size, (char *data, unsigned long int size),
    gp_file_set_data_and_size, ($self, data, size))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    get_data_and_size, (const char **data, unsigned long int *size),
    gp_file_get_data_and_size, ($self, data, size))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    open, (const char *filename),
    gp_file_open, ($self, filename))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    save, (const char *filename),
    gp_file_save, ($self, filename))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    clean, (),
    gp_file_clean, ($self))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    copy, (CameraFile *source),
    gp_file_copy, ($self, source))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    append, (const char *data, unsigned long int size),
    gp_file_append, ($self, data, size))
MEMBER_FUNCTION(_CameraFile, CameraFile,
    slurp, (char *data, size_t size, size_t *readlen),
    gp_file_slurp, ($self, data, size, readlen))

// These structures are private
%ignore _CameraFileHandler;

%include "gphoto2/gphoto2-file.h"
