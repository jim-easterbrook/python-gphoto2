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

%module(package="gphoto2") file
#pragma SWIG nowarn=321

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

%include "typemaps.i"

IMPORT_GPHOTO2_ERROR()

%rename(CameraFile) _CameraFile;

// Make docstring parameter types more Pythonic
%typemap(doc) CameraFile * "$1_name: $*1_type"
%typemap(doc) CameraFileHandler * "$1_name: $*1_type"

// gp_file_get_mtime() returns a pointer in output params
typedef long int time_t;
%apply time_t *OUTPUT { time_t * };

// gp_file_new() returns a pointer in an output parameter
PLAIN_ARGOUT(CameraFile **)

// make gp_file_open() create a new CameraFile
NEW_ARGOUT(CameraFile *camera_file, gp_file_new, gp_file_unref)
// Redefine signature as many other functions also use *file
int gp_file_open(CameraFile *camera_file, const char *filename);
%ignore gp_file_open;

// gp_file_get_name(), gp_file_get_mime_type() & gp_file_get_name_by_type
// return pointers in output params
STRING_ARGOUT()

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
#if PY_VERSION_HEX < 0x03000000
    (readbufferproc) 0,                       /* bf_getreadbuffer */
    (writebufferproc) 0,                      /* bf_getwritebuffer */
    (segcountproc) 0,                         /* bf_getsegcount */
    (charbufferproc) 0,                       /* bf_getcharbuffer */
#endif
#if PY_VERSION_HEX >= 0x02060000
    (getbufferproc)FileData_getbuffer,        /* bf_getbuffer */
    (releasebufferproc) 0,                    /* bf_releasebuffer */
#endif
};

static PyTypeObject FileDataType = {
#if PY_VERSION_HEX >= 0x03000000
    PyVarObject_HEAD_INIT(NULL, 0)
#else
    PyObject_HEAD_INIT(NULL)
    0,                                        /* ob_size */
#endif
    "gphoto2.FileData",                       /*tp_name*/
    sizeof(FileData),                         /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)FileData_dealloc,             /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
#if PY_VERSION_HEX >= 0x03000000
    0,                                        /*tp_compare */
#else
    (cmpfunc) 0,                              /*tp_compare */
#endif
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
#if PY_VERSION_HEX >= 0x03000000
    Py_TPFLAGS_DEFAULT,                       /*tp_flags*/
#else
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_NEWBUFFER, /*tp_flags*/
#endif
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

// Add default constructor and destructor to _CameraFile
struct _CameraFile {};
DEFAULT_CTOR(_CameraFile, CameraFile, gp_file_new)
DEFAULT_DTOR(_CameraFile, gp_file_unref)
%ignore _CameraFile;
%ignore gp_file_free;
%ignore gp_file_ref;
%ignore gp_file_unref;

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
#if GPHOTO2_VERSION >= 0x020500
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

// These structures are private
%ignore _CameraFileHandler;

// These functions are internal
%ignore gp_file_slurp;

%include "gphoto2/gphoto2-file.h"
