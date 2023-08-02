python-gphoto2 tests
====================

These test routines are not intended to test libgphoto2 itself (it has its own test suite) but should test that every python-gphoto2 function is callable and returns the expected result type and value.

There is one test file for each module in the python-gphoto2 package.
To run one test file, invoke it directly, for example::

    python -m unittest tests/test_camera.py -v

If this fails with a message like ``ModuleNotFoundError: No module named 'tests.test_camera'`` then it's possible you have a package called ``tests`` in one of your Python site-packages directories.
`python-oauth2`_ is one package I know of that installs a separate ``tests`` package.

To run all the tests, use the Python unittest_ package's ``discover`` facility::

    python -m unittest discover tests


.. _python-oauth2:       https://pypi.org/project/oauth2/
.. _unittest:            https://docs.python.org/3/library/unittest.html
