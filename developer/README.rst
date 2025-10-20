Notes for developers
====================

The python interfaces can be built with any recent version of libgphoto2, but functions only present in later versions will not be accessible from python unless the interface is built with that later version. However, using this later version interface with an earlier version of libgphoto2 would normally result in undefined reference errors.

The solution is to include definitions of new functions in the interface to replace the proper versions when building for an older version of libgphoto2. See the camera.i interface file for an example.

The ``developer/build_swig.py`` script has one optional parameter: the installation directory of the version to be swigged. If this is omitted, the system installed libgphoto2 is used. For example::

    python3 developer/build_swig.py libgphoto2-2.5.28/local_install

Using local libgphoto2
----------------------

To build python-gphoto2 with a different version of libgphoto2 than the one installed on your system you first need to build a local copy of libgphoto2. Download and extract the libgphoto2 source, change to the source directory and then configure, build and install::

    ./configure --prefix=$PWD/local_install CFLAGS="-std=gnu99 -g -O2"
    make
    make install

Note the use of ``--prefix=$PWD/local_install`` to create a local copy, rather than a system installation.

Now you can build and install a package that includes your local copy of the libgphoto2 libs::

    GPHOTO2_ROOT=$PWD/libgphoto2-2.5.28/local_install pip install --user . -v

The ``GPHOTO2_ROOT`` environment variable tells setup.py to use the files in libgphoto2-2.5.28/local_install.
This value needs to be an absolute path.

Tracking libgphoto2 releases
----------------------------

When a new version of libgphoto2 is issued you should download it from https://sourceforge.net/projects/gphoto/files/libgphoto/ and run ``build_swig.py``. The Python3 script ``developer/compare_versions.py`` can be used to test if the swig generated files for two libgphoto2 versions differ.

If the only differences are the addition of some constants, then no changes to the SWIG sources are required. Other differences may require more work to accommodate. Once this is done the older version can usually be discarded.

Differences found so far::

    2.5.0     Base 2.5 version
    2.5.1-3   No change
    2.5.4     Add GP_MIME_ARW constant
    2.5.5     No change
    2.5.6     Add GP_MIME_TXT constant
    2.5.7-9   No change
    2.5.10    Add gp_camera_list_config, gp_camera_get_single_config & gp_camera_set_single_config functions and GP_MIME_NEF constant
    2.5.11-16 No change
    2.5.17    Add GP_EVENT_FILE_CHANGED enum
    2.5.18-22 No change
    2.5.23    Add GP_MIME_CR3 constant
    2.5.24    Add GP_PORT_IP enum
    2.5.25-27 No change
    2.5.28    Add gp_filesystem_set_info_dirty
    2.5.29    No change
    2.5.30    Add gp_init_localedir & gp_port_init_localedir functions
    2.5.31    No change
    2.5.32    Add GP_MIME_MPO, GP_MIME_QTKN, GP_MIME_QTKT, and GP_MIME_RAF constants
    2.5.33    No change

Documentation
-------------

The libgphoto2 source includes documentation in "doxygen" format.
If you install doxygen and doxy2swig (https://github.com/m7thon/doxy2swig) this documentation can be included in the python interfaces.
Clone the doxy2swig GitHub repos to your working directory, then run ``python3 developer/build_doc.py source_dir`` before running ``python3 developer/build_swig.py install_dir``.

Releases
--------

After uploading a new release to PyPI a GitHub tag and corresponding message can be created by running ``python3 developer/tag_release.py``. Only then should the python-gphoto2 version number be incremented.
