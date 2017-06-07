Notes for developers
====================

The python interfaces can be built with any version of libgphoto2, but functions only present in later versions will not be accessible from python unless the interface is built with that later version. However, using this later version interface with an earlier version of libgphoto2 will result in undefined reference errors.

The solution is to distribute a set of interfaces built with the versions of libgphoto2 that introduce new functions. Go to https://sourceforge.net/projects/gphoto/files/libgphoto/ and download the required sources, then extract them in to your python-gphoto2 working directory, e.g. the libgphoto2-2.5.0 directory should be in the same directory as the setup.py file.

When you run setup.py build_swig you should get a set of swig generated files for each of these sources. The Python3 script developer/compare_versions.py can be used to test if the swig generated files for two libgphoto2 versions differ.

Differences found so far:

2.4.0  Base 2.4 version
2.4.1  No change
2.4.2  No change
2.4.3  No change
2.4.4  No change
2.4.5  No change
2.4.6  Add GP_MIME_CR2 constant
2.4.7  No change
2.4.8  Add gp_widget_get_readonly & gp_widget_set_readonly functions and
       GP_EVENT_CAPTURE_COMPLETE constant
2.4.9  Add GPPortSettingsUsbDiskDirect and GPPortSettingsUsbScsi types
2.4.10 No change
2.4.11 Add GP_MIME_AVCHD constant
2.4.12 Add GP_MIME_RW2 constant
2.4.13 Minor change in gp_filesystem_get_folder arguments
2.4.14 No change

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

Where there is no change, or the change only adds a constant, the SWIG generated bindings from the later version can be used with an earlier version. E.g. version 2.5.9 can be used to generate bindings for any version from 2.5.0 onwards. You can rename the required source directories using the following mapping:

2.4.7  -> 2.4.0
2.4.14 -> 2.4.8
2.5.9  -> 2.5.0
2.5.14 -> 2.5.10

Documentation
-------------

The libgphoto2 source includes documentation in "doxygen" format. If you install doxygen and doxy2swig (https://github.com/m7thon/doxy2swig) this documentation can be included in the python interfaces. Clone the doxy2swig GitHub repos to your working directory, then run 'python setup.py build_doc' before running 'python setup.py build_swig'.
