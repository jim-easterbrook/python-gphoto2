#!/usr/bin/env python

import gphoto2 as gp 
import os
import sys
# *******************************************************
# gp.camera_wait_for_event() function waits for 
# a capture trigger to arrive. When it does, it downloads
# the image directly from the camera, without using SD 
# card
# 
# gp_camera_trigger_capture() or Trigger Button on the
# camera can be used to start capturing.
# 
# gp_capture_image_and_download() method takes about 2 seconds
# to process since it saves the image to SD CARD 
# first then downloads it, which takes a lot of time.
#
# "object oriented" version of wait-for-event.py  
# *******************************************************

def main():

    # Init camera
    camera = gp.Camera()
    camera.init()
    timeout = 3000 # miliseconds
    while(True):
        result,img = camera.wait_for_event(timeout)
        if(result == gp.GP_EVENT_FILE_ADDED):
            _,cam_file = gp.gp_camera_file_get(camera,img.folder,img.name,gp.GP_FILE_TYPE_NORMAL)
            target_path = os.path.join(os.getcwd(),img.name)
            print("Image is being saved to {}".format(target_path))
            gp.gp_file_save(cam_file,target_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
