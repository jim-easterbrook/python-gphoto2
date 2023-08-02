// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014-23  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

%module(package="gphoto2") filesys

%include "common/preamble.i"

%import "file.i"

// gp_camera_file_get_info() etc. return a pointer in an output parameter
CALLOC_ARGOUT(CameraFileInfo *info)

// Make docstring parameter types more Pythonic
%typemap(doc) CameraFileInfo "$1_name: gphoto2.$1_type"

// image dimensions use uint32_t and storage info uses uint64_t
%include "stdint.i"

// Add constructor to CameraFileInfo
%defaultctor _CameraFileInfo;

// Ignore functions only used by camera drivers
%ignore gp_filesystem_append;
%ignore gp_filesystem_count;
%ignore gp_filesystem_delete_all;
%ignore gp_filesystem_delete_file;
%ignore gp_filesystem_delete_file_noop;
%ignore gp_filesystem_dump;
%ignore gp_filesystem_free;
%ignore gp_filesystem_get_file;
%ignore gp_filesystem_get_folder;
%ignore gp_filesystem_get_info;
%ignore gp_filesystem_get_storageinfo;
%ignore gp_filesystem_list_files;
%ignore gp_filesystem_list_folders;
%ignore gp_filesystem_make_dir;
%ignore gp_filesystem_name;
%ignore gp_filesystem_new;
%ignore gp_filesystem_number;
%ignore gp_filesystem_put_file;
%ignore gp_filesystem_read_file;
%ignore gp_filesystem_remove_dir;
%ignore gp_filesystem_reset;
%ignore gp_filesystem_set_file_noop;
%ignore gp_filesystem_set_funcs;
%ignore gp_filesystem_set_info;
%ignore gp_filesystem_set_info_noop;
%ignore gp_filesystem_set_info_dirty;

// Ignore internal structures
%ignore CameraFilesystem;
%ignore CameraFilesystemFuncs;
%ignore _CameraFilesystemFuncs;

// Camera storage is immutable
%immutable _CameraStorageInformation::fields;
%immutable _CameraStorageInformation::basedir;
%immutable _CameraStorageInformation::label;
%immutable _CameraStorageInformation::description;
%immutable _CameraStorageInformation::type;
%immutable _CameraStorageInformation::fstype;
%immutable _CameraStorageInformation::access;
%immutable _CameraStorageInformation::capacitykbytes;
%immutable _CameraStorageInformation::freekbytes;
%immutable _CameraStorageInformation::freeimages;

// Top level of CameraFileInfo is immutable
%immutable _CameraFileInfo::preview;
%immutable _CameraFileInfo::file;
%immutable _CameraFileInfo::audio;

%include "gphoto2/gphoto2-filesys.h"
