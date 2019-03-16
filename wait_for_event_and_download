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
# *******************************************************

def main():

    # Init camera
    camera = gp.check_result(gp.gp_camera_new())
    gp.check_result(gp.gp_camera_init(camera))

    while(True):
        result,image_file = gp.check_result(gp.gp_camera_wait_for_event(camera,gp.GP_EVENT_FILE_ADDED))
        if (result == gp.GP_EVENT_FILE_ADDED):
            # Get the image from the camera
            camera_file = gp.check_result(gp.gp_camera_file_get(
                                            camera, 
                                            image_file.folder, 
                                            image_file.name,
                                            gp.GP_FILE_TYPE_NORMAL))
            # Path where the image is to be saved
            target_path= os.path.join(os.getcwd(),image_file.name)
            print("Picture is saved to {}".format(target_path))
            gp.gp_file_save(camera_file, target_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
