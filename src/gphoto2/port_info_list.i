// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") port_info_list

%include "common/preamble.i"

%rename(PortInfoList) _GPPortInfoList;

%typemap(in, numinputs=0) GPPortInfo * (GPPortInfo temp) {
  temp = NULL;
  $1 = &temp;
}
%typemap(argout) GPPortInfo * {
  $result = SWIG_Python_AppendOutput(
    $result, SWIG_NewPointerObj(*$1, $descriptor(_GPPortInfo*), 0));
}

// Make docstring parameter types more Pythonic
%typemap(doc) GPPortInfo "$1_name: gphoto2.$1_type";
%typemap(doc) GPPortInfoList * "$1_name: gphoto2.$*1_type";

#ifndef SWIGIMPORTED

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_port_info_list_new() returns a pointer in an output parameter
PLAIN_ARGOUT(GPPortInfoList **)

// gp_port_info_get_type returns a pointer to an enum
%apply int *OUTPUT { GPPortType * };

// Make GPPortInfoList more like a Python list
LEN_MEMBER_FUNCTION(_GPPortInfoList, gp_port_info_list_count)
#if defined(SWIGPYTHON_BUILTIN)
%feature("python:slot", "sq_item",   functype="ssizeargfunc") _GPPortInfoList::__getitem__;
#endif
%exception __getitem__ {
  $action
  if (PyErr_Occurred() != NULL) {
    goto fail;
  }
}
%extend _GPPortInfoList {
  void __getitem__(int idx, GPPortInfo *info) {
    if (idx < 0 || idx >= gp_port_info_list_count($self)) {
      PyErr_SetString(PyExc_IndexError, "GPPortInfoList index out of range");
      return;
    }
    {
      int error = gp_port_info_list_get_info($self, idx, info);
      if (error < GP_OK) {
        GPHOTO2_ERROR(error)
        return;
      }
    }
  }
};

// Add member methods to _GPPortInfo
struct _GPPortInfo {};
MEMBER_FUNCTION(_GPPortInfo,
    void, get_name, (char **name),
    gp_port_info_get_name, ($self, name), )
MEMBER_FUNCTION(_GPPortInfo,
    void, get_path, (char **path),
    gp_port_info_get_path, ($self, path), )
MEMBER_FUNCTION(_GPPortInfo,
    void, get_type, (GPPortType *type),
    gp_port_info_get_type, ($self, type), )

// Add default constructor and destructor to _GPPortInfoList
struct _GPPortInfoList {};
DEFAULT_CTOR(_GPPortInfoList, gp_port_info_list_new)
DEFAULT_DTOR(_GPPortInfoList, gp_port_info_list_free)

// Add member methods to _GPPortInfoList
MEMBER_FUNCTION(_GPPortInfoList,
    void, append, (GPPortInfo info),
    gp_port_info_list_append, ($self, info), )
MEMBER_FUNCTION(_GPPortInfoList,
    void, load, (),
    gp_port_info_list_load, ($self), )
MEMBER_FUNCTION(_GPPortInfoList,
    int, count, (),
    gp_port_info_list_count, ($self), )
MEMBER_FUNCTION(_GPPortInfoList,
    int, lookup_path, (const char *path),
    gp_port_info_list_lookup_path, ($self, path), )
MEMBER_FUNCTION(_GPPortInfoList,
    int, lookup_name, (const char *name),
    gp_port_info_list_lookup_name, ($self, name), )
MEMBER_FUNCTION(_GPPortInfoList,
    void, get_info, (const int n, GPPortInfo *info),
    gp_port_info_list_get_info, ($self, n, info), )

// Substitute definitions of things added during libgphoto2 development
%{
#if GPHOTO2_VERSION < 0x02051e00
int gp_port_init_localedir(const char *localedir) {
    return GP_ERROR_NOT_SUPPORTED;
}
#endif
#if GPHOTO2_VERSION < 0x02051800
  int GP_PORT_IP = GP_PORT_USB_SCSI + 1;
#endif
%}

// Don't wrap internal functions
%ignore gp_port_info_new;
%ignore gp_port_info_set_name;
%ignore gp_port_info_set_path;
%ignore gp_port_info_set_type;
%ignore gp_port_info_get_library_filename;
%ignore gp_port_info_set_library_filename;
%ignore gp_port_info_list_free;

// Turn off default exception handling
%noexception;

#endif //ifndef SWIGIMPORTED

%include "gphoto2/gphoto2-port-info-list.h"
