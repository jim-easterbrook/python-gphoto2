#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2019-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This file is part of python-gphoto2.
#
# python-gphoto2 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# python-gphoto2 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with python-gphoto2.  If not, see
# <https://www.gnu.org/licenses/>.

from contextlib import contextmanager
from datetime import datetime
import locale
import logging
import os
import sys

import gphoto2 as gp

# Callback functions. These should have the function signatures shown
# (with an extra 'self' if they're class methods).

def cb_idle(context, data):
    print('cb_idle', data)

def cb_error(context, text, data):
    print('cb_error', text, data)

def cb_status(context, text, data):
    print('cb_status', text, data)

def cb_message(context, text, data):
    print('cb_message', text, data)

def cb_question(context, text, data):
    print('cb_question', text, data)
    return gp.GP_CONTEXT_FEEDBACK_OK

def cb_cancel(context, data):
    print('cb_cancel', data)
    return gp.GP_CONTEXT_FEEDBACK_OK

def cb_progress_start(context, target, text, data):
    print('cb_progress_start', target, text, data)
    return 123

def cb_progress_update(context, id_, current, data):
    print('cb_progress_update', id_, current, data)

def cb_progress_stop(context, id_, data):
    print('cb_progress_stop', id_, data)

# Using a Python contextmanager to ensure callbacks are deleted when the
# gphoto2 context is no longer required. This example uses every
# available callback. You probably don't need all of them.

@contextmanager
def context_with_callbacks():
    context = gp.Context()
    callbacks = []
    callbacks.append(context.set_idle_func(cb_idle, 'A'))
    callbacks.append(context.set_error_func(cb_error, 'B'))
    callbacks.append(context.set_status_func(cb_status, 'C'))
    callbacks.append(context.set_message_func(cb_message, 'D'))
    callbacks.append(context.set_question_func(cb_question, 'E'))
    callbacks.append(context.set_cancel_func(cb_cancel, 'F'))
    callbacks.append(context.set_progress_funcs(
        cb_progress_start, cb_progress_update, cb_progress_stop, 'G'))
    try:
        yield context
    finally:
        del callbacks

def list_files(camera, context, path='/'):
    result = []
    # get files
    for name, value in camera.folder_list_files(path, context):
        result.append(os.path.join(path, name))
    # read folders
    folders = []
    for name, value in camera.folder_list_folders(path, context):
        folders.append(name)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, context, os.path.join(path, name)))
    return result

# Perform a few simple operations on a camera after setting up
# callbacks.

# I don't get many callbacks with my Canon cameras, just progress update
# and 'cancel' during camera.init while the drivers are loaded, and
# 'cancel' when listing the files. Maybe other camera drivers make more
# use of them.

def main():
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())
    with context_with_callbacks() as context:
        camera = gp.Camera()
        print('camera.init')
        camera.init(context)
        print('camera.get_summary')
        text = camera.get_summary(context)
        print('camera.get_config')
        config = camera.get_config(context)
        print('list_files')
        files = list_files(camera, context)
        camera.exit(context)
    return 0

if __name__ == "__main__":
    sys.exit(main())
