python-gphoto2
==============

python-gphoto2 is a very basic (low-level) Python interface to [libgphoto2](http://www.gphoto.org/proj/libgphoto2/).
It is built using [SWIG](http://swig.org/) to automatically generate the interface code.
This gives direct access to the libgphoto2 functions, but in a rather un-Pythonic manner.

There are some Python helper classes to ease access to many of the low-level functions.
This makes the package a bit more Pythonic, but you will still need to deal directly with the lower level at times.

There are still parts of the libgphoto2 API that are not included in python-gphoto2.
Please let me know if you have any specific requirements.

Dependencies
------------

*   Python: <http://python.org/>
*   SWIG: <http://swig.org/>
*   libgphoto2: <http://www.gphoto.org/proj/libgphoto2/> version 2.5 or greater

Note that you need the "development headers" versions of libgphoto2 and Python.
Most Linux distributions' package managers have these, but the names vary.
Look for `libgphoto2-2-dev` or `libgphoto2-devel` or something similar.

Building and installation
-------------------------

Python's `distutils` are used to build and install python-gphoto2:

    python setup.py build
    python setup.py build
    sudo python setup.py install

Note the repetition of the `build` command - the first one runs SWIG and creates Python interface files which are then built on the second run.

Documentation
-------------

After building and installing `pydoc gphoto2` will display copious documentation.
In general it is easier to use the C [API documentation](http://www.gphoto.org/doc/api/).

There is one major difference between the Python and C APIs.
C functions that are passed a pointer to a pointer (and usually do some memory allocation) such as [gp_camera_new](http://www.gphoto.org/doc/api/gphoto2-camera_8h.html) have Python equivalents that create the required pointer and return it in a list with the gphoto2 error code.
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
This function also unwraps lists such as that returned by `gp.gp_camera_new` in the example.
Using this function the example becomes:

    import gphoto2 as gp
    camera = gp.check_result(gp.gp_camera_new())
    ...
    gp.check_result(gp.gp_camera_unref(camera))

The Python helper classes deal with cleaning up and make things even simpler.
Here is a complete example:

    import gphoto2 as gp
    with gp.Context() as context:
        with gp.Camera(context.context) as camera:
            camera.init()
            text = gp.CameraText()
            camera.get_summary(text)
            print 'Summary'
            print '======='
            print text.text
            camera.exit()

Other functions that have result pointer parameters in the C versions also return a list containing the error code and result value(s) in their Python versions.

Some functions, such as [gp_widget_get_value](http://www.gphoto.org/doc/api/gphoto2-widget_8h.html), can return different types using a `void *` pointer in C.
The Python interface includes type specific functions such as `gp_widget_get_value_text` that can be used from Python.

See the example programs for typical usage of the Python gphoto2 API.

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
