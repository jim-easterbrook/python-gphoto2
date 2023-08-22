#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2019  "sdaau"
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

# another camera config gui, with load/save settings to file, and live view
# started: sdaau 2019, on with python3-gphoto2 and `sudo -H pip2 install gphoto2`, Ubuntu 18.04
# uses camera-config-gui.py, and code from focus-gui.py, time_lapse.py

"""
NOTE that properties are reported by the camera, depending on the camera state! On Canon S3 IS:
For instance, if camera is not in capture mode, then upon --save-cam-conf-json, the properties "imgsettings" and "capturesettings" (which otherwise contain other properties as children) will return error.
If camera is in capture mode, and prop "shootingmode" is "Auto" - then "iso" has "Auto" option, "exposurecompensation" and "flashcompensation" is read-write, "aperture" and "shutterspeed" is read-only
If camera is in capture mode, and prop "shootingmode" is "Manual" - then "iso" loses "Auto" option, "exposurecompensation" and "flashcompensation" become read-only, "aperture" and "shutterspeed" become read-write
NOTE: some properties may take a while to update, see [waiting for variables to update, and wait_for_event causing picture to be taken? · Issue #75 · jim-easterbrook/python-gphoto2 · GitHub](https://github.com/jim-easterbrook/python-gphoto2/issues/75)
Upon loading json files on camera that change some modes, you might get an error, in which case you can try loading the same file again
NOTE: if doing live view on Canon, while capture=0, then still an image is returned - but it is the last captured image (except if immediately after camera startup, when capture=0 is ignored, and live view captures regardless). However, sometimes live view may freeze even with capture=1 - in which case, switching Camera Output from Off to LCD/Video Out and back to Off helps.
NOTE: Switching from viewing full res image capture, to lower resolution live view preview, and vice versa, should automatically fit the view. But if the view gets "lost": in that case, hit Ctrl-F for fit to view once, then can do Ctrl-Z for original scale (or mouse wheel to zoom in/out the preview).
"""

import io
import locale
import logging
import math
import sys, os
import re
import argparse
import json, codecs
from collections import OrderedDict
from datetime import datetime
import time
import tzlocal # sudo -H pip install tzlocal # pip2, pip3
my_timezone = tzlocal.get_localzone()

from PIL import Image, ImageDraw, ImageFont

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog

import gphoto2 as gp

THISSCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1,THISSCRIPTDIR)
ccgoo = __import__('camera-config-gui')
NOCAMIMG = "cam-conf-no-cam.png"
APPNAME = "cam-conf-view-gui.py"

patTrailDigSpace = re.compile(r'(?<=\.)(\d+?)(0+)(?=[^\d]|$)') # SO: 32348435

# blacklist by properties' names, since on a Canon S3 IS, serialnumber etc are read-write
# make it react by regex too, as on a Canon S3 IS there is read-write:
# 'd04a' = '0' (PTP Property 0xd04a)), 'd034' = '1548282664' (UNIX Time)) ...
# which should likely not be changed; most of ^d0.* properties are read-only or duplicates,
# but still good to ignore them all in one go:
BLACKLISTPROPSREGEX = [
    'opcode', 'datetime', 'serialnumber', 'manufacturer', 'cameramodel', 'deviceversion', 'vendorextension', r'^d0'
]
BLACKLISTPROPSREGEX = [re.compile(x) for x in BLACKLISTPROPSREGEX]

PROPNAMESTOSETFIRST = [ "shootingmode" ]
MINFPS=0.5 # just for the text in status bar
SLEEPWAITCHANGE=2 # amount of seconds to wait for variable update after first pass, when loading json file

def get_camera_model(camera_config):
    # get the camera model
    OK, camera_model = gp.gp_widget_get_child_by_name(
        camera_config, 'cameramodel')
    if OK < gp.GP_OK:
        OK, camera_model = gp.gp_widget_get_child_by_name(
            camera_config, 'model')
    if OK >= gp.GP_OK:
        camera_model = camera_model.get_value()
    else:
        camera_model = ''
    return camera_model

def get_gphoto2_CameraWidgetType_string(innumenum):
    switcher = {
        0: "GP_WIDGET_WINDOW",
        1: "GP_WIDGET_SECTION",
        2: "GP_WIDGET_TEXT",
        3: "GP_WIDGET_RANGE",
        4: "GP_WIDGET_TOGGLE",
        5: "GP_WIDGET_RADIO",
        6: "GP_WIDGET_MENU",
        7: "GP_WIDGET_BUTTON",
        8: "GP_WIDGET_DATE"
    }
    return switcher.get(innumenum, "Invalid camwidget type")

class PropCount(object):
    def __init__(self):
        self.numro = 0
        self.numrw = 0
        self.numtot = 0
        self.numexc = 0
    def __str__(self):
        return "{},{},{},{}".format(self.numtot,self.numrw,self.numro,self.numexc)

def get_formatted_ts(inunixts=None):
    if inunixts is None:
        unixts = time.time()
    else:
        unixts = inunixts
    unixts = round(unixts,6)
    tzlocalts = tzlocal.get_localzone().localize(datetime.utcfromtimestamp(unixts), is_dst=None).replace(microsecond=0)
    isots = tzlocalts.isoformat(' ')
    fsuffts = tzlocalts.strftime('%Y%m%d_%H%M%S') # file suffix timestamp
    return (unixts, isots, fsuffts)

def get_stamped_filename(infilename, inunixts):
    unixts, isots, fsuffts = get_formatted_ts( inunixts )
    outfilename = re.sub(r"_\d{8}_\d{6}", "", infilename) # remove any of our timestamps
    # "split" at first period (if any), and insert (or append) our timestamp there:
    outfilename = re.sub(r'^([^.\n]*)([.]*)(.*)$', r'\1_'+fsuffts+r'\2\3', outfilename)
    return outfilename

def get_camera_config_children(childrenarr, savearr, propcount):
    for child in childrenarr:
        tmpdict = OrderedDict()
        propcount.numtot += 1
        if child.get_readonly():
            propcount.numro += 1
        else:
            propcount.numrw += 1
        tmpdict['idx'] = str(propcount)
        tmpdict['ro'] = child.get_readonly()
        tmpdict['name'] = child.get_name()
        tmpdict['label'] = child.get_label()
        tmpdict['type'] = child.get_type()
        tmpdict['typestr'] = get_gphoto2_CameraWidgetType_string( tmpdict['type'] )
        if ((tmpdict['type'] == gp.GP_WIDGET_RADIO) or (tmpdict['type'] == gp.GP_WIDGET_MENU)):
            tmpdict['count_choices'] = child.count_choices()
            tmpchoices = []
            for choice in child.get_choices():
                tmpchoices.append(choice)
            tmpdict['choices'] = ",".join(tmpchoices)
        if (child.count_children() > 0):
            tmpdict['children'] = []
            get_camera_config_children(child.get_children(), tmpdict['children'], propcount)
        else:
            # NOTE: camera HAS to be "into preview mode to raise mirror", otherwise at this point can get "gphoto2.GPhoto2Error: [-2] Bad parameters" for get_value
            try:
                tmpdict['value'] = child.get_value()
            except Exception as ex:
                tmpdict['value'] = "{} {}".format( type(ex).__name__, ex.args)
                propcount.numexc += 1
        savearr.append(tmpdict)

def get_camera_config_object(camera_config, inunixts=None):
    retdict = OrderedDict()
    retdict['camera_model'] = get_camera_model(camera_config)
    if inunixts is None: myunixts = time.time()
    else: myunixts = inunixts
    unixts, isots, fsuffts = get_formatted_ts( myunixts )
    retdict['ts_taken_on'] = unixts
    retdict['date_taken_on'] = isots
    propcount = PropCount()
    retarray = []
    retdict['children'] = []
    get_camera_config_children(camera_config.get_children(), retdict['children'], propcount)
    excstr = "no errors - OK." if (propcount.numexc == 0) else "{} errors - bad (please check if camera mirror is up)!".format(propcount.numexc)
    print("Parsed camera config: {} properties total, of which {} read-write and {} read-only; with {}".format(propcount.numtot, propcount.numrw, propcount.numro, excstr))
    return retdict

def put_camera_capture_preview_mirror(camera, camera_config, camera_model):
    if camera_model == 'unknown':
        # find the capture size class config item
        # need to set this on my Canon 350d to get preview to work at all
        OK, capture_size_class = gp.gp_widget_get_child_by_name(
            camera_config, 'capturesizeclass')
        if OK >= gp.GP_OK:
            # set value
            value = capture_size_class.get_choice(2)
            capture_size_class.set_value(value)
            # set config
            camera.set_config(camera_config)
    else:
        # put camera into preview mode to raise mirror
        ret = gp.gp_camera_capture_preview(camera) # OK, camera_file
        #print(ret) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]

def start_capture_view():
    camera = gp.Camera()
    hasCamInited = False
    try:
        camera.init() # prints: WARNING: gphoto2: (b'gp_context_error') b'Could not detect any camera' if logging set up
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
    if hasCamInited:
        camera_config = camera.get_config()
        camera_model = get_camera_model(camera_config)
        put_camera_capture_preview_mirror(camera, camera_config, camera_model)
        print("Started capture view (extended lens/raised mirror) on camera: {}".format(camera_model))
        sys.exit(0)
    else: # camera not inited
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)

def stop_capture_view():
    camera = gp.Camera()
    hasCamInited = False
    try:
        camera.init()
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
    if hasCamInited:
        camera_config = camera.get_config()
        camera_model = get_camera_model(camera_config)
        # https://github.com/gphoto/gphoto2/issues/195
        OK, capture = gp.gp_widget_get_child_by_name( camera_config, 'capture' )
        if OK >= gp.GP_OK:
            capture.set_value(0)
            camera.set_config(camera_config)
        print("Stopped capture view (retracted lens/released mirror) on camera: {} ({} {})".format(camera_model, OK, capture))
        sys.exit(0)
    else: # camera not inited
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)

# mostly from time_lapse.py (_send_file is from focus-gui.py)
def do_capture_image(camera):
    # adjust camera configuratiuon
    cfg = camera.get_config()
    capturetarget_cfg = cfg.get_child_by_name('capturetarget')
    capturetarget = capturetarget_cfg.get_value()
    capturetarget_cfg.set_value('Internal RAM')
    camera.set_config(cfg)
    # do capture
    path = camera.capture(gp.GP_CAPTURE_IMAGE)
    print('capture cam path: {} {}'.format(path.folder, path.name))
    camera_file = camera.file_get(
        path.folder, path.name, gp.GP_FILE_TYPE_NORMAL)
    # saving of image implied in current directory:
    camera_file.save(path.name)
    camera.file_delete(path.folder, path.name)
    # reset configuration
    capturetarget_cfg.set_value(capturetarget)
    camera.set_config(cfg)
    return path.name


def get_json_filters(args):
    jsonfilters = []
    if hasattr(args, 'include_names_json'):
        splitnames = args.include_names_json.split(",")
        for iname in splitnames:
            splitnameeq = iname.split("=") # 1-element array if = not present; 2-element array if present
            splitnameeq = list(filter(None, splitnameeq))
            jsonfilters.append(splitnameeq)
    jsonfilters = list(filter(None, jsonfilters))
    return jsonfilters

def copy_json_filter_props(inarr, outarr, inpropcount, outpropcount, jsonfilters):
    for inchild in inarr:
        inpropcount.numtot += 1
        if inchild['ro'] == 1:
            inpropcount.numro += 1
        else:
            inpropcount.numrw += 1
        shouldCopy = False
        if len(jsonfilters)>0:
            for jfilter in jsonfilters:
                if len(jfilter) == 2:
                    key = jfilter[0] ; val = jfilter[1]
                    if ( str(inchild[key]) == val ):
                        shouldCopy = True
                elif len(jfilter) == 1:
                    if inchild["name"] == jfilter[0]:
                        shouldCopy = True
        else: # len(jsonfilters) == 0: ; no filters, pass everything
            shouldCopy = True
        # copy with flatten hierarchy - only copy dicts that have 'value' (else they have 'children'):
        if ( ('value' in inchild.keys()) and (inchild['value'] is not None) ):
            if shouldCopy:
                outpropcount.numtot += 1
                if inchild['ro'] == 1:
                    outpropcount.numro += 1
                else:
                    outpropcount.numrw += 1
                if 'Error' in str(inchild['value']):
                    outpropcount.numexc += 1
                outarr.append(inchild)
        else: # if the child dict has no 'value' then it has 'children'
            if 'children' in inchild.keys():
                copy_json_filter_props(inchild['children'], outarr, inpropcount, outpropcount, jsonfilters)


def do_GetSaveCamConfJson(camera, jsonfile, inunixts=None):
    camera_config = camera.get_config() # may print: WARNING: gphoto2: (b'_get_config [config.c:7649]') b"Type of property 'Owner Name' expected: 0x4002 got: 0x0000"
    camconfobj = get_camera_config_object(camera_config, inunixts)
    with open(jsonfile, 'wb') as f:
        json.dump(camconfobj, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=2, separators=(',', ': '))
    print("Saved config to {}".format(jsonfile))


def getSaveCamConfJson(args):
    if (not(args.save_cam_conf_json)):
        print("getSaveCamConfJson: Sorry, unusable/empty output .json filename; aborting")
        sys.exit(1)
    jsonfile = os.path.realpath(args.save_cam_conf_json)
    print("getSaveCamConfJson: saving to {}".format(jsonfile))
    camera = gp.Camera()
    hasCamInited = False
    try:
        camera.init()
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
    if hasCamInited:
        do_GetSaveCamConfJson(camera, jsonfile)
        print("Exiting.")
        sys.exit(0)
    else: # camera not inited
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)

def copyFilterCamConfJson(args):
    if (not(args.load_cam_conf_json) or not(args.save_cam_conf_json)):
        print("copyFilterCamConfJson: Sorry, unusable/empty input or output .json filename; aborting")
        sys.exit(1)
    injsonfile = os.path.realpath(args.load_cam_conf_json)
    outjsonfile = os.path.realpath(args.save_cam_conf_json)
    print("loadSetCamConfJson: input load from {}, output save to {}".format(injsonfile, outjsonfile))
    # no need for camera here
    # open and parse injsonfile as object
    with open(injsonfile) as in_data_file:
        indatadict = json.load(in_data_file, object_pairs_hook=OrderedDict)
    # check filters
    jsonfilters = get_json_filters(args)
    jsonfilterslen = len(jsonfilters)
    if jsonfilterslen > 0:
        print("Got {} json filters; including only properties names(/values) in filters in output file".format(jsonfilterslen))
    else:
        print("Got no ({}) json filters; copying input (flattened) to output file".format(jsonfilterslen))
    retdict = OrderedDict()
    retdict['camera_model'] = indatadict['camera_model']
    retdict['orig_ts_taken_on'] = indatadict['ts_taken_on']
    retdict['orig_date_taken_on'] = indatadict['date_taken_on']
    unixts, isots, fsuffts = get_formatted_ts( time.time() )
    retdict['ts_taken_on'] = unixts
    retdict['date_taken_on'] = isots
    inpropcount = PropCount()
    outpropcount = PropCount()
    retdict['children'] = []
    copy_json_filter_props(indatadict['children'], retdict['children'], inpropcount, outpropcount, jsonfilters)
    print("Processed input props: {} ro, {} rw, {} total; got output props: {} ro, {} rw, {} total".format(
        inpropcount.numro, inpropcount.numrw, inpropcount.numtot, outpropcount.numro, outpropcount.numrw, outpropcount.numtot
    ))
    # save
    with open(outjsonfile, 'wb') as f:
        json.dump(retdict, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=2, separators=(',', ': '))
    print("Saved filtered copy to output file {}".format(outjsonfile))
    sys.exit(0)

def do_LoadSetCamConfJson(camera, injsonfile):
    camera_config = camera.get_config()
    # open and parse injsonfile as object
    with open(injsonfile) as in_data_file:
        indatadict = json.load(in_data_file, object_pairs_hook=OrderedDict)
    print("Getting flattened object (removes hierarchy/nodes with only children and without value) from {} ...".format(injsonfile))
    inpropcount = PropCount()
    outpropcount = PropCount()
    jsonfilters = [] # empty here
    flatproparray = []
    copy_json_filter_props(indatadict['children'], flatproparray, inpropcount, outpropcount, jsonfilters)
    print("Flattened {} ro, {} rw, {} total input props to: {} ro, {} rw, {} total flat props".format(
        inpropcount.numro, inpropcount.numrw, inpropcount.numtot, outpropcount.numro, outpropcount.numrw, outpropcount.numtot
    ))
    print("Applying at most {} read/write props (ignoring {} read-only ones, out of {} total props) to camera:".format(
        outpropcount.numrw, outpropcount.numro, len(flatproparray)
    ))
    numappliedprops = 0
    usedlabels = [] ; usednames = []
    # NOTE - some of the camera properties depend on others;
    # say for shootingmode=Manual, some vars are r/w, but for shootingmode=Auto, same vars become r/o
    # thus we split off flatproparray in two parts, executed first the one, then the other
    flatproparrayfirst = []
    for iname in PROPNAMESTOSETFIRST: # SO: 54343917
        # find the object having the name iname
        foundidx = -1
        for ix, idict in enumerate(flatproparray):
            if idict.get('name') == iname:
                foundidx = ix
                break
        if foundidx > -1:
            # remove dict object via pop at index, save removed object
            remdict = flatproparray.pop(foundidx)
            # add removed object to newarr:
            flatproparrayfirst.append(remdict)
    print("First pass (of applying cam settings):")
    usednamesfirst = []
    passedpropsfirst = 0
    # no need to check duplicates or blacklisted here:
    for ix, tprop in enumerate(flatproparrayfirst):
        if tprop['ro'] == 1:
            print(" {:3d}: (ignoring read-only prop '{}' ({}))".format(ix+1, tprop['name'], tprop['label'] ))
        else:
            numappliedprops += 1
            print(" {:3d}: Applying prop {}/{}: '{}' = '{}' ({}))".format(ix+1, numappliedprops, outpropcount.numrw, tprop['name'], tprop['value'], tprop['label']))
            usedlabels.append(tprop['label'])
            usednamesfirst.append(tprop['name'])
            OK, gpprop = gp.gp_widget_get_child_by_name( camera_config, "{}".format(tprop['name']) )
            if OK >= gp.GP_OK:
                if ( type(tprop['value']).__name__ == "unicode" ):
                    gpprop.set_value( "{}".format(tprop['value']) )
                else:
                    gpprop.set_value( tprop['value'] )
        passedpropsfirst = ix+1
    print("  applying props: {}.".format(",".join(usednamesfirst)))
    camera.set_config(camera_config)
    # sleeping for 5 sec seems enough to allow changes between auto and manual shootingmode, without taking a picture... but 1 sec is not; 2 seems enough..
    time.sleep(SLEEPWAITCHANGE)
    print("Second pass (of applying cam settings):")
    for ix, tprop in enumerate(flatproparray):
        propnum = passedpropsfirst + ix + 1
        if tprop['ro'] == 1:
            print(" {:3d}: (ignoring read-only prop '{}' ({}))".format(propnum, tprop['name'], tprop['label'] ))
        # only look for exact duplicates - rest, if needed, can be blacklisted:
        elif ( tprop['label'] in usedlabels ):
            print(" {:3d}: (ignoring duplicate label prop '{}' ({}))".format(propnum, tprop['name'], tprop['label'] ))
        elif ( any([pat.match(tprop['name']) for pat in BLACKLISTPROPSREGEX]) ):
            print(" {:3d}: (ignoring blacklisted name prop '{}' ({}))".format(propnum, tprop['name'], tprop['label'] ))
        else:
            numappliedprops += 1
            print(" {:3d}: Applying prop {}/{}: '{}' = '{}' ({}))".format(propnum, numappliedprops, outpropcount.numrw, tprop['name'], tprop['value'], tprop['label']))
            usedlabels.append(tprop['label'])
            usednames.append(tprop['name'])
            OK, gpprop = gp.gp_widget_get_child_by_name( camera_config, "{}".format(tprop['name']) )
            if OK >= gp.GP_OK:
                if ( type(tprop['value']).__name__ == "unicode" ):
                    gpprop.set_value( "{}".format(tprop['value']) )
                else:
                    gpprop.set_value( tprop['value'] )
    print("  applying props: {} (+ {}).".format( ",".join(usednames), ",".join(usednamesfirst) ))
    camera.set_config(camera_config)
    print("Applied {} properties from file {} to camera.".format(numappliedprops, injsonfile))

def loadSetCamConfJson(args):
    if (not(args.load_cam_conf_json)):
        print("loadSetCamConfJson: Sorry, unusable/empty output .json filename; aborting")
        sys.exit(1)
    injsonfile = os.path.realpath(args.load_cam_conf_json)
    print("loadSetCamConfJson: loading from {}".format(injsonfile))
    camera = gp.Camera()
    ctx = gp.Context()
    hasCamInited = False
    try:
        camera.init(ctx)
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
    if hasCamInited:
        do_LoadSetCamConfJson(camera, injsonfile)
        print("Exiting.")
        sys.exit(0)
    else:
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)


# SO:35514531 - see also SO:46934526, 40683840, 9475772, https://github.com/baoboa/pyqt5/blob/master/examples/widgets/imageviewer.py
class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self.parent = parent
        self.isMouseOver = False
        self.ZOOMFACT = 1.25
        self._zoom = 0
        self._zoomfactor = 1
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def printUnityFactor(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())
        print("puf factor {} vr_w {} sr_w {} u_w {} vr_h {} sr_h {} u_h {} ".format(factor, viewrect.width(), scenerect.width(), unity.width(), viewrect.height(), scenerect.height(), unity.height() ))

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                # here, view scaled to fit:
                self._zoomfactor = factor
                self._zoom = math.log( self._zoomfactor, self.ZOOMFACT )
                self.scale(factor, factor)
                self.parent.updateStatusBar()
                if (self.isMouseOver): # should be true on wheel, regardless
                    self.setDragState()

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self._photo.setPixmap(QtGui.QPixmap())

    def resetZoom(self):
        if self.hasPhoto():
            self._zoom = 0
            self._zoomfactor = 1.0
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            self.parent.updateStatusBar()
            if (self.isMouseOver):
                self.setDragState()

    def zoomPlus(self):
        if self.hasPhoto():
            factor = self.ZOOMFACT # 1.25
            self._zoomfactor = self._zoomfactor * self.ZOOMFACT
            self._zoom += 1
            self.scale(factor, factor)
            self.parent.updateStatusBar()
            self.setDragState()

    def zoomMinus(self):
        if self.hasPhoto():
            factor = 1.0/self.ZOOMFACT #0.8
            self._zoomfactor = self._zoomfactor / self.ZOOMFACT
            self._zoom -= 1
            self.scale(factor, factor)
            self.parent.updateStatusBar()
            self.setDragState()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                self.zoomPlus()
            else:
                self.zoomMinus()

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(QtCore.QPoint(event.pos()))
        super(PhotoViewer, self).mousePressEvent(event)

    def getCanDrag(self):
        return ((self.horizontalScrollBar().maximum() > 0) or (self.verticalScrollBar().maximum() > 0))

    def setDragState(self):
        # here we mostly want to take case of the mouse cursor/pointer - and show the hand only when dragging is possible
        canDrag = self.getCanDrag()
        if (canDrag):
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def enterEvent(self, event):
        self.isMouseOver = True
        self.setDragState()
        return super(PhotoViewer, self).enterEvent(event)

    def leaveEvent(self, event):
        self.isMouseOver = False
        # no need for setDragState - is autohandled, as we leave
        return super(PhotoViewer, self).enterEvent(event)

# monkeypatch ccgoo.RangeWidget - it reacted only on self.sliderReleased.connect(self.new_value),
# which reacts only if slider dragged first, making it impossible to control from say VNC
class MyRangeWidget(QtWidgets.QSlider):
    def __init__(self, config_changed, config, parent=None):
        QtWidgets.QSlider.__init__(self, Qt.Horizontal, parent)
        self.config_changed = config_changed
        self.config = config
        if self.config.get_readonly():
            self.setDisabled(True)
        assert self.config.count_children() == 0
        lo, hi, self.inc = self.config.get_range()
        value = self.config.get_value()
        self.setRange(int(lo * self.inc), int(hi * self.inc))
        self.setValue(int(value * self.inc))
        self.valueChanged.connect(self.new_value)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            e.accept()
            x = e.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.setValue(value)
        else:
            return super().mousePressEvent(self, e)

    def new_value(self):
        value = float(self.value()) * self.inc
        self.config.set_value(value)
        self.config_changed()
ccgoo.RangeWidget = MyRangeWidget

class MainWindow(QtWidgets.QMainWindow):
    quit_action = None
    new_image_sig = QtCore.pyqtSignal(object)

    def _reset_config(self):
        if self.hasCamInited:
            if self.old_capturetarget is not None:
                # find the capture target item
                OK, capture_target = gp.gp_widget_get_child_by_name(
                    self.camera_config, 'capturetarget')
                if OK >= gp.GP_OK:
                    # set config
                    capture_target.set_value(self.old_capturetarget)
                    self.camera.set_config(self.camera_config)
                    self.old_capturetarget = None

    def closeEvent(self, event):
        if self.hasCamInited:
            self.running = False
            self._reset_config()
            self.camera.exit()
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        return super(MainWindow, self).closeEvent(event)

    def _set_config(self):
        if self.hasCamInited:
            # find the capture target item
            OK, capture_target = gp.gp_widget_get_child_by_name(
                self.camera_config, 'capturetarget')
            if OK >= gp.GP_OK:
                if self.old_capturetarget is None:
                    self.old_capturetarget = capture_target.get_value()
                choice_count = capture_target.count_choices()
                for n in range(choice_count):
                    choice = capture_target.get_choice(n)
                    if 'internal' in choice.lower():
                        # set config
                        capture_target.set_value(choice)
                        self.camera.set_config(self.camera_config)
                        break
            # find the image format config item
            # camera dependent - 'imageformat' is 'imagequality' on some
            OK, image_format = gp.gp_widget_get_child_by_name(
                self.camera_config, 'imageformat')
            if OK >= gp.GP_OK:
                # get current setting
                value = image_format.get_value()
                # make sure it's not raw
                if 'raw' in value.lower():
                    print('Cannot preview raw images')
                    return False
            return True
        else:
            return False

    def set_splitter(self, inqtsplittertype, inwidget1, inwidget2):
        if (hasattr(self,'splitter1')):
            self.mainwid.layout().removeWidget(self.splitter1)
            self.splitter1.close()
        self.splitter1 = QtWidgets.QSplitter(inqtsplittertype)
        self.splitter1.addWidget(inwidget1)
        self.splitter1.addWidget(inwidget2)
        self.splitter1.setSizes([600, 600]); # equal splitter at start
        self.mainwid.layout().addWidget(self.splitter1)
        self.mainwid.layout().update()

    def create_main_menu(self):
        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        # actions
        self.load_action = QtWidgets.QAction('&Load settings', self)
        self.load_action.setShortcuts(['Ctrl+L'])
        self.load_action.triggered.connect(self.load_settings)
        self.save_action = QtWidgets.QAction('&Save settings', self)
        self.save_action.setShortcuts(['Ctrl+S'])
        self.save_action.triggered.connect(self.save_settings)
        self.fileMenu.addAction(self.load_action)
        self.fileMenu.addAction(self.save_action)
        self.fileMenu.addAction(self.quit_action)
        self.viewMenu = self.mainMenu.addMenu('&View')
        self.zoomorig_action = QtWidgets.QAction('&Zoom original', self)
        self.zoomorig_action.setShortcuts(['Ctrl+Z'])
        self.zoomorig_action.triggered.connect(self.zoom_original)
        self.zoomfitview_action = QtWidgets.QAction('Zoom to &fit view', self)
        self.zoomfitview_action.setShortcuts(['Ctrl+F'])
        self.zoomfitview_action.triggered.connect(self.zoom_fit_view)
        self.zoomplus_action = QtWidgets.QAction('Zoom plu&s', self)
        self.zoomplus_action.setShortcuts(['+'])
        self.zoomplus_action.triggered.connect(self.zoom_plus)
        self.zoomminus_action = QtWidgets.QAction('Zoom &minus', self)
        self.zoomminus_action.setShortcuts(['-'])
        self.zoomminus_action.triggered.connect(self.zoom_minus)
        self.switchlayout_action = QtWidgets.QAction('Switch &Layout', self)
        self.switchlayout_action.setShortcuts(['Ctrl+A'])
        self.switchlayout_action.triggered.connect(self.switch_splitter_layout)
        self.dopreview_action = QtWidgets.QAction('Do &Preview', self)
        self.dopreview_action.setShortcuts(['Ctrl+X'])
        self.dopreview_action.triggered.connect(self._do_preview)
        self.repeatpreview_action = QtWidgets.QAction('&Repeat Preview', self)
        self.repeatpreview_action.setShortcuts(['Ctrl+R'])
        self.repeatpreview_action.setCheckable(True)
        self.repeatpreview_action.setChecked(False)
        self.repeatpreview_action.triggered.connect(self.continuous)
        self.docapture_action = QtWidgets.QAction('Capture &Image', self)
        self.docapture_action.setShortcuts(['Ctrl+I'])
        self.docapture_action.triggered.connect(self._capture_image)
        self.viewMenu.addAction(self.switchlayout_action)
        self.viewMenu.addAction(self.dopreview_action)
        self.viewMenu.addAction(self.repeatpreview_action)
        self.viewMenu.addAction(self.docapture_action)
        self.viewMenu.addAction(self.zoomorig_action)
        self.viewMenu.addAction(self.zoomfitview_action)
        self.viewMenu.addAction(self.zoomplus_action)
        self.viewMenu.addAction(self.zoomminus_action)

    def replicate_ccgoo_main_window(self):
        # main widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(QtWidgets.QGridLayout())
        self.widget.layout().setColumnStretch(0, 1)
        # 'apply' button
        if self.args.config_apply_btn == 1:
            self.apply_button = QtWidgets.QPushButton('apply changes')
            self.apply_button.setEnabled(False)
            self.apply_button.clicked.connect(self.apply_changes)
            self.widget.layout().addWidget(self.apply_button, 1, 1)

    def eventFilter(self, source, event):
        return super(MainWindow, self).eventFilter(source, event)

    def replicate_fg_viewer(self):
        self.image_display = PhotoViewer(self)
        self.frameviewlayout.addWidget(self.image_display)
        self.new_image_sig.connect(self.new_image)

    def updateStatusBar(self):
        msgstr = ""
        if self.lastException:
            msgstr = "No camera: {} {}; ".format( type(self.lastException).__name__, self.lastException.args)
        if self.hasCamInited:
            msgstr = "Camera model: {} ; ".format(self.camera_model if (self.camera_model) else "No info")
            if self.lastImageSize:
                msgstr += "last imgsize: {} x {} ".format(self.lastImageSize[0], self.lastImageSize[1])
        zoomstr = "zoom: {:.3f} {:.3f}".format(self.image_display._zoom, self.image_display._zoomfactor)
        def replacer(m):
            retstr = m.group(1).replace(r'0', ' ')+' '*len(m.group(2))
            return retstr
        zoomstr = patTrailDigSpace.sub(lambda m: replacer(m), zoomstr)
        msgstr += zoomstr
        if self.fps:
            msgstr += " ; {}".format(self.fps)
            self.fps = ""
        if self.singleStatusMsg:
            msgstr += " ({})".format(self.singleStatusMsg)
            self.singleStatusMsg = ""
        self.statusBar().showMessage(msgstr)

    def checkCreateNoCamImg(self):
        nocamimgpath = os.path.join(THISSCRIPTDIR, NOCAMIMG)
        if (not(os.path.isfile(nocamimgpath))):
            # create gradient background with text:
            nocamsize = (320, 240)
            nocamsizec = (nocamsize[0]/2, nocamsize[1]/2)
            colA = (80, 80, 80) ; colB = (210, 30, 30) ; # colB is center
            nocamimg = Image.new('RGB', nocamsize, color=0xFF)
            gradoffset = (-50, 20)
            nocammaxd = math.sqrt((nocamsizec[0]+abs(gradoffset[0]))**2 + (nocamsizec[1]+abs(gradoffset[1]))**2)
            for ix in range(nocamsize[0]):
                for iy in range(nocamsize[1]):
                    dist = math.sqrt( (ix-nocamsizec[0]-gradoffset[0])**2 + (iy-nocamsizec[1]-gradoffset[1])**2 )
                    distnorm = dist/nocammaxd
                    r = colA[0]*distnorm + colB[0]*(1.0-distnorm)
                    g = colA[1]*distnorm + colB[1]*(1.0-distnorm)
                    b = colA[2]*distnorm + colB[2]*(1.0-distnorm)
                    nocamimg.putpixel((ix, iy), (int(r), int(g), int(b)) )
            d = ImageDraw.Draw(nocamimg)
            d.text((20,nocamsizec[1]-4), "No camera (unknown)", fill=(240,240,240))
            nocamimg.save(nocamimgpath)


    def __init__(self, args):
        self.args = args
        self.current_splitter_style=0
        self.lastImageSize = None
        self.lastImageType = None # 0 - preview; 1 - capture image
        self.timestamp = None
        self.fps = ""
        self.lastException = None
        self.lastOpenPath = None
        self.lastSavePath = None
        self.singleStatusMsg = ""
        self.hasCamInited = False
        self.do_init = QtCore.QEvent.registerEventType()
        self.do_next = QtCore.QEvent.registerEventType()
        self.running = False
        QtWidgets.QMainWindow.__init__(self)
        self.settings = QtCore.QSettings("MyCompany", APPNAME)
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))
        self.setWindowTitle("Camera config {}".format(APPNAME))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        # quit shortcut
        self.quit_action = QtWidgets.QAction('&Quit', self)
        self.quit_action.setShortcuts(['Ctrl+Q', 'Ctrl+W'])
        self.quit_action.setStatusTip('Exit application')
        self.quit_action.triggered.connect(QtWidgets.qApp.closeAllWindows)
        self.addAction(self.quit_action)
        # main menu
        self.create_main_menu()
        # replicate main window from camera-config-gui-oo
        self.replicate_ccgoo_main_window()
        # frames
        self.frameview = QtWidgets.QFrame(self)
        self.frameview.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameviewlayout = QtWidgets.QGridLayout(self.frameview)
        self.frameviewlayout.setSpacing(0);
        self.frameviewlayout.setContentsMargins(0,0,0,0);

        self.checkCreateNoCamImg()

        self.replicate_fg_viewer()

        self.frameconf = QtWidgets.QFrame(self)
        self.frameconf.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameconf.setStyleSheet("padding: 0;") # nope
        self.frameconflayout = QtWidgets.QHBoxLayout(self.frameconf)
        self.frameconflayout.setSpacing(0);
        self.frameconflayout.setContentsMargins(0,0,0,0);
        self.scrollconf = QtWidgets.QScrollArea(self)
        self.scrollconf.setWidgetResizable(False)
        # self.contentconf is just used for init here; afterward is replaced by self.widget (self.configsection)
        self.contentconf = QtWidgets.QWidget()
        self.contentconf.setLayout(QtWidgets.QGridLayout())
        self.contentconf.layout().setColumnStretch(0, 1)
        self.scrollconf.setWidget(self.contentconf)
        self.frameconflayout.addWidget(self.scrollconf)

        self.mainwid = QtWidgets.QWidget()
        self.mainwid.setLayout(QtWidgets.QGridLayout())
        self.setCentralWidget(self.mainwid)
        self.set_splitter(Qt.Horizontal, self.frameview, self.frameconf)

        self.camera = gp.Camera()
        self.ctx = gp.Context()
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_init), Qt.LowEventPriority - 1)

    def event(self, event):
        if ( (event.type() != self.do_init) and (event.type() != self.do_next) ):
            return QtWidgets.QMainWindow.event(self, event)
        event.accept()
        if event.type() == self.do_init:
            QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self.initialise()
            finally:
                QtWidgets.QApplication.restoreOverrideCursor()
            return True
        elif event.type() == self.do_next:
            self._do_continuous()
            return True

    def _do_continuous(self):
        if not self.running:
            self._reset_config()
            return
        if self.hasCamInited:
             self._do_preview()
        else:
            self._do_preview_camnotinit()
        # post event to trigger next capture
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_next), Qt.LowEventPriority - 1)

    @QtCore.pyqtSlot()
    def continuous(self):
        if self.running:
            self.running = False
            self.updateStatusBar() # clear last singleStatusMsg - clears fps upon stop
            return
        self.running = True
        self._do_continuous()

    def CameraHandlerInit(self):
        # get camera config tree
        self.hasCamInited = False
        self.lastException = None
        try:
            self.camera.init(self.ctx)
            self.hasCamInited = True
        except Exception as ex:
            self.lastException = ex
            if type(ex) == gp.GPhoto2Error:
                nocamimgpath = os.path.join(THISSCRIPTDIR, NOCAMIMG)
                temppixmap = QtGui.QPixmap(nocamimgpath)
                self.image_display.setPhoto(temppixmap)
        if self.hasCamInited:
            self.camera_config = self.camera.get_config()
            # from CameraHandler::Init:
            self.old_capturetarget = None
            # get the camera model
            self.camera_model = get_camera_model(self.camera_config)
            put_camera_capture_preview_mirror(self.camera, self.camera_config, self.camera_model)
        self.updateStatusBar()

    def recreate_section_widget(self):
        if ( hasattr(self, 'configsection') and (self.configsection) ):
            self.widget.layout().removeWidget(self.configsection)
        self.configsection = ccgoo.SectionWidget(self.config_changed, self.camera_config)
        self.widget.layout().addWidget(self.configsection, 0, 0, 1, 3)
        self.scrollconf.setWidget(self.widget)

    def initialise(self):
        self.CameraHandlerInit()
        if self.hasCamInited:
            # create corresponding tree of tab widgets
            self.setWindowTitle(self.camera_config.get_label())
            self.recreate_section_widget()

    def config_changed(self):
        if self.args.config_apply_btn == 1:
            self.apply_button.setEnabled(True)
        else:
            def handler():
                self.apply_changes()
                timer.stop()
                timer.deleteLater()
            timer = QtCore.QTimer()
            timer.timeout.connect(handler)
            timer.start(0)

    def reconstruct_config_section(self):
        # assumes first setup already done, so there are existing tabs:
        tabs = self.configsection.children()[1]
        lastindex = tabs.currentIndex()
        # get also the values of self.scrollconf scrollbars
        lastconfhscroll = (self.scrollconf.horizontalScrollBar().value(), self.scrollconf.horizontalScrollBar().minimum(), self.scrollconf.horizontalScrollBar().singleStep(), self.scrollconf.horizontalScrollBar().pageStep(), self.scrollconf.horizontalScrollBar().maximum())
        lastconfvscroll = (self.scrollconf.verticalScrollBar().value(), self.scrollconf.verticalScrollBar().minimum(), self.scrollconf.verticalScrollBar().singleStep(), self.scrollconf.verticalScrollBar().pageStep(), self.scrollconf.verticalScrollBar().maximum())
        # Pre-reconstruct
        self.camera_config = self.camera.get_config()
        self.replicate_ccgoo_main_window()
        self.recreate_section_widget()
        tabs = self.configsection.children()[1]
        tabs.setCurrentIndex(lastindex)
        # Post-reconstruct
        self.scrollconf.horizontalScrollBar().setValue(lastconfhscroll[0])
        self.scrollconf.verticalScrollBar().setValue(lastconfvscroll[0])

    def apply_changes(self):
        self.camera.set_config(self.camera_config)
        # here we'd need to reconstruct, to get the proper config values
        self.reconstruct_config_section()

    def load_settings(self):
        self.updateStatusBar() # clear last singleStatusMsg
        if self.lastOpenPath is not None:
            startpath, startfile = os.path.split(self.lastOpenPath)
        elif self.lastSavePath is not None:
            startpath, startfile = os.path.split(self.lastSavePath)
        else: # both None
            startpath = os.getcwd()
            startfile = ""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Camera Settings", os.path.join(startpath, startfile), "JSON Text Files (*.json);;All Files (*)", options=options)
        if fileName:
            do_LoadSetCamConfJson(self.camera, fileName)
            # update GUI also
            self.camera_config = self.camera.get_config()
            # avoid GUI context
            def handler():
                self.apply_changes()
                timer.stop()
                timer.deleteLater()
            timer = QtCore.QTimer()
            timer.timeout.connect(handler)
            timer.start(0)
            self.lastOpenPath = fileName
            self.singleStatusMsg = "loaded file to cam config; see terminal stdout for more"
            self.updateStatusBar()

    def save_settings(self):
        self.updateStatusBar() # clear last singleStatusMsg
        if self.lastSavePath is not None:
            startpath, startfile = os.path.split(self.lastSavePath)
        else: # both None
            startpath = os.getcwd()
            startfile = "{}.json".format( re.sub(r'\s+', '', self.camera_model) )
        unixts = time.time()
        startfile = get_stamped_filename(startfile, unixts)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Camera Settings", os.path.join(startpath, startfile), "JSON Text Files (*.json);;All Files (*)", options=options)
        if fileName:
            do_GetSaveCamConfJson(self.camera, fileName, unixts)
            self.lastSavePath = fileName
            self.singleStatusMsg = "saved cam config to file; see terminal stdout for more"
            self.updateStatusBar()

    def zoom_original(self):
        self.image_display.resetZoom()

    def zoom_fit_view(self):
        self.image_display.fitInView()

    def zoom_plus(self):
        self.image_display.zoomPlus()

    def zoom_minus(self):
        self.image_display.zoomMinus()

    def set_splitter_layout_style(self):
        if self.current_splitter_style == 0:
            self.set_splitter(Qt.Horizontal, self.frameview, self.frameconf)
        elif self.current_splitter_style == 1:
            self.set_splitter(Qt.Vertical, self.frameview, self.frameconf)
        elif self.current_splitter_style == 2:
            self.set_splitter(Qt.Horizontal, self.frameconf, self.frameview)
        elif self.current_splitter_style == 3:
            self.set_splitter(Qt.Vertical, self.frameconf, self.frameview)

    def switch_splitter_layout(self):
        self.current_splitter_style = (self.current_splitter_style + 1) % 4
        self.set_splitter_layout_style()

    def _do_preview(self):
        # capture preview image
        OK, camera_file = gp.gp_camera_capture_preview(self.camera)
        if OK < gp.GP_OK:
            print('Failed to capture preview')
            self.running = False
            return
        self._send_file(camera_file)

    def _do_preview_camnotinit(self):
        # since cam not inited here, just load the cam-conf-no-cam.png/NOCAMIMG
        nocamimgpath = os.path.join(THISSCRIPTDIR, NOCAMIMG)
        image = Image.open(nocamimgpath)
        image.load()
        self.singleStatusMsg = "No cam img: {} x {}".format(image.size[0], image.size[1])
        self.new_image_sig.emit(image)

    def _capture_image(self):
        startts = time.time()
        self.running = False
        self.repeatpreview_action.setChecked(False) # needed just for the menu item
        self.singleStatusMsg = "Capturing image - wait ..."
        self.updateStatusBar() # clear last singleStatusMsg
        imgfilename = do_capture_image(self.camera)
        imgpathname = os.path.realpath(imgfilename)
        image = Image.open(imgpathname)
        image.load()
        self.new_image_sig.emit(image)
        self.lastImageType = 1
        self.image_display.fitInView()
        endts = time.time()
        self.singleStatusMsg = "Captured image: {} [{:.3f} s]".format(imgpathname, endts-startts)
        self.updateStatusBar()

    def _send_file(self, camera_file):
        file_data = camera_file.get_data_and_size()
        image = Image.open(io.BytesIO(file_data))
        image.load()
        self.new_image_sig.emit(image)
        if self.lastImageType != 0:
            self.image_display.fitInView() # reset previous offsets..
            self.image_display.resetZoom() # .. then back to zoom_original for preview img
            self.lastImageType = 0

    @QtCore.pyqtSlot(object)
    def new_image(self, image):
        self.lastImageSize = image.size
        w, h = image.size
        image_data = image.tobytes('raw', 'RGB')
        self.q_image = QtGui.QImage(image_data, w, h, QtGui.QImage.Format_RGB888)
        self._draw_image()
        if self.timestamp is not None:
            tstampnow = time.time()
            tdelta = tstampnow - self.timestamp
            fps = 1.0/tdelta
            self.fps = "(<{} fps)".format(MINFPS) if (fps<MINFPS) else "{:7.2f} fps".format(fps)
            self.timestamp = tstampnow
        else:
            self.timestamp = time.time()
        self.updateStatusBar()

    def _draw_image(self):
        if not self.q_image:
            return
        self.pixmap = QtGui.QPixmap.fromImage(self.q_image)
        self.image_display.setPhoto(self.pixmap)


def main():
    locale.setlocale(locale.LC_ALL, '')
    # set up logging
    # note that: '%(filename)s:%(lineno)d' just prints 'port_log.py:127'
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    callback_obj = gp.check_result(gp.use_python_logging())

    # command line argument parser
    parser = argparse.ArgumentParser(description="{} - interact with camera via python-gphoto2. Called without command line arguments, it will start a Qt GUI.".format(APPNAME))
    parser.add_argument('--save-cam-conf-json', default=argparse.SUPPRESS, help='Get and save the camera configuration to .json file, if standalone (together with --load-cam-conf-json, can be used for copying filtered json files). The string argument is the filename, action is aborted if standalone and no camera online, or if the argument is empty. Overwrites existing files without prompting. Note that if camera is online, but mirror is not raised, process will complete with errors and fewer properties collected in json file (default: suppress)') # "%(default)s"
    parser.add_argument('--load-cam-conf-json', default=argparse.SUPPRESS, help='Load and set the camera configuration from .json file, if standalone (together with --save-cam-conf-json, can be used for copying filtered json files). The string argument is the filename, action is aborted if standalone and no camera online, or if the argument is empty (default: suppress)') # "%(default)s"
    parser.add_argument('--include-names-json', default=argparse.SUPPRESS, help='Comma separated list of property names to be filtered/included. When using --load-cam-conf-json with --save-cam-conf-json, a json copy with flattening of hierarchy (removal of nodes with children and without value) is performed; in that case --include-names-json can be used to include only certain properties in the output. Can also use `ro=0` or `ro=1` as filtering criteria. If empty ignored (default: suppress)') # "%(default)s"
    parser.add_argument('--start-capture-view', default='', help='Command - start capture view (extend lens/raise mirror) on the camera, then exit', action='store_const', const=start_capture_view) # "%(default)s"
    parser.add_argument('--stop-capture-view', default='', help='Command - stop capture view (retract lens/release mirror) on the camera, then exit', action='store_const', const=stop_capture_view) # "%(default)s"
    parser.add_argument('--config-apply-btn', type=int, default=0, help='GUI option: 0: do not create apply button, update on change; 1: create apply button, update on its click (default: %(default)s)') # ""
    args = parser.parse_args() # in case of --help, this also prints help and exits before Qt window is raised
    if (args.start_capture_view): args.start_capture_view()
    elif (args.stop_capture_view): args.stop_capture_view()
    elif (hasattr(args, 'save_cam_conf_json') and not(hasattr(args, 'load_cam_conf_json'))):
        getSaveCamConfJson(args)
    elif (hasattr(args, 'load_cam_conf_json') and not(hasattr(args, 'save_cam_conf_json'))):
        loadSetCamConfJson(args)
    elif (hasattr(args, 'load_cam_conf_json') and hasattr(args, 'save_cam_conf_json')):
        copyFilterCamConfJson(args)

    # start Qt Gui
    app = QtWidgets.QApplication([APPNAME]) # SO: 18133302
    main = MainWindow(args)
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

