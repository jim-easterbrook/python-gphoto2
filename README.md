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

Note the repetition of the `build` command - the first one runs SWIG and creates a Python interface file which is then used on the second run.

Documentation
-------------

After building and installing `pydoc gphoto2` will generate copious documentation.
In general it is easier to use the C [API documentation](http://www.gphoto.org/doc/api/).

There is one major difference between the Python and C APIs.
C functions that are passed a pointer to a pointer (and usually do some memory allocation) such as [gp_camera_new](http://www.gphoto.org/doc/api/gphoto2-camera_8h.html#a34f54a290d83399407fbe44d270c0ca) have Python equivalents that create the required pointer and return it in a tuple with the gphoto2 error code.
For example, the C code:
    #include "gphoto2.h"
    int error;
    Camera *camera;
    error = gp_camera_new(&camera);
    ...
    error = gp_camera_unref(camera);
has this Python equivalent:
    import gphoto2 as gp
    error, camera = gp.gp_camera_new()
    ...
    error = gp.gp_camera_unref(camera)

The Python interface includes a function to check gphoto2 error values and raise an exception if an error occurs.
This function also unwraps tuples such as that returned by `gp.gp_camera_new` in the example.
Using this function the example becomes:
    import gphoto2 as gp
    camera = gp.check_result(gp.gp_camera_new())
    ...
    gp.check_result(gp.gp_camera_unref(camera))

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
