Installation
============

There are several different ways to install `python-gphoto2`_.
This allows you to use different versions of libgphoto2_.
The following instructions apply to python-gphoto2 v2.3.5 and later.

.. contents::
   :backlinks: top

"Binary wheel"
--------------

Since python-gphoto2 v2.3.1 "binary wheels" are provided for many Linux and MacOS computers.
These include a recent version of the libgphoto2_ libraries, and pre-built Python interface modules, which makes installation quick and easy.
Use pip_'s ``--only-binary`` option to install one of these wheels::

    $ pip3 install gphoto2 --user --only-binary :all:
    Collecting gphoto2
      Downloading gphoto2-2.3.5-cp36-cp36m-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (6.3 MB)
         |████████████████████████████████| 6.3 MB 953 kB/s            
    Installing collected packages: gphoto2
    Successfully installed gphoto2-2.3.5

You can test your installation by running python-gphoto2 as a module::

    $ python3 -m gphoto2
    python-gphoto2 version: 2.3.5
    libgphoto2 version: 2.5.30, standard camlibs, gcc, no ltdl, EXIF
    libgphoto2_port version: 0.12.1, iolibs: disk ptpip serial usb usbdiskdirect usbscsi, gcc, no ltdl, EXIF, USB, serial without locking
    python-gphoto2 examples: /home/jim/.local/lib/python3.6/site-packages/gphoto2/examples

This shows you the version numbers of python-gphoto2 & libgphoto2, and where to find the python-gphoto2 example files.

If the installation fails it is most likely because none of the available wheels is compatible with your computer.
In this case you *must* install the dependencies_ listed below before installing python-gphoto2.

Raspberry Pi
^^^^^^^^^^^^

Binary wheels for the Raspberry Pi are available from piwheels_.
You still need to install some system packages to use these::

    $ sudo apt install libgphoto2-6 libgphoto2-port12 libexif12 libltdl7
    $ pip3 install gphoto2 --user --only-binary :all:

See the piwheels site for more information.

Dependencies
------------

*   Python: http://python.org/ version 3.6 or greater
*   libgphoto2: http://www.gphoto.org/proj/libgphoto2/ version 2.5.10 or greater
*   build tools: `pkg-config`_, C compiler & linker

In most cases you should use your operating system's package manager to install these.
Note that you need the "development headers" for libgphoto2_ and Python.
On some systems these are included in the base package, but on others they need to be installed separately.
Search for ``libgphoto2-dev`` or ``libgphoto2-devel`` or something similar.
Test your installation with the ``pkg-config`` command::

    $ pkg-config --modversion libgphoto2 python3
    2.5.27
    3.6

"System" libgphoto2
-------------------

This downloads python-gphoto2 from PyPI_ and compiles it with the libgphoto2_ installed on your computer.
Note the use of ``--no-binary`` to prevent installation from a binary wheel::

    $ pip3 install gphoto2 --user --no-binary :all:
    Collecting gphoto2
      Downloading gphoto2-2.3.5.tar.gz (583 kB)
         |████████████████████████████████| 583 kB 954 kB/s            
      Preparing metadata (setup.py) ... done
    Skipping wheel build for gphoto2, due to binaries being disabled for it.
    Installing collected packages: gphoto2
        Running setup.py install for gphoto2 ... done
    Successfully installed gphoto2-2.3.5
    $ python3 -m gphoto2
    python-gphoto2 version: 2.3.5
    libgphoto2 version: 2.5.27, standard camlibs (SKIPPING lumix), gcc, ltdl, EXIF
    libgphoto2_port version: 0.12.0, iolibs: disk ptpip serial usb1 usbdiskdirect usbscsi, gcc, ltdl, EXIF, USB, serial lockdev locking
    python-gphoto2 examples: /home/jim/.local/lib/python3.6/site-packages/gphoto2/examples

This installation may take longer than you expect as the package's modules are compiled during installation.
You can use pip_'s ``-v`` option to increase verbosity so you can see that it's doing something.

Using the "system" libgphoto2 guarantees compatibility with other operating system packages, but it may not be the latest version of libgphoto2.
If the system libgphoto2 is uninstalled than python-gphoto2 will stop working.

"Local" libgphoto2
------------------

If your system libgphoto2 is an old version you can try downloading and building a more recent version, then using it with python-gphoto2.
Follow the "download" link on the libgphoto2_ site, then choose a version and download an archive file (``tar.xz``, ``tar.gz``, or ``tar.bz2``).
After extracting the files, change to the new libgphoto2 directory then configure and build in the usual way::

    $ ./configure --prefix=$HOME/.local
    $ make
    $ make install

Note the use of ``--prefix=$HOME/.local`` to set the installation directory.
This can be any directory you like, but should not be a system directory such as ``/usr``.

The ``configure`` script has options to choose different camera drivers, which may be useful if you have an old camera that you would like to use.
You can list the options with ``./configure -h``.

To use this local installation of libgphoto2 with python-gphoto2 you set the ``GPHOTO2_ROOT`` environment variable when installing python-gphoto2::

    $ GPHOTO2_ROOT=$HOME/.local pip3 install gphoto2 --user --no-binary :all:
    Collecting gphoto2
      Using cached gphoto2-2.3.5.tar.gz (583 kB)
      Preparing metadata (setup.py) ... done
    Skipping wheel build for gphoto2, due to binaries being disabled for it.
    Installing collected packages: gphoto2
        Running setup.py install for gphoto2 ... done
    Successfully installed gphoto2-2.3.5
    $ python3 -m gphoto2
    python-gphoto2 version: 2.3.5
    libgphoto2 version: 2.5.30, standard camlibs, gcc, no ltdl, EXIF
    libgphoto2_port version: 0.12.1, iolibs: disk ptpip serial usb1 usbdiskdirect usbscsi, gcc, no ltdl, EXIF, USB, serial without locking
    python-gphoto2 examples: /home/jim/.local/lib/python3.6/site-packages/gphoto2/examples

Running SWIG
------------

Most users should not need to use SWIG_ to install python-gphoto2, unless you need to test a new version of SWIG or modify the Python gphoto2 interface.

SWIG should be installable via your operating system's package manager.
Note that this may be an older version of SWIG than the one used to generate the files on PyPI_.

You can download the python-gphoto2 source files from the GitHub releases_ page or you can use git_ to "clone" the GitHub_ repository::

    $ git clone https://github.com/jim-easterbrook/python-gphoto2.git
    $ cd python-gphoto2

The ``developer`` directory includes a script to run SWIG_.
It has one optional parameter: the installation prefix of the version to be swigged::

    $ python3 developer/build_swig.py $HOME/.local

Omitting the parameter uses the system installation::

    $ python3 developer/build_swig.py

This builds the interface for the version of libgphoto2_ installed on your computer.
The interface files are created in directories with names like ``src/swig-gp2_5_18``.
This naming scheme allows for different versions of libgphoto2_.
The most appropriate version is chosen when the interface is built.

As before, pip_ is used to build and install python-gphoto2::

    $ GPHOTO2_ROOT=$HOME/.local pip3 install --user -v .

Documentation
-------------

The libgphoto2 source includes documentation in "doxygen" format.
If you install doxygen and doxy2swig_ this documentation can be included in the python interfaces.
Clone the doxy2swig GitHub repos to your working directory, then use ``developer/build_doc.py`` to convert the docs to SWIG format before running SWIG::

    $ python3 developer/build_doc.py $HOME/libgphoto2-2.5.30
    $ python3 developer/build_swig.py $HOME/.local

Note that ``build_doc.py`` needs the source directory of libgphoto2, not its installation root.
The libgphoto2 docs are in the C source files.

.. _doxy2swig:         https://github.com/m7thon/doxy2swig
.. _git:               http://git-scm.com/
.. _GitHub:            https://github.com/jim-easterbrook/python-gphoto2
.. _libgphoto2:        http://www.gphoto.org/proj/libgphoto2/
.. _pip:               https://pip.pypa.io/
.. _piwheels:          https://www.piwheels.org/project/gphoto2/
.. _pkg-config:        https://en.wikipedia.org/wiki/Pkg-config
.. _python-gphoto2:    https://pypi.org/project/gphoto2/
.. _PyPI:              https://pypi.python.org/pypi/gphoto2/
.. _releases:          https://github.com/jim-easterbrook/python-gphoto2/releases
.. _setuptools:        https://pypi.org/project/setuptools/
.. _SWIG:              http://swig.org/
