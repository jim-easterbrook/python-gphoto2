// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This file is part of python-gphoto2.
//
// python-gphoto2 is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// python-gphoto2 is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with python-gphoto2.  If not, see <https://www.gnu.org/licenses/>.

%module(package="gphoto2", threads="1") file
%nothread;
#pragma SWIG nowarn=321

%include "common/preamble.i"

%rename(CameraFile) _CameraFile;

// gp_file_get_mtime() returns a pointer in output params
typedef long int time_t;
%apply time_t *OUTPUT { time_t * };
%typemap(doc) time_t "$1_name: int"

// Make docstring parameter types more Pythonic
%typemap(doc) CameraFile * "$1_name: gphoto2.$*1_type"
%typemap(doc) CameraFileHandler * "$1_name: gphoto2.$*1_type"
%typemap(doc) enum CameraFileType "$1_name: $1_type (gphoto2.GP_FILE_TYPE_PREVIEW etc.)"

// Allow other Python threads to continue during some function calls
%thread gp_file_copy;
%thread gp_file_get_data_and_size;
%thread gp_file_save;
%thread gp_file_set_data_and_size;

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_file_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFile **)

// gp_file_get_data_and_size() returns a pointer to some data
%typemap(in, numinputs=0) (const char **data, unsigned long int *size)
                          (char *temp_data = NULL,
                           unsigned long temp_size = 0) %{
  $1 = &temp_data;
  $2 = &temp_size;
%}
%typemap(argout) (const char **data, unsigned long int *size) %{
  $result = SWIG_Python_AppendOutput(
    $result, PyMemoryView_FromMemory(*$1, *$2, PyBUF_READ));
%}

// gp_file_set_data_and_size() requires data allocated by malloc which it will free later
%typemap(in, numinputs=1) (char * data, unsigned long int size) {
  Py_buffer view;
  if (PyObject_CheckBuffer($input) != 1) {
    PyErr_SetString(
      PyExc_TypeError,
      "in method '$symname', argument $argnum does not support the buffer interface");
    SWIG_fail;
  }
  if (PyObject_GetBuffer($input, &view, PyBUF_SIMPLE) != 0) {
    PyErr_SetString(
      PyExc_TypeError,
      "in method '$symname', argument $argnum does not export a simple buffer");
    SWIG_fail;
  }
  $1 = malloc(view.len);
  if (!$1) {
    PyErr_SetString(
      PyExc_MemoryError, "in method '$symname', insufficient memory");
    SWIG_fail;
  }
  memcpy($1, view.buf, view.len);
  $2 = view.len;
  PyBuffer_Release(&view);
}
%exception gp_file_set_data_and_size %{
  $action
  if (result < GP_OK) free(arg2);
%}
%exception _CameraFile::set_data_and_size {
  $action
  if (PyErr_Occurred()) {
    free(arg2);
    SWIG_fail;
  }
}
%typemap(doc) char * data, unsigned long int size "$1_name: readable buffer (e.g. bytes)"

// Add default constructor and destructor to _CameraFile
struct _CameraFile {};
DEFAULT_CTOR(_CameraFile, gp_file_new)
DEFAULT_DTOR(_CameraFile, gp_file_unref)

// Add constructor from file descriptor
%extend _CameraFile {
  _CameraFile(int fd) {
    struct _CameraFile *result;
    int error = gp_file_new_from_fd(&result, fd);
    if (error < GP_OK)
      GPHOTO2_ERROR(error)
    return result;
  }
};

// Add member methods to _CameraFile
MEMBER_FUNCTION(_CameraFile,
    void, set_name, (const char *name),
    gp_file_set_name, ($self, name), )
MEMBER_FUNCTION(_CameraFile,
    void, get_name, (const char **name),
    gp_file_get_name, ($self, name), )
MEMBER_FUNCTION(_CameraFile,
    void, set_mime_type, (const char *mime_type),
    gp_file_set_mime_type, ($self, mime_type), )
MEMBER_FUNCTION(_CameraFile,
    void, get_mime_type, (const char **mime_type),
    gp_file_get_mime_type, ($self, mime_type), )
MEMBER_FUNCTION(_CameraFile,
    void, set_mtime, (time_t mtime),
    gp_file_set_mtime, ($self, mtime), )
MEMBER_FUNCTION(_CameraFile,
    void, get_mtime, (time_t *mtime),
    gp_file_get_mtime, ($self, mtime), )
MEMBER_FUNCTION(_CameraFile,
    void, detect_mime_type, (),
    gp_file_detect_mime_type, ($self), )
MEMBER_FUNCTION(_CameraFile,
    void, adjust_name_for_mime_type, (),
    gp_file_adjust_name_for_mime_type, ($self), )
MEMBER_FUNCTION(_CameraFile,
    void, get_name_by_type, (const char *basename, CameraFileType type, char **newname),
    gp_file_get_name_by_type, ($self, basename, type, newname), )
MEMBER_FUNCTION(_CameraFile,
    void, set_data_and_size, (char *data, unsigned long int size),
    gp_file_set_data_and_size, ($self, data, size), 1)
MEMBER_FUNCTION(_CameraFile,
    void, get_data_and_size, (const char **data, unsigned long int *size),
    gp_file_get_data_and_size, ($self, data, size), 1)
MEMBER_FUNCTION(_CameraFile,
    void, save, (const char *filename),
    gp_file_save, ($self, filename), 1)
MEMBER_FUNCTION(_CameraFile,
    void, clean, (),
    gp_file_clean, ($self), )
MEMBER_FUNCTION(_CameraFile,
    void, copy, (CameraFile *source),
    gp_file_copy, ($self, source), 1)
MEMBER_FUNCTION(_CameraFile,
    void, open, (const char *filename),
    gp_file_open, ($self, filename), 1)

// These structures are private
%ignore _CameraFileHandler;

// These functions are internal
%ignore gp_file_append;
%ignore gp_file_slurp;
%ignore gp_file_free;
%ignore gp_file_ref;
%ignore gp_file_unref;
%ignore gp_file_new_from_handler;

// Turn off default exception handling
%noexception;

%include "gphoto2/gphoto2-file.h"
