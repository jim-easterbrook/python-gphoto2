// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-16  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") port

%{
#include "gphoto2/gphoto2.h"
%}

%import "port_info_list.i"

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

IMPORT_GPHOTO2_ERROR()

// Make docstring parameter types more Pythonic
%typemap(doc) GPPort * "$1_name: $*1_type"

// gp_port_new() returns a pointer in an output parameter
PLAIN_ARGOUT(GPPort **)

// Add default constructor and destructor to _GPPort
#if SWIG_VERSION < 0x020005
#define _GPPort GPPort
#endif
DEFAULT_CTOR(_GPPort, GPPort, gp_port_new)
DEFAULT_DTOR(_GPPort, gp_port_free)
%ignore gp_port_free;

// These structures are private
%ignore _GPPortSettings;
%ignore _GPPortSettingsSerial;
%ignore _GPPortSettingsUSB;
%ignore _GPPortSettingsUsbDiskDirect;
%ignore _GPPortSettingsUsbScsi;

// Use library functions to access these
%ignore _GPPort::type;
%ignore _GPPort::settings;
%ignore _GPPort::settings_pending;
%ignore _GPPort::timeout;
%ignore _GPPort::pl;
%ignore _GPPort::pc;

%include "gphoto2/gphoto2-port.h"
%include "gphoto2/gphoto2-port-portability.h"
