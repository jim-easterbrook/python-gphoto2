python-gphoto2
==============

.. contents::
   :backlinks: top

python-gphoto2 is a very basic (low-level) Python interface (or binding) to `libgphoto2 <http://www.gphoto.org/proj/libgphoto2/>`_.
It is built using `SWIG <http://swig.org/>`_ to automatically generate the interface code.
This gives direct access to the libgphoto2 functions, but in a rather un-Pythonic manner.

There are some Python helper classes to ease access to many of the low-level functions.
This makes the package a bit more Pythonic, but you will still need to deal directly with the lower level at times.

Dependencies
------------

*   Python: http://python.org/ version 2.6 or greater (including Python 3)
*   SWIG: http://swig.org/
*   libgphoto2: http://www.gphoto.org/proj/libgphoto2/ version 2.4 or greater

Note that you need the "development headers" versions of libgphoto2 and Python.
Most Linux distributions' package managers have these, but the names vary.
Look for ``libgphoto2-2-dev`` or ``libgphoto2-devel`` or something similar.

Installation and testing
------------------------

There are several ways to install python-gphoto2, with varying levels of control over the installation process.
Note that they all need SWIG and the other dependencies - there are no "binary" packages at present.

Install with ``pip``
^^^^^^^^^^^^^^^^^^^^

The easiest installation method is to use the `pip <https://pip.pypa.io/>`_ command::

    sudo pip install gphoto2

Install with ``git``
^^^^^^^^^^^^^^^^^^^^

To install the very latest version, use `git <http://git-scm.com/>`_ to "clone" the GitHub repository, then change to the new directory::

    git clone https://github.com/jim-easterbrook/python-gphoto2.git
    cd python-gphoto2

Python's `distutils <https://docs.python.org/2/library/distutils.html>`_ are used to build and install python-gphoto2::

    python setup.py build
    sudo python setup.py install

Install a downloaded archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Visit the `project releases page <https://github.com/jim-easterbrook/python-gphoto2/releases>`_ or `PyPI <https://pypi.python.org/pypi/gphoto2>`_ and download one of the zip or tar.gz files, then extract it and change to the new directory.
For example::

    tar xf python-gphoto2-gphoto2-0.3.2.tar.gz
    cd python-gphoto2-gphoto2-0.3.2

As before, Python's ``distutils`` are used to build and install python-gphoto2::

    python setup.py build
    sudo python setup.py install

Testing
^^^^^^^

Connect a digital camera to your computer, switch it on, and try one of the example programs::

    python examples/camera-summary.py

.. note::
   If you installed with pip the example files should be in ``/usr/share/python-gphoto2/examples`` or somewhere similar (except for versions before 0.3.2, which didn't install the examples at all).

If this works then you're ready to start using python-gphoto2.

Using python-gphoto2
--------------------

The Python interface to libgphoto2 should allow you to do anything you could do in a C program.
However, the project is still quite young and there are probably bits missing.
Let me know if you run into any problems.

The following paragraphs show how the Python interfaces differ from C.
See the example programs for typical usage of the Python gphoto2 API.

Low-level interface
^^^^^^^^^^^^^^^^^^^

Using SWIG to generate the Python interfaces automatically means that every function in libgphoto2 *should* be available to Python.
The ``pydoc`` command can be used to show basic information about a function::

   jim@firefly ~/python-gphoto2 $ pydoc gphoto2.gp_camera_folder_list_files
   Help on built-in function gp_camera_folder_list_files in gphoto2:

   gphoto2.gp_camera_folder_list_files = gp_camera_folder_list_files(...)
       gp_camera_folder_list_files(camera, folder, list, context) -> int

       Parameters:
           camera: Camera *
           folder: char const *
           list: CameraList *
           context: GPContext *
   jim@firefly ~/python-gphoto2 $

In general it is easier to use the C `API documentation <http://www.gphoto.org/doc/api/>`_, but make sure you find the documentation for the version of libgphoto2 installed on your computer.

Note that there is one major difference between the Python and C APIs.
C functions that use a pointer parameter to return a value (and often do some memory allocation) such as `gp_camera_new() <http://www.gphoto.org/doc/api/gphoto2-camera_8h.html>`_ have Python equivalents that create the required pointer and return it in a list with the gphoto2 error code.
For example, the C code:

.. code:: c

    #include "gphoto2.h"
    int error;
    Camera *camera;
    error = gp_camera_new(&camera);
    ...
    error = gp_camera_unref(camera);

has this Python equivalent:

.. code:: python

    import gphoto2 as gp
    error, camera = gp.gp_camera_new()
    ...
    error = gp.gp_camera_unref(camera)

Some functions, such as `gp_widget_get_value() <http://www.gphoto.org/doc/api/gphoto2-widget_8h.html>`_, can return different types using a ``void *`` pointer in C.
The Python interface includes type specific functions such as ``gp_widget_get_value_text()``.

Error checking
^^^^^^^^^^^^^^

Most of the libgphoto2 functions return an integer to indicate success or failure.
The Python interface includes a function to check these values and raise an exception if an error occurs.
This function also unwraps lists such as that returned by ``gp_camera_new()`` in the example.
Using this function the example becomes:

.. code:: python

    import gphoto2 as gp
    camera = gp.check_result(gp.gp_camera_new())
    ...
    gp.check_result(gp.gp_camera_unref(camera))

Higher-level interface
^^^^^^^^^^^^^^^^^^^^^^

There are some higher-level Python helper classes that handle object creation and deletion and make things even simpler.
They provide simplified interfaces to many of the libgphoto2 functions, with shortened names and no need to pass shared data such as ``context``.
Here is a complete example program:

.. code:: python

    import gphoto2 as gp
    with gp.Context() as context:
        with gp.Camera(context.context) as camera:
            camera.init()
            text = gp.CameraText()
            camera.get_summary(text)
            print('Summary')
            print('=======')
            print(text.text)
            camera.exit()

The higher level classes and the functions they wrap are as follows.
Each class also "owns" a low-level object which is available as an attribute (e.g. to pass to other functions).

=================== =================================== ============= =============
Python class        C function                          Python method Data & C type
=================== =================================== ============= =============
Camera              gp_camera_xxx(camera, ..., context) xxx(...)      camera (Camera)
                    gp_camera_xxx(camera, ...)
CameraAbilitiesList gp_abilities_list_xxx(list, ...)    xxx(...)      list (CameraAbilitiesList)
CameraFile          gp_file_xxx(file, ...)              xxx(...)      file (CameraFile)
CameraList          gp_list_xxx(list, ...)              xxx(...)      list (CameraList)
CameraWidget        gp_widget_xxx(widget, ...)          xxx(...)      widget (CameraWidget)
Context             gp_xxx(..., context)                xxx(...)      context (GPContext)
PortInfoList        gp_port_info_list_xxx(list, ...)    xxx(...)      list (GPPortInfoList)
=================== =================================== ============= =============

Legalese
--------

python-gphoto2 - Python interface to libgphoto2
http://github.com/jim-easterbrook/python-gphoto2
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
along with this program.  If not, see http://www.gnu.org/licenses/.
