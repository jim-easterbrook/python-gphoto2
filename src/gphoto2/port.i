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

%module(package="gphoto2") port

%{
#include "gphoto2/gphoto2.h"
%}

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

// These functions are internal
%ignore gp_port_check_int;
%ignore gp_port_check_int_fast;
%ignore gp_port_close;
%ignore gp_port_flush;
%ignore gp_port_get_error;
%ignore gp_port_get_info;
%ignore gp_port_get_pin;
%ignore gp_port_get_settings;
%ignore gp_port_get_timeout;
%ignore gp_port_open;
%ignore gp_port_read;
%ignore gp_port_reset;
%ignore gp_port_seek;
%ignore gp_port_send_break;
%ignore gp_port_send_scsi_cmd;
%ignore gp_port_set_error;
%ignore gp_port_set_info;
%ignore gp_port_set_pin;
%ignore gp_port_set_settings;
%ignore gp_port_set_timeout;
%ignore gp_port_usb_clear_halt;
%ignore gp_port_usb_find_device;
%ignore gp_port_usb_find_device_by_class;
%ignore gp_port_usb_msg_class_read;
%ignore gp_port_usb_msg_class_write;
%ignore gp_port_usb_msg_interface_read;
%ignore gp_port_usb_msg_interface_write;
%ignore gp_port_usb_msg_read;
%ignore gp_port_usb_msg_write;
%ignore gp_port_write;

%include "gphoto2/gphoto2-port.h"
