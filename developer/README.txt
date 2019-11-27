Notes for developers
====================

The python interfaces can be built with any version of libgphoto2, but functions only present in later versions will not be accessible from python unless the interface is built with that later version. However, using this later version interface with an earlier version of libgphoto2 would normally result in undefined reference errors.

The solution is to include definitions of new functions in the interface to replace the proper versions when building for an older version of libgphoto2. See the camera.i interface file for an example.

When running 'python3 setup.py build_swig' interfaces will be built for each version of libgphoto2 found in your python-gphoto2 working directory. When a new version of libgphoto2 is issued you should download it from https://sourceforge.net/projects/gphoto/files/libgphoto/ and run build_swig. The Python3 script developer/compare_versions.py can be used to test if the swig generated files for two libgphoto2 versions differ.

Once the interface source files have been modified to allow for anything added in the new version then it can be renamed (e.g. 2.5.23 -> 2.5) to become the new "master" version.

Differences found so far:

2.5.0  Base 2.5 version
2.5.1  No change
2.5.2  No change
2.5.3  No change
2.5.4  Add GP_MIME_ARW constant
2.5.5  No change
2.5.6  Add GP_MIME_TXT constant
2.5.7  No change
2.5.8  No change
2.5.9  No change
2.5.10 Add gp_camera_list_config, gp_camera_get_single_config &
       gp_camera_set_single_config functions and GP_MIME_NEF constant
2.5.11 No change
2.5.12 No change
2.5.13 No change
2.5.14 No change
2.5.15 No change
2.5.16 No change
2.5.17 Add GP_EVENT_FILE_CHANGED enum
2.5.18 No change
2.5.19 No change
2.5.20 No change
2.5.21 No change
2.5.22 No change
2.5.23 Add GP_MIME_CR3 constant

Documentation
-------------

The libgphoto2 source includes documentation in "doxygen" format. If you install doxygen and doxy2swig (https://github.com/m7thon/doxy2swig) this documentation can be included in the python interfaces. Clone the doxy2swig GitHub repos to your working directory, then run 'python3 setup.py build_doc' before running 'python3 setup.py build_swig'.
