python-gphoto2 tests
====================

These test routines are not intended to test libgphoto2 itself (it has its own test suite) but should test that every python-gphoto2 function is callable and returns the expected result type and value.

There is one test file for each module in the python-gphoto2 package.
To run one test file, invoke it directly, for example::

    python -m unittest tests/test_camera.py -v

To run all the tests, use the Python unittest_ package's ``discover`` facility::

    python -m unittest discover tests


.. _unittest:            https://docs.python.org/3/library/unittest.html
