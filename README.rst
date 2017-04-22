python-gphoto2
==============

python-gphoto2 is a comprehensive Python interface (or binding) to libgphoto2_.
It is built using SWIG_ to automatically generate the interface code.
This gives direct access to nearly all the libgphoto2_ functions, but sometimes in a rather un-Pythonic manner.

Other Python bindings to libgphoto2_ are available:
piggyphoto_ uses ctypes_ (included in standard Python installations) to interface to the library.
The gphoto2 source tree includes some `Python bindings`_ which also use ctypes_.
`gphoto2-cffi`_ uses cffi_.

.. contents::
   :backlinks: top

Dependencies
------------

*   Python: http://python.org/ version 2.6 or greater (including Python 3)
*   libgphoto2: http://www.gphoto.org/proj/libgphoto2/ version 2.4 or greater
*   build tools: pkg-config, C compiler & linker

Note that you need the "development headers" versions of libgphoto2_ and Python.
Most Linux distributions' package managers have these, but the names vary.
Look for ``libgphoto2-2-dev`` or ``libgphoto2-devel`` or something similar.

Installation and testing
------------------------

There are several ways to install python-gphoto2, with varying levels of control over the installation process.
You can install it with pip_, or by downloading an archive, or by getting the source from GitHub_.

The commands below will install python-gphoto2 for your default Python version.
To install for both Python 2 and Python 3, run the installation process twice with specific commands, i.e. ``pip2`` and ``pip3`` or ``python2`` and ``python3``.

Install with pip_
^^^^^^^^^^^^^^^^^

The easiest installation method is to use the pip_ command::

    sudo pip install -v gphoto2

Note that this may take longer than you expect as the package's modules are compiled during installation.
The ``-v`` option increases pip_'s verbosity so you can see that it's doing something.

Install a downloaded archive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Visit PyPI_ and download one of the zip or tar.gz files, then extract it and change to the new directory.
For example::

    tar xzf gphoto2-1.3.4.tar.gz
    cd gphoto2-1.3.4

Python's distutils_ are used to build and install python-gphoto2::

    python setup.py build
    sudo python setup.py install

Install from GitHub_ (SWIG_ required)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SWIG (http://swig.org/) should be installable via your operating system's package manager.
Note that this may be an older version of SWIG than the one used to generate the files on PyPI_.

To install the current development version, use git_ to "clone" the GitHub_ repository, then change to the new directory::

    git clone https://github.com/jim-easterbrook/python-gphoto2.git
    cd python-gphoto2

As before, Python's distutils_ are used to build and install python-gphoto2, but now you have to run SWIG_ first to generate the files to be compiled::

    python setup.py build_swig
    python setup.py build
    sudo python setup.py install

See "`running SWIG`_" below for more detail.

Testing
^^^^^^^

.. note:: If you installed with pip_ the example files should be in ``/usr/share/python-gphoto2/examples`` or ``/usr/local/share/python-gphoto2/examples`` or somewhere similar.
   Otherwise they are in the ``examples`` sub-directory of your source directory.

Connect a digital camera to your computer, switch it on, and try one of the example programs::

    python examples/camera-summary.py

If this works then you're ready to start using python-gphoto2.

Reinstalling
^^^^^^^^^^^^

If you update or move your installation of libgphoto2_ the Python gphoto2 package may fail to import one of the libgphoto2 shared object files.
If this happens you need to rebuild and reinstall the Python gphoto2 package::

    sudo pip install -v -U --force-reinstall gphoto2

if you installed with pip_, or ::

    rm -rf build
    python setup.py build
    sudo python setup.py install

if you installed from source.

Using python-gphoto2
--------------------

The Python interface to libgphoto2_ should allow you to do anything you could do in a C program.
However, there are still bits missing and functions that cannot be called from Python.
Let me know if you run into any problems.

The following paragraphs show how the Python interfaces differ from C.
See the example programs for typical usage of the Python gphoto2 API.

"C" interface
^^^^^^^^^^^^^

Using SWIG_ to generate the Python interfaces automatically means that every function in libgphoto2_ *should* be available to Python.
The ``pydoc`` command can be used to show the documentation of a function::

   jim@firefly ~/python-gphoto2 $ pydoc gphoto2.gp_camera_folder_list_files
   Help on built-in function gp_camera_folder_list_files in gphoto2:

   gphoto2.gp_camera_folder_list_files = gp_camera_folder_list_files(...)
       gp_camera_folder_list_files(Camera camera, char const * folder, Context context) -> int

       Lists the files in supplied `folder`.

       Parameters
       ----------
       * `camera` :
           a Camera
       * `folder` :
           a folder
       * `list` :
           a CameraList
       * `context` :
           a GPContext

       Returns
       -------
       a gphoto2 error code
   jim@firefly ~/python-gphoto2 $ 

Most of this text is copied from the "doxygen" format documentation in the C source code.
(The online `API documentation`_ shows how it is intended to look.)
Note that the function signature does not include the ``list`` parameter mentioned in the main text.
In C this is an "output" parameter, a concept that doesn't really exist in Python.
The Python version of ``gp_camera_folder_list_files`` returns a sequence containing the integer error code and the ``list`` value.

Most of the libgphoto2_ functions that use pointer parameters to return values in the C API have been adapted like this in the Python API.
(Unfortunately I've not found a way to persuade SWIG_ to include this extra return value in the documentation.
You should use ``pydoc`` to check the actual parameters expected by the Python function.)

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

Note that the gp_camera_unref() call is not needed.
It is called automatically when the Python camera object is deleted.

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

Many of the libgphoto2_ functions have been added as methods of the appropriate GPhoto2 object.
This allows GPhoto2 to be used in a more "Pythonic" style.
For example, ``gp.gp_camera_init(camera, context)`` can be replaced by ``camera.init(context)``.
These object methods also include error checking.
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

The object methods are more "hand crafted" than the rest of the Python bindings, which are automatically generated from the library header files.
This means that there may be some functions in the "C" interface that do not have corresponding object methods.

Error checking
^^^^^^^^^^^^^^

Most of the libgphoto2_ functions return an integer to indicate success or failure.
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

The libgphoto2_ library includes functions (such as ``gp_log()``) to output messages from its various functions.
These messages are mostly used for debugging purposes, and it can be helpful to see them when using libgphoto2_ from Python.
The Python interface includes a ``use_python_logging()`` function to connect libgphoto2_ logging to the standard Python logging system.
You should call ``use_python_logging()`` near the start of your program, as shown in the examples.

The libgphoto2_ logging messages have four possible severity levels, each of which is mapped to a suitable Python logging severity.
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

If you prefer to use your own logging system you can define a logging callback function in Python.
The function must take 3 parameters: ``level``, ``domain`` and ``string``.
Since python-gphoto2 version 1.3 the callback function is installed with ``gp_log_add_func`` (previously called ``gp_log_add_func_py``):

.. code:: python

    import gphoto2 as gp
    ...
    def callback(level, domain, string):
        print('Callback: level =', level, ', domain =', domain, ', string =', string)
    ...
    callback_id = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, callback))
    ...

Since python-gphoto2 version 1.4 you can pass some user data to your callback function (e.g. to log which thread an error occurred in):

.. code:: python

    import gphoto2 as gp
    ...
    def callback(level, domain, string, data=None):
        print('Callback: level =', level, ', domain =', domain, ', string =', string, 'data =', data)
    ...
    callback_id1 = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, callback))
    callback_id2 = gp.check_result(gp.gp_log_add_func(gp.GP_LOG_VERBOSE, callback, 123))
    ...

What to do if you have a problem
--------------------------------

If you find a problem in the Python gphoto2 interface (e.g. a segfault, a missing function, or a function without a usable return value) then please report it on the GitHub "issues" page (https://github.com/jim-easterbrook/python-gphoto2/issues) or email jim@jim-easterbrook.me.uk.

If your problem is more general, e.g. difficulty with capturing multiple images, then try doing what you want to do with the `gphoto2 command line program`_.
If the problem persists then it might be worth asking on the `gphoto-user mailing list`_.
Another reader of the mailing list may have the same camera model and already know what to do.

Notes on some gphoto2 functions
-------------------------------

gp_file_get_data_and_size / CameraFile.get_data_and_size
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since python-gphoto2 version 1.2.0 these functions return a ``FileData`` object that supports the `buffer protocol`_.
The data can be made accessible to Python (2.7 and 3.x) by using a memoryview_ object.
This allows the data to be used without copying.
See the ``copy-data.py`` example for typical usage.

In earlier versions of python-gphoto2 these functions returned a ``str`` (Python 2) or ``bytes`` (Python 3) object containing a copy of the data in the ``CameraFile`` object.

gp_camera_file_read / Camera.file_read / gp_file_slurp / CameraFile.slurp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Although the documentation says the ``buf`` parameter is of type ``char *`` you can pass any Python object that exposes a writeable buffer interface.
This allows you to read a file directly into a Python object without additional copying.
See the ``copy-chunks.py`` example which uses memoryview_ to expose a bytearray_.

gp_camera_wait_for_event / Camera.wait_for_event
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These functions return both the event type and the event data.
The data you get depends on the type.
``GP_EVENT_FILE_ADDED`` and ``GP_EVENT_FOLDER_ADDED`` events return a ``CameraFilePath``, others return ``None``.

Running SWIG_
-------------

SWIG_ is used to convert the ``.i`` interface definition files in ``src/gphoto2`` to ``.py`` and ``.c`` files.
These are then compiled to build the Python interface to libgphoto2_.
The files downloaded from PyPI_ include the SWIG_ generated files, but you may wish to regenerate them by running SWIG_ again (e.g. to test a new version of SWIG_ or of libgphoto2_).
You will also need to run SWIG_ if you have downloaded the python-gphoto2 sources from GitHub_ instead of using PyPI_.

The file ``setup.py`` defines an extra command to run SWIG_.
It has no user options::

    python setup.py build_swig

By default this builds the interface for the version of libgphoto2_ installed on your computer.
The interface files are created in directories with names like ``src/swig-bi-py3-gp2.5.0``.
This naming scheme allows for different versions of Python and libgphoto2_, and use (or not) of the `SWIG -builtin`_ flag.
The appropriate version is chosen when the interface is built.

To build interfaces for multiple versions of libgphoto2_ (e.g. v2.5.10 as well as v2.5.0) you need to put those versions' source files in your working directory and then run ``setup.py build_swig`` again.
More information about this is in the file ``developer/README.txt``.

Licence
-------

| python-gphoto2 - Python interface to libgphoto2
| http://github.com/jim-easterbrook/python-gphoto2
| Copyright (C) 2014-17  Jim Easterbrook  jim@jim-easterbrook.me.uk

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

.. _API documentation: http://www.gphoto.org/doc/api/
.. _buffer protocol:   https://docs.python.org/2/c-api/buffer.html
.. _bytearray:         https://docs.python.org/2/library/functions.html#bytearray
.. _cffi:              http://cffi.readthedocs.org/
.. _ctypes:            https://docs.python.org/2/library/ctypes.html
.. _distutils:         https://docs.python.org/2/library/distutils.html
.. _git:               http://git-scm.com/
.. _GitHub:            https://github.com/jim-easterbrook/python-gphoto2
.. _gphoto2-cffi:      https://github.com/jbaiter/gphoto2-cffi
.. _gphoto2 command line program:
                       http://gphoto.org/doc/manual/using-gphoto2.html
.. _gphoto-user mailing list:
                       http://gphoto.org/mailinglists/
.. _libgphoto2:        http://www.gphoto.org/proj/libgphoto2/
.. _memoryview:        https://docs.python.org/2/library/stdtypes.html#memoryview
.. _Python bindings:
   http://sourceforge.net/p/gphoto/code/HEAD/tree/trunk/bindings/libgphoto2-python/
.. _piggyphoto:        https://github.com/alexdu/piggyphoto
.. _pip:               https://pip.pypa.io/
.. _PyPI:              https://pypi.python.org/pypi/gphoto2/
.. _SWIG:              http://swig.org/
.. _SWIG -builtin:     http://www.swig.org/Doc3.0/Python.html#Python_builtin_types
