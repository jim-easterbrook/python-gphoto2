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

%module(package="gphoto2", threads="1") camera
%nothread;

%{
#include "gphoto2/gphoto2.h"
%}

%include "macros.i"

AUTODOC

%import "abilities_list.i"
%import "filesys.i"
%import "result.i"
%import "widget.i"

%include "typemaps.i"

%include "stdint.i"

IMPORT_GPHOTO2_ERROR()

%rename(Camera) _Camera;

// Allow other Python threads to continue during some function calls
%thread gp_camera_wait_for_event;
%thread gp_camera_capture;
%thread gp_camera_trigger_capture;
%thread gp_camera_capture_preview;
%thread gp_camera_get_config;
%thread gp_camera_get_single_config;
%thread gp_camera_folder_list_files;
%thread gp_camera_folder_list_folders;
%thread gp_camera_folder_delete_all;
%thread gp_camera_folder_put_file;
%thread gp_camera_file_get;
%thread gp_camera_file_get_info;
%thread gp_camera_file_read;

// Make docstring parameter types more Pythonic
%typemap(doc) (Camera *) "$1_name: $*1_type"

// gp_camera_new() returns a pointer in an output parameter
PLAIN_ARGOUT(Camera **)

// gp_camera_get_summary() etc. return a pointer in an output parameter
CALLOC_ARGOUT(CameraText *summary)
CALLOC_ARGOUT(CameraText *manual)
CALLOC_ARGOUT(CameraText *about)

// gp_camera_folder_list_files() etc. return a pointer in an output parameter
NEW_ARGOUT(CameraList *, gp_list_new, gp_list_unref)

// gp_camera_capture_preview() & gp_camera_file_get() return a pointer
NEW_ARGOUT(CameraFile *camera_file, gp_file_new, gp_file_unref)
// Redefine signature as gp_camera_folder_put_file() also uses *file
int gp_camera_capture_preview(Camera *camera, CameraFile *camera_file, GPContext *context);
%ignore gp_camera_capture_preview;

// gp_camera_capture() returns a pointer in an output parameter
CALLOC_ARGOUT(CameraFilePath *path)

// gp_camera_file_read() fills a user-supplied buffer
%typemap(doc) (char * buf, uint64_t * size) "$1_name: writable buffer"
%typemap(in, numinputs=1) (char * buf, uint64_t * size) (uint64_t temp) {
  Py_buffer view;
  if (PyObject_CheckBuffer($input) != 1) {
    PyErr_SetString(
      PyExc_TypeError,
      "in method '$symname', argument $argnum does not support the buffer interface");
    SWIG_fail;
  }
  if (PyObject_GetBuffer($input, &view, PyBUF_SIMPLE | PyBUF_WRITABLE) != 0) {
    PyErr_SetString(
      PyExc_TypeError,
      "in method '$symname', argument $argnum does not export a writable buffer");
    SWIG_fail;
  }
  $1 = view.buf;
  temp = view.len;
  $2 = &temp;
  PyBuffer_Release(&view);
}
%typemap(argout) (char * buf, uint64_t * size) {
  $result = SWIG_Python_AppendOutput($result, PyLong_FromUnsignedLongLong(*$2));
}

// Add default constructor and destructor to _Camera
DEFAULT_CTOR(_Camera, Camera, gp_camera_new)
DEFAULT_DTOR(_Camera, gp_camera_unref)
%ignore gp_camera_ref;
%ignore gp_camera_unref;

// Add member methods to _Camera
MEMBER_FUNCTION(_Camera, Camera,
    set_abilities, (CameraAbilities abilities),
    gp_camera_set_abilities, ($self, abilities))
MEMBER_FUNCTION(_Camera, Camera,
    get_abilities, (CameraAbilities *abilities),
    gp_camera_get_abilities, ($self, abilities))
MEMBER_FUNCTION(_Camera, Camera,
    set_port_info, (GPPortInfo info),
    gp_camera_set_port_info, ($self, info))
MEMBER_FUNCTION(_Camera, Camera,
    get_port_info, (GPPortInfo *info),
    gp_camera_get_port_info, ($self, info))
MEMBER_FUNCTION(_Camera, Camera,
    set_port_speed, (int speed),
    gp_camera_set_port_speed, ($self, speed))
INT_MEMBER_FUNCTION(_Camera, Camera,
    get_port_speed, (),
    gp_camera_get_port_speed, ($self))
MEMBER_FUNCTION(_Camera, Camera,
    init, (GPContext *context),
    gp_camera_init, ($self, context))
MEMBER_FUNCTION(_Camera, Camera,
    exit, (GPContext *context),
    gp_camera_exit, ($self, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    get_config, (CameraWidget **window, GPContext *context),
    gp_camera_get_config, ($self, window, context))
#if GPHOTO2_VERSION >= 0x02050a
MEMBER_FUNCTION(_Camera, Camera,
    list_config, (CameraList *list, GPContext *context),
    gp_camera_list_config, ($self, list, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    get_single_config, (const char *name, CameraWidget **widget, GPContext *context),
    gp_camera_get_single_config, ($self, name, widget, context))
#endif
MEMBER_FUNCTION(_Camera, Camera,
    set_config, (CameraWidget *window, GPContext *context),
    gp_camera_set_config, ($self, window, context))
#if GPHOTO2_VERSION >= 0x02050a
MEMBER_FUNCTION(_Camera, Camera,
    set_single_config, (const char *name, CameraWidget *widget, GPContext *context),
    gp_camera_set_single_config, ($self, name, widget, context))
#endif
MEMBER_FUNCTION(_Camera, Camera,
    get_summary, (CameraText *summary, GPContext *context),
    gp_camera_get_summary, ($self, summary, context))
MEMBER_FUNCTION(_Camera, Camera,
    get_manual, (CameraText *manual, GPContext *context),
    gp_camera_get_manual, ($self, manual, context))
MEMBER_FUNCTION(_Camera, Camera,
    get_about, (CameraText *about, GPContext *context),
    gp_camera_get_about, ($self, about, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    capture, (CameraCaptureType type, CameraFilePath *path, GPContext *context),
    gp_camera_capture, ($self, type, path, context))
#if GPHOTO2_VERSION >= 0x020500
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    trigger_capture, (GPContext *context),
    gp_camera_trigger_capture, ($self, context))
#endif
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    capture_preview, (CameraFile *camera_file, GPContext *context),
    gp_camera_capture_preview, ($self, camera_file, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    wait_for_event,
    (int timeout, CameraEventType *eventtype, void **eventdata, GPContext *context),
    gp_camera_wait_for_event, ($self, timeout, eventtype, eventdata, context))
MEMBER_FUNCTION(_Camera, Camera,
    get_storageinfo, (CameraStorageInformation **sifs, int *nrofsifs, GPContext *context),
    gp_camera_get_storageinfo, ($self, sifs, nrofsifs, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    folder_list_files, (const char *folder, CameraList *list, GPContext *context),
    gp_camera_folder_list_files, ($self, folder, list, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    folder_list_folders, (const char *folder, CameraList *list, GPContext *context),
    gp_camera_folder_list_folders, ($self, folder, list, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    folder_delete_all, (const char *folder, GPContext *context),
    gp_camera_folder_delete_all, ($self, folder, context))
#if GPHOTO2_VERSION < 0x020500
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    folder_put_file, (const char *folder, CameraFile *file, GPContext *context),
    gp_camera_folder_put_file, ($self, folder, file, context))
#else
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    folder_put_file, (const char *folder, const char *filename, CameraFileType type, CameraFile *file, GPContext *context),
    gp_camera_folder_put_file, ($self, folder, filename, type, file, context))
#endif
MEMBER_FUNCTION(_Camera, Camera,
    folder_make_dir, (const char *folder, const char *name, GPContext *context),
    gp_camera_folder_make_dir, ($self, folder, name, context))
MEMBER_FUNCTION(_Camera, Camera,
    folder_remove_dir, (const char *folder, const char *name, GPContext *context),
    gp_camera_folder_remove_dir, ($self, folder, name, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    file_get_info, (const char *folder, const char *file, CameraFileInfo *info, GPContext *context),
    gp_camera_file_get_info, ($self, folder, file, info, context))
MEMBER_FUNCTION(_Camera, Camera,
    file_set_info, (const char *folder, const char *file, CameraFileInfo info, GPContext *context),
    gp_camera_file_set_info, ($self, folder, file, info, context))
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    file_get, (const char *folder, const char *file, CameraFileType type, CameraFile *camera_file, GPContext *context),
    gp_camera_file_get, ($self, folder, file, type, camera_file, context))
#if GPHOTO2_VERSION >= 0x020500
MEMBER_FUNCTION_THREAD(_Camera, Camera,
    file_read, (const char *folder, const char *file, CameraFileType type, uint64_t offset, char *buf, uint64_t *size, GPContext *context),
    gp_camera_file_read, ($self, folder, file, type, offset, buf, size, context))
#endif
MEMBER_FUNCTION(_Camera, Camera,
    file_delete, (const char *folder, const char *file, GPContext *context),
    gp_camera_file_delete, ($self, folder, file, context))

// gp_camera_get_storageinfo() returns an allocated array in an output parameter
%typemap(in, numinputs=0)
    (CameraStorageInformation **, int *)
        (CameraStorageInformation* temp_ptr, int temp_cnt),
    (CameraStorageInformation **sifs, int *nrofsifs)
        (CameraStorageInformation* temp_ptr, int temp_cnt){
  $1 = &temp_ptr;
  $2 = &temp_cnt;
}
%typemap(argout) (CameraStorageInformation **, int *),
                 (CameraStorageInformation **sifs, int *nrofsifs) {
  // copy single array of CameraStorageInformation to individual Python objects
  PyObject* out_list = PyList_New(*$2);
  int n;
  for (n = 0; n < *$2; n++) {
    CameraStorageInformation* new_sif = malloc(sizeof(CameraStorageInformation));
    if (new_sif == NULL) {
      PyErr_SetString(PyExc_MemoryError, "Cannot allocate " "$*1_type");
      SWIG_fail;
    }
    memcpy(new_sif, &(*$1)[n], sizeof(CameraStorageInformation));
    PyList_SetItem(out_list, n,
        SWIG_NewPointerObj(new_sif, SWIGTYPE_p__CameraStorageInformation, SWIG_POINTER_OWN));
  }
  $result = SWIG_Python_AppendOutput($result, out_list);
}
%typemap(freearg) (CameraStorageInformation **, int *),
                  (CameraStorageInformation **sifs, int *nrofsifs) {
  // deallocate CameraStorageInformation array allocated by gp_camera_get_storageinfo
  free(*$1);
}

// gp_camera_wait_for_event() returns two pointers in output parameters
%typemap(in, numinputs=0) (CameraEventType * eventtype, void ** eventdata)
                          (CameraEventType temp_type, void *temp_data) {
  $1 = &temp_type;
  $2 = &temp_data;
}
%typemap(argout) (CameraEventType * eventtype, void ** eventdata) {
  $result = SWIG_Python_AppendOutput($result, PyInt_FromLong(*$1));
  if (*$1 == GP_EVENT_FILE_ADDED || *$1 == GP_EVENT_FOLDER_ADDED) {
    $result = SWIG_Python_AppendOutput(
      $result, SWIG_NewPointerObj(*$2, SWIGTYPE_p_CameraFilePath, SWIG_POINTER_OWN));
  }
  else {
    Py_INCREF(Py_None);
    $result = SWIG_Python_AppendOutput($result, Py_None);
  }
}

// Add __str__ method to CameraText
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "tp_str", functype="reprfunc") CameraText::__str__;
#endif // SWIGPYTHON_BUILTIN
%extend CameraText {
  char *__str__() {
    return $self->text;
  }
};

// Don't wrap deprecated functions
%ignore gp_camera_free;

// These structures are private
%ignore _CameraFunctions;

// Use library functions to access these
%ignore _Camera::pl;
%ignore _Camera::pc;
%ignore _Camera::port;
%ignore _Camera::fs;
%ignore _Camera::functions;

// Other structures are read only
%immutable;

%include "gphoto2/gphoto2-camera.h"
