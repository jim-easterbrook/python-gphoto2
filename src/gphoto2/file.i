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

#ifndef SWIGIMPORTED

// Allow other Python threads to continue during some function calls
%thread gp_file_append;
%thread gp_file_copy;
%thread gp_file_get_data_and_size;
%thread gp_file_save;
%thread gp_file_set_data_and_size;

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_file_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFile **)

// make gp_file_open() create a new CameraFile
NEW_ARGOUT(CameraFile *camera_file, gp_file_new, gp_file_unref)
// Redefine signature as many other functions also use *file
%noexception gp_file_open;
int gp_file_open(CameraFile *camera_file, const char *filename);
%ignore gp_file_open;

// Define a simple Python type that has the buffer interface
// This definition is not SWIGGED, just compiled
%{
typedef struct {
    PyObject_HEAD
    CameraFile  *file;
    void        *buf;
    Py_ssize_t  len;
} FileData;

static void
FileData_dealloc(FileData* self)
{
    if (self->file)
        gp_file_unref(self->file);
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static int
FileData_getbuffer(FileData *self, Py_buffer *view, int flags)
{
    return PyBuffer_FillInfo(view, (PyObject*)self, self->buf, self->len, 1, flags);
}

static void
FileData_set(FileData *self, CameraFile *file, void *buf, Py_ssize_t len)
{
    if (self->file)
        gp_file_unref(self->file);
    self->file = file;
    self->buf = buf;
    self->len = len;
    if (self->file)
        gp_file_ref(self->file);
}

static PyBufferProcs FileData_BufferProcs = {
    (getbufferproc)FileData_getbuffer,        /* bf_getbuffer */
    (releasebufferproc) 0,                    /* bf_releasebuffer */
};

static PyTypeObject FileDataType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "gphoto2.FileData",                       /*tp_name*/
    sizeof(FileData),                         /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)FileData_dealloc,             /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare */
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    &FileData_BufferProcs,                    /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,                       /*tp_flags*/
    "gphoto2 CameraFile data buffer",         /* tp_doc */
};
%}

%init %{
  FileDataType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&FileDataType) >= 0) {
    Py_INCREF(&FileDataType);
    PyModule_AddObject(m, "FileData", (PyObject *)&FileDataType);
  }
%}

// gp_file_get_data_and_size() returns a pointer to some data
%typemap(in, numinputs=0) (const char ** data, unsigned long * size)
                          (char *temp_data, unsigned long temp_size) {
  temp_data = NULL;
  temp_size = 0;
  $1 = &temp_data;
  $2 = &temp_size;
}
%typemap(argout) (CameraFile *, const char ** data, unsigned long * size),
                 (struct _CameraFile *self, char const **data, unsigned long *size) {
  // Create a new FileData object to store result
  PyObject *file_data = PyObject_CallObject((PyObject*)&FileDataType, NULL);
  if (file_data == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Cannot create FileData");
    SWIG_fail;
  }
  FileData_set((FileData*)file_data, $1, *$2, *$3);
  $result = SWIG_Python_AppendOutput($result, file_data);
}

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
  memcpy($1, view.buf, view.len);
  $2 = view.len;
  PyBuffer_Release(&view);
}
%typemap(freearg) (char * data, unsigned long int size) {
  if ($1 && PyErr_Occurred()) free($1);
}
%typemap(doc) char * data, unsigned long int size "$1_name: readable buffer (e.g. bytes)"

// gp_file_append() takes any readable buffer
%typemap(in, numinputs=1) (const char * data, unsigned long int size) {
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
  $1 = view.buf;
  $2 = view.len;
  PyBuffer_Release(&view);
}
%typemap(doc) const char * data, unsigned long int size "$1_name: readable buffer (e.g. bytes)"

// Add default constructor and destructor to _CameraFile
struct _CameraFile {};
DEFAULT_CTOR(_CameraFile, gp_file_new)
DEFAULT_DTOR(_CameraFile, gp_file_unref)

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
    void, append, (const char *data, unsigned long int size),
    gp_file_append, ($self, data, size), 1)

// These structures are private
%ignore _CameraFileHandler;

// These functions are internal
%ignore gp_file_slurp;
%ignore gp_file_free;
%ignore gp_file_ref;
%ignore gp_file_unref;

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-file.h"
