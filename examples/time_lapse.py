#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2018-22  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

"""Simple time lapse script.

This works OK with my Canon SLR, but will probably need changes to work
with another camera.

"""

from contextlib import contextmanager
import locale
import os
import subprocess
import sys
import time

import gphoto2 as gp


# time between captures
INTERVAL = 10.0
# temporary directory
WORK_DIR = '/tmp/time_lapse'
# result
OUT_FILE = 'time_lapse.mp4'


@contextmanager
def configured_camera():
    # initialise camera
    camera = gp.Camera()
    camera.init()
    try:
        # adjust camera configuratiuon
        cfg = camera.get_config()
        capturetarget_cfg = cfg.get_child_by_name('capturetarget')
        capturetarget = capturetarget_cfg.get_value()
        capturetarget_cfg.set_value('Internal RAM')
        # camera dependent - 'imageformat' is 'imagequality' on some
        imageformat_cfg = cfg.get_child_by_name('imageformat')
        imageformat = imageformat_cfg.get_value()
        imageformat_cfg.set_value('Small Fine JPEG')
        camera.set_config(cfg)
        # use camera
        yield camera
    finally:
        # reset configuration
        capturetarget_cfg.set_value(capturetarget)
        imageformat_cfg.set_value(imageformat)
        camera.set_config(cfg)
        # free camera
        camera.exit()


def empty_event_queue(camera):
    while True:
        type_, data = camera.wait_for_event(10)
        if type_ == gp.GP_EVENT_TIMEOUT:
            return
        if type_ == gp.GP_EVENT_FILE_ADDED:
            # get a second image if camera is set to raw + jpeg
            print('Unexpected new file', data.folder + data.name)


def main():
    locale.setlocale(locale.LC_ALL, '')
    if not os.path.exists(WORK_DIR):
        os.makedirs(WORK_DIR)
    template = os.path.join(WORK_DIR, 'frame%04d.jpg')
    next_shot = time.time() + 1.0
    count = 0
    with configured_camera() as camera:
        while True:
            try:
                empty_event_queue(camera)
                while True:
                    sleep = next_shot - time.time()
                    if sleep < 0.0:
                        break
                    time.sleep(sleep)
                path = camera.capture(gp.GP_CAPTURE_IMAGE)
                print('capture', path.folder + path.name)
                camera_file = camera.file_get(
                    path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
                camera_file.save(template % count)
                camera.file_delete(path.folder, path.name)
                next_shot += INTERVAL
                count += 1
            except KeyboardInterrupt:
                break
    subprocess.check_call(['ffmpeg', '-r', '25',
                           '-i', template, '-c:v', 'h264', OUT_FILE])
    for i in range(count):
        os.unlink(template % i)
    return 0


if __name__ == "__main__":
    sys.exit(main())
