python-gphoto2
==============

python-gphoto2 is a comprehensive Python interface (or binding) to `libgphoto2 <http://www.gphoto.org/proj/libgphoto2/>`_.
It is built using `SWIG <http://swig.org/>`_ to automatically generate the interface code.
This gives direct access to nearly all the libgphoto2 functions, but sometimes in a rather un-Pythonic manner.

Other Python bindings to libgphoto2 are available:
`piggyphoto <https://github.com/alexdu/piggyphoto>`_ uses ctypes (included in standard Python installations) to interface to the library.
The gphoto2 source tree includes some `Python bindings <http://sourceforge.net/p/gphoto/code/HEAD/tree/trunk/bindings/libgphoto2-python/>`_ which also use ctypes.
`gphoto2-cffi <https://github.com/jbaiter/gphoto2-cffi>`_ uses `cffi <http://cffi.readthedocs.org/>`_.

.. contents::
   :backlinks: top

Dependencies
------------

*   Python: http://python.org/ version 2.6 or greater (including Python 3)
*   libgphoto2: http://www.gphoto.org/proj/libgphoto2/ version 2.4 or greater
*   SWIG: http://swig.org/ (optional since python-gphoto2 v0.11)

Note that you need the "development headers" versions of libgphoto2 and Python.
Most Linux distributions' package managers have these, but the names vary.
Look for ``libgphoto2-2-dev`` or ``libgphoto2-devel`` or something similar.

Installation and testing
------------------------

There are several ways to install python-gphoto2, with varying levels of control over the installation process.

The commands below will install python-gphoto2 for your default Python version.
To install for both Python 2 and Python 3, run the installation process twice with specific commands, i.e. ``pip2`` and ``pip3`` or ``python2`` and ``python3``.

Install with ``pip``
^^^^^^^^^^^^^^^^^^^^

The easiest installation method is to use the `pip <https://pip.pypa.io/>`_ command::

    sudo pip install gphoto2

Note that this may take longer than you expect as the SWIG generated files are compiled during installation.

Install a downloaded archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Visit `PyPI <https://pypi.python.org/pypi/gphoto2>`_ and download one of the zip or tar.gz files, then extract it and change to the new directory.
For example::

    tar xzf gphoto2-0.11.0.tar.gz
    cd gphoto2-0.11.0

Python's `distutils <https://docs.python.org/2/library/distutils.html>`_ are used to build and install python-gphoto2::

    python setup.py build
    sudo python setup.py install

Install from GitHub (SWIG required)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To install the very latest version, use `git <http://git-scm.com/>`_ to "clone" the GitHub repository, then change to the new directory::

    git clone https://github.com/jim-easterbrook/python-gphoto2.git
    cd python-gphoto2

As before, Python's ``distutils`` are used to build and install python-gphoto2, but now you have to run SWIG first to generate the files to be compiled::

    python setup.py build_swig
    python setup.py build
    sudo python setup.py install

See "running SWIG" below for more detail.

Testing
^^^^^^^

.. note:: If you installed with pip the example files should be in ``/usr/share/python-gphoto2/examples`` or ``/usr/local/share/python-gphoto2/examples`` or somewhere similar.
   Otherwise they are in the ``examples`` sub-directory of your working directory.

Connect a digital camera to your computer, switch it on, and try one of the example programs::

    python examples/camera-summary.py

If this works then you're ready to start using python-gphoto2.

Using python-gphoto2
--------------------

The Python interface to libgphoto2 should allow you to do anything you could do in a C program.
However, the project is quite young and there are still bits missing and functions that cannot be called from Python.
Let me know if you run into any problems.

The following paragraphs show how the Python interfaces differ from C.
See the example programs for typical usage of the Python gphoto2 API.

"C" interface
^^^^^^^^^^^^^

Using SWIG to generate the Python interfaces automatically means that every function in libgphoto2 *should* be available to Python.
The ``pydoc`` command can be used to show basic information about a function::

   jim@firefly ~/python-gphoto2 $ pydoc gphoto2.gp_camera_folder_list_files
   Help on built-in function gp_camera_folder_list_files in gphoto2:

   gphoto2.gp_camera_folder_list_files = gp_camera_folder_list_files(...)
       gp_camera_folder_list_files(camera, folder, context) -> int

       Parameters:
           camera: Camera *
           folder: char const *
           context: Context *


       See also: gphoto2.Camera.folder_list_files

   jim@firefly ~/python-gphoto2 $ 

If you compare this to the C `API documentation <http://www.gphoto.org/doc/api/>`_ of ``gp_camera_folder_list_files`` you will see that the C function signature includes an additional parameter "``list``" of type "``CameraList *``".
This is an "output" parameter, a concept that doesn't really exist in Python.
The Python version of ``gp_camera_folder_list_files`` returns a sequence containing the integer error code and the ``list`` value.

Most of the libgphoto2 functions that use pointer parameters to return values in the C API have been adapted like this in the Python API.
(Unfortunately I've not found a way to persuade SWIG to include this extra return value in the documentation.
You should use ``pydoc`` to check the parameters expected by the Python function.)

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

Note that the gp_camera_unref() call is not needed (since python-gphoto2 version 0.5.0).
It is called automatically when the python camera object is deleted.

Here is a complete example program (without any error checking):

.. code:: python

    import gphoto2 as gp
    context = gp.gp_context_new()
    error, camera = gp.gp_camera_new()
    error = gp.gp_camera_init(camera, context)
    error, text = gp.gp_camera_get_summary(camera, context)
    print('Summary')
    print('=======')
    print(text.text)
    error = gp.gp_camera_exit(camera, context)

"Object oriented" interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^

SWIG has the ability to attach member functions to C structs such as the GPhoto2 ``Camera`` object.
The Python interface includes many such member functions, allowing GPhoto2 to be used in a more "Pythonic" style.
These member functions also include error checking.
If an error occurs they raise a Python ``GPhoto2Error`` exception.

The example program can be re-written as follows:

.. code:: python

    import gphoto2 as gp
    context = gp.Context()
    camera = gp.Camera()
    camera.init(context)
    text = camera.get_summary(context)
    print('Summary')
    print('=======')
    print(str(text))
    camera.exit(context)

The member functions are more "hand crafted" than the rest of the Python bindings, which are automatically generated from the library header files.
This means that there are some functions in the "C" interface that do not have corresponding member methods.
Those that do include a "see also" reference in their docstring, as shown in the ``pydoc`` example above.

Error checking
^^^^^^^^^^^^^^

Most of the libgphoto2 functions return an integer to indicate success or failure.
The Python interface includes a ``check_result()`` function to check these values and raise a ``GPhoto2Error`` exception if an error occurs.

This function also removes the error code from lists such as that returned by ``gp_camera_new()`` in the example.
Using this function the earlier example becomes:

.. code:: python

    import gphoto2 as gp
    context = gp.gp_context_new()
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera, context))
    text = gp.check_result(gp.gp_camera_get_summary(camera, context))
    print('Summary')
    print('=======')
    print(text.text)
    gp.check_result(gp.gp_camera_exit(camera, context))

There may be some circumstances where you don't want an exception to be raised when some errors occur.
You can "fine tune" the behaviour of the ``check_result()`` function by adjusting the ``error_severity`` variable:

.. code:: python

    import gphoto2 as gp
    gp.error_severity[gp.GP_ERROR] = logging.WARNING
    ...

In this case a warning message will be logged (using Python's standard logging module) but no exception will be raised when a ``GP_ERROR`` error occurs.
However, this is a "blanket" approach that treats all ``GP_ERROR`` errors the same.
It is better to test for particular error conditions after particular operations, as described below.

The ``GPhoto2Error`` exception object has two attributes that may be useful in an exception handler.
``GPhoto2Error.code`` stores the integer error generated by the library function and ``GPhoto2Error.string`` stores the corresponding error message.

For example, to wait for a user to connect a camera you could do something like this:

.. code:: python

    import gphoto2 as gp
    ...
    print('Please connect and switch on your camera')
    while True:
        try:
            camera.init(context)
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                # no camera, try again in 2 seconds
                time.sleep(2)
                continue
            # some other error we can't handle here
            raise
        # operation completed successfully so exit loop
        break
    # continue with rest of program
    ...

When just calling a single function like this, it's probably easier to test the error value directly instead of using Python exceptions:

.. code:: python

    import gphoto2 as gp
    ...
    print('Please connect and switch on your camera')
    while True:
        error = gp.gp_camera_init(camera, context)
        if error >= gp.GP_OK:
            # operation completed successfully so exit loop
            break
        if error != gp.GP_ERROR_MODEL_NOT_FOUND:
            # some other error we can't handle here
            raise gp.GPhoto2Error(error)
        # no camera, try again in 2 seconds
        time.sleep(2)
    # continue with rest of program
    ...

Logging
^^^^^^^

The libgphoto2 library includes functions (such as ``gp_log()``) to output messages from its various functions.
These messages are mostly used for debugging purposes, and it can be helpful to see them when using libgphoto2 from Python.
The Python interface includes a ``use_python_logging()`` function to connect libgphoto2 logging to the standard Python logging system.
You should call ``use_python_logging()`` near the start of your program, as shown in the examples.

The libgphoto2 logging messages have four possible severity levels, each of which is mapped to a suitable Python logging severity.
You can override this mapping by passing your own to ``use_python_logging()``:

.. code:: python

    import logging
    import gphoto2 as gp
    ...
    gp.use_python_logging(mapping={
        gp.GP_LOG_ERROR   : logging.INFO,
        gp.GP_LOG_VERBOSE : logging.DEBUG,
        gp.GP_LOG_DEBUG   : logging.DEBUG - 3,
        gp.GP_LOG_DATA    : logging.DEBUG - 6})
    ...


Running SWIG
------------

SWIG is used to convert the ``.i`` interface definition files in ``src/gphoto2`` to ``.py`` and ``.c`` files.
These are then compiled to build the Python interface to libgphoto2.
The files downloaded from `PyPI <https://pypi.python.org/pypi/gphoto2>`_ include the SWIG generated files, but you may wish to regenerate them by running SWIG again (e.g. to test a new version of SWIG or of libgphoto2).
You will also need to run SWIG if you have downloaded the python-gphoto2 sources from GitHub instead of using PyPI.

The file ``setup.py`` defines an extra command to run SWIG.
It has no user options::

    python setup.py build_swig

By default this builds the interface for the version of libgphoto2 installed on your computer.
The interface files are created in the directory ``src/swig-gp2.x``, where ``x`` is the libgphoto2 sub-version (4 or 5 at present).

To build interfaces for additional versions (e.g. v2.4 as well as v2.5) you need to put a copy of that version's include (``.h``) files in a sub-directory of your working directory called ``include/gphoto2-2.x`` and then run ``setup.py`` again.

Licence
-------

python-gphoto2 - Python interface to libgphoto2
http://github.com/jim-easterbrook/python-gphoto2
Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk

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
