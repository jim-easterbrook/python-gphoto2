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

%module(package="gphoto2.lib") gphoto2_version

%{
#include "gphoto2/gphoto2.h"
#include "gphoto2/gphoto2-version.h"
%}

%feature("autodoc", "2");

%include "typemaps.i"

%typemap(out) char ** {
  $result = PyList_New(0);
  char **line = $1;
  int i;
  while (*line) {
    PyList_Append($result, PyString_FromString(*line));
    line++;
  }
}

%include "gphoto2/gphoto2-port-version.h"
%include "gphoto2/gphoto2-version.h"
