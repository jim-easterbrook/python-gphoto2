// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2023-25  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") port
#pragma SWIG nowarn=321

%include "common/preamble.i"

%import "port_info_list.i"

// Turn on default exception handling
DEFAULT_EXCEPTION

// gp_port_new() returns a pointer in an output parameter
PLAIN_ARGOUT(GPPort **)

// Add default constructor and destructor to _GPPort
DEFAULT_CTOR(_GPPort, gp_port_new)
DEFAULT_DTOR(_GPPort, gp_port_free)

// Add member methods to _GPPort
MEMBER_FUNCTION(_GPPort,
    void, close, (),
    gp_port_close, ($self), )
MEMBER_FUNCTION(_GPPort,
    void, get_info, (GPPortInfo *info),
    gp_port_get_info, ($self, info), )
MEMBER_FUNCTION(_GPPort,
    void, open, (),
    gp_port_open, ($self), )
MEMBER_FUNCTION(_GPPort,
    void, reset, (),
    gp_port_reset, ($self), )
MEMBER_FUNCTION(_GPPort,
    void, set_info, (GPPortInfo info),
    gp_port_set_info, ($self, info), )

// Don't wrap internal functions
%ignore gp_port_check_int;
%ignore gp_port_check_int_fast;
%ignore gp_port_flush;
%ignore gp_port_free;
%ignore gp_port_get_error;
%ignore gp_port_get_pin;
%ignore gp_port_get_settings;
%ignore gp_port_get_timeout;
%ignore gp_port_read;
%ignore gp_port_seek;
%ignore gp_port_send_break;
%ignore gp_port_send_scsi_cmd;
%ignore gp_port_set_error;
%ignore gp_port_set_pin;
%ignore gp_port_set_settings;
%ignore gp_port_set_timeout;
%ignore gp_port_usb_clear_halt;
%ignore gp_port_usb_find_device;
%ignore gp_port_usb_find_device_by_class;
%ignore gp_port_usb_get_sys_device;
%ignore gp_port_usb_msg_class_read;
%ignore gp_port_usb_msg_class_write;
%ignore gp_port_usb_msg_interface_read;
%ignore gp_port_usb_msg_interface_write;
%ignore gp_port_usb_msg_read;
%ignore gp_port_usb_msg_write;
%ignore gp_port_usb_set_sys_device;
%ignore gp_port_write;

%ignore _GPPort::type;
%ignore _GPPort::settings;
%ignore _GPPort::settings_pending;
%ignore _GPPort::timeout;
%ignore _GPPort::pl;
%ignore _GPPort::pc;

%ignore _GPPortSettings;
%ignore _GPPortSettingsSerial;
%ignore _GPPortSettingsUSB;
%ignore _GPPortSettingsUsbDiskDirect;
%ignore _GPPortSettingsUsbScsi;

// Turn off default exception handling
%noexception;

%include "gphoto2/gphoto2-port.h"
