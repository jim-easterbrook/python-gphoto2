python-gphoto2
==============

python-gphoto2 is a very basic (low-level) Python interface to [libgphoto2](http://www.gphoto.org/proj/libgphoto2/).
It is built using [SWIG](http://swig.org/) to automatically generate the interface code.
This gives direct access to the libgphoto2 functions, but in a rather un-Pythonic manner.

There are still parts of the libgphoto2 API that are not included in python-gphoto2.
Please let me know if you have any specific requirements.

Dependencies
------------

*   Python: <http://python.org/>
*   SWIG: <http://swig.org/>
*   libgphoto2: <http://www.gphoto.org/proj/libgphoto2/>

Building and installation
-------------------------

Python's `distutils` are used to build and install python-gphoto2:

    python setup.py build
    python setup.py build
    sudo python setup.py install

Note the repetition of the `build` command -- the first one runs SWIG and creates a Python interface file which is then used on the second run.

Documentation
-------------

After building and installing `pydoc gphoto2` will generate copious documentation.
In general it is easier to use the `C` [API documentation](http://www.gphoto.org/doc/api/).

Legalese
--------

python-gphoto2 - Python interface to libgphoto2
<http://github.com/jim-easterbrook/python-gphoto2>
Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
