#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-18  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# another camera config gui, with load/save settings to file, and live view
# started: sdaau 2019, on with python3-gphoto2 and `sudo -H pip2 install gphoto2`, Ubuntu 18.04
# uses camera-config-gui-oo.py, focus-gui.py

from __future__ import print_function

import io
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

from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt5.QtGui import QIcon

import gphoto2 as gp

THISSCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1,THISSCRIPTDIR)
ccgoo = __import__('camera-config-gui-oo')
#fg = __import__('focus-gui')
NOCAMIMG = "cam-conf-no-cam.png"
APPNAME = "cam-conf-view-gui.py"

patTrailDigSpace = re.compile(r'(?<=\.)(\d+?)(0+)(?=[^\d]|$)') # SO: 32348435


def get_camera_model(camera_config):
    # get the camera model
    OK, camera_model = gp.gp_widget_get_child_by_name(
        camera_config, 'cameramodel')
    if OK < gp.GP_OK:
        OK, camera_model = gp.gp_widget_get_child_by_name(
            camera_config, 'model')
    if OK >= gp.GP_OK:
        camera_model = camera_model.get_value()
        #print('Camera model:', camera_model)
    else:
        #print('No camera model info')
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
    tzlocalts = tzlocal.get_localzone().localize(datetime.utcfromtimestamp(unixts), is_dst=None).replace(microsecond=0)
    isots = tzlocalts.isoformat(' ')
    fsuffts = tzlocalts.strftime('%Y%m%d_%H%M%S') # file suffix timestamp
    return (unixts, isots, fsuffts)


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

def get_camera_config_object(camera_config):
    retdict = OrderedDict()
    retdict['camera_model'] = get_camera_model(camera_config)
    unixts, isots, fsuffts = get_formatted_ts( time.time() )
    retdict['ts_taken_on'] = unixts
    retdict['date_taken_on'] = isots
    propcount = PropCount()
    retarray = []
    # # from camera-config-gui-oo.py
    # for child in camera_config.get_children():
    #     tmpdict = OrderedDict()
    #     tmpdict['ro'] = child.get_readonly()
    #     tmpdict['label'] = child.get_label()
    #     tmpdict['name'] = child.get_name()
    #     tmpdict['type'] = child.get_type()
    #     if ((tmpdict['type'] == gp.GP_WIDGET_RADIO) or (tmpdict['type'] == gp.GP_WIDGET_MENU)):
    #         tmpdict['count_choices'] = child.count_choices()
    #     retarray.append(tmpdict)
    # retdict['config'] = retarray
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
        print(gp.gp_camera_capture_preview(camera)) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]

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
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)#Off)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)#Off)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def printUnityFactor(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        #self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height())
        # NB: u_w == u_h gives "previous" or "current" _zoomfactor (depending where its called)
        # NB: vr_w, vr_h remain same after zoom, sr_w, sr_h change (both are pixel sizes)
        print("puf factor {} vr_w {} sr_w {} u_w {} vr_h {} sr_h {} u_h {} ".format(factor, viewrect.width(), scenerect.width(), unity.width(), viewrect.height(), scenerect.height(), unity.height() ))

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                # here, unity.width() == unity.height(); view is reset to actual in pixels (so: _zoomfactor=1, _zoom=0):
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                #~ print("fiv factor {} vr_w {} sr_w {} u_w {} vr_h {} sr_h {} u_h {} ".format(factor, viewrect.width(), scenerect.width(), unity.width(), viewrect.height(), scenerect.height(), unity.height() ))
                # here, view scaled to fit:
                self._zoomfactor = factor
                self._zoom = math.log( self._zoomfactor, self.ZOOMFACT )
                self.scale(factor, factor)
                self.parent.updateStatusBar()
                if (self.isMouseOver): # should be true on wheel, regardless
                    self.setDragState()
            #self._zoom = 0

    def setPhoto(self, pixmap=None):
        #self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            #self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        #self.fitInView()

    def resetZoom(self):
        if self.hasPhoto():
            self._zoom = 0
            self._zoomfactor = 1.0
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            self.parent.updateStatusBar()
            #~ self.printUnityFactor()
            if (self.isMouseOver): # should be true on wheel, regardless
                self.setDragState()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = self.ZOOMFACT # 1.25
                self._zoomfactor = self._zoomfactor * self.ZOOMFACT
                self._zoom += 1
            else:
                factor = 1.0/self.ZOOMFACT #0.8
                self._zoomfactor = self._zoomfactor / self.ZOOMFACT
                self._zoom -= 1
            #if self._zoom > 0:
            #    self.scale(factor, factor)
            #elif self._zoom == 0:
            #    #self.fitInView()
            #    pass
            #else:
            #    self._zoom = 0
            # note: resetTransform() with scale(_zoomfactor) works - but it also messes up anchor under the mouse
            #self.resetTransform() #self.resetMatrix() # SO: 39101834, but it causes "AttributeError ... has no attribute 'resetMatrix'" SO:54311832, but as per qt doc, likely resetTransform is same as resetMatrix
            #self.scale(self._zoomfactor, self._zoomfactor)
            # so better to go along with scale(factor) here, for smoother browsing:
            self.scale(factor, factor)
            self.parent.updateStatusBar()
            #~ self.printUnityFactor()
            if (self.isMouseOver): # should be true on wheel, regardless
                self.setDragState()

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(QtCore.QPoint(event.pos()))
        super(PhotoViewer, self).mousePressEvent(event)

    def getCanDrag(self):
        return ((self.horizontalScrollBar().maximum() > 0) or (self.verticalScrollBar().maximum() > 0))

    def setDragState(self):
        # here we mostly want to take case of the mouse cursor/pointer - and show the hand only when dragging is possible
        canDrag = self.getCanDrag()
        #~ print("Mouse Entered, {} {} {} {} {} {} {}".format(self.horizontalScrollBar().minimum(), self.horizontalScrollBar().pageStep(), self.horizontalScrollBar().maximum(), self.verticalScrollBar().minimum(), self.verticalScrollBar().pageStep(), self.verticalScrollBar().maximum(), canDrag))
        if (canDrag):
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def enterEvent(self, event):
        self.isMouseOver = True
        self.setDragState()
        return super(PhotoViewer, self).enterEvent(event)

    def leaveEvent(self, event):
        #print("Mouse Left")
        self.isMouseOver = False
        # no need for setDragState - is autohandled, as we leave
        return super(PhotoViewer, self).enterEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    quit_action = None
    new_image_sig = QtCore.pyqtSignal(object)

    def _reset_config(self):
        if self.old_capturetarget is not None:
            # find the capture target item
            OK, capture_target = gp.gp_widget_get_child_by_name(
                self.config, 'capturetarget')
            if OK >= gp.GP_OK:
                # set config
                capture_target.set_value(self.old_capturetarget)
                self.camera.set_config(self.config)
                self.old_capturetarget = None

    def closeEvent(self, event):
        if self.hasCamInited:
            #~ self.camera_handler.shut_down() # ->
            #~ self.running = False
            self._reset_config()
            self.camera.exit()
            #~ self.ch_thread.quit()
            #~ self.ch_thread.wait()
        return super(MainWindow, self).closeEvent(event)

    def _set_config(self):
        # find the capture target item
        OK, capture_target = gp.gp_widget_get_child_by_name(
            self.config, 'capturetarget')
        if OK >= gp.GP_OK:
            if self.old_capturetarget is None:
                self.old_capturetarget = capture_target.get_value()
            choice_count = capture_target.count_choices()
            for n in range(choice_count):
                choice = capture_target.get_choice(n)
                if 'internal' in choice.lower():
                    # set config
                    capture_target.set_value(choice)
                    self.camera.set_config(self.config)
                    break
        # find the image format config item
        OK, image_format = gp.gp_widget_get_child_by_name(
            self.config, 'imageformat')
        if OK >= gp.GP_OK:
            # get current setting
            value = image_format.get_value()
            # make sure it's not raw
            if 'raw' in value.lower():
                print('Cannot preview raw images')
                return False
        return True

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
        self.fileMenu = self.mainMenu.addMenu('File')
        # actions
        self.load_action = QtWidgets.QAction('Load settings', self)
        self.load_action.setShortcuts(['Ctrl+L'])
        self.load_action.triggered.connect(self.load_settings)
        self.save_action = QtWidgets.QAction('Save settings', self)
        self.save_action.setShortcuts(['Ctrl+S'])
        self.save_action.triggered.connect(self.save_settings)
        self.fileMenu.addAction(self.load_action)
        self.fileMenu.addAction(self.save_action)
        self.fileMenu.addAction(self.quit_action)
        self.viewMenu = self.mainMenu.addMenu('View')
        self.zoomorig_action = QtWidgets.QAction('Zoom original', self)
        self.zoomorig_action.setShortcuts(['Ctrl+Z'])
        self.zoomorig_action.triggered.connect(self.zoom_original)
        self.zoomfitview_action = QtWidgets.QAction('Zoom to fit view', self)
        self.zoomfitview_action.setShortcuts(['Ctrl+F'])
        self.zoomfitview_action.triggered.connect(self.zoom_fit_view)
        self.switchlayout_action = QtWidgets.QAction('Switch Layout', self)
        self.switchlayout_action.setShortcuts(['Ctrl+A'])
        self.switchlayout_action.triggered.connect(self.switch_splitter_layout)
        self.dopreview_action = QtWidgets.QAction('Do Preview', self)
        self.dopreview_action.setShortcuts(['Ctrl+X'])
        self.dopreview_action.triggered.connect(self._do_preview)
        self.viewMenu.addAction(self.switchlayout_action)
        self.viewMenu.addAction(self.dopreview_action)
        self.viewMenu.addAction(self.zoomorig_action)
        self.viewMenu.addAction(self.zoomfitview_action)

    def replicate_ccgoo_main_window(self):
        # main widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(QtWidgets.QGridLayout())
        self.widget.layout().setColumnStretch(0, 1)
        #self.setCentralWidget(self.widget)
        # 'apply' button
        self.apply_button = QtWidgets.QPushButton('apply changes')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_changes)
        self.widget.layout().addWidget(self.apply_button, 1, 1)
        # 'cancel' button
        #quit_button = QtWidgets.QPushButton('cancel')
        #quit_button.clicked.connect(QtWidgets.qApp.closeAllWindows)
        #widget.layout().addWidget(quit_button, 1, 2)

    def eventFilter(self, source, event):
        #if (event.type() == QtCore.QEvent.Wheel): # no need anymore
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
            if self.lastPreviewSize:
                msgstr += "last preview: {} x {} ".format(self.lastPreviewSize[0], self.lastPreviewSize[1])
        msgstr += "zoom: {:.3f} {:.3f}".format(self.image_display._zoom, self.image_display._zoomfactor)
        def replacer(m):
            retstr = m.group(1).replace(r'0', ' ')+' '*len(m.group(2))
            #~ print('"{}" "{}" "{}" -> "{}"'.format(m.group(0),m.group(1),m.group(2),retstr))
            return retstr
        msgstr = patTrailDigSpace.sub(lambda m: replacer(m), msgstr)
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
            # SO:2726171 "Per PIL's docs, ImageDraw's default font is a bitmap font, and therefore it cannot be scaled. For scaling, you need to select a true-type font."
            # SO:24085996 ImageFont: "On Windows, if the given file name does not exist, the loader also looks in Windows fonts directory."
            d = ImageDraw.Draw(nocamimg)
            d.text((20,nocamsizec[1]-4), "No camera (unknown)", fill=(240,240,240))
            nocamimg.save(nocamimgpath)


    def __init__(self):
        self.current_splitter_style=0
        self.lastPreviewSize = None
        self.lastException = None
        self.hasCamInited = False
        self.do_init = QtCore.QEvent.registerEventType()
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Camera config {}".format(APPNAME))
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        # quit shortcut
        self.quit_action = QtWidgets.QAction('Quit', self)
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
        self.contentconf = QtWidgets.QWidget()
        self.contentconf.setLayout(QtWidgets.QGridLayout())
        self.contentconf.layout().setColumnStretch(0, 1)
        self.scrollconf.setWidget(self.contentconf)
        self.frameconflayout.addWidget(self.scrollconf)

        self.mainwid = QtWidgets.QWidget()
        self.mainwid.setLayout(QtWidgets.QGridLayout())
        self.setCentralWidget(self.mainwid)
        self.set_splitter(Qt.Horizontal, self.frameview, self.frameconf)

        # defer full initialisation (slow operation) until gui is visible
        #~ tempmap = QtGui.QPixmap("grad.png")
        #~ self.new_image(tempmap)

        self.camera = gp.Camera()
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_init), Qt.LowEventPriority - 1)

    def event(self, event):
        if event.type() != self.do_init:
            return QtWidgets.QMainWindow.event(self, event)
        event.accept()
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        #print("AO: {} {}".format( self.contentview.frameGeometry().width(), self.contentview.frameGeometry().height() ) ) # 187 258, OK
        # set initial size
        #inwfit, inhfit = self.frameview.frameGeometry().width(), self.frameview.frameGeometry().height()
        try:
            self.initialise()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        return True

    def CameraHandlerInit(self):
        # get camera config tree
        self.hasCamInited = False
        self.lastException = None
        try:
            self.camera.init() # prints: WARNING: gphoto2: (b'gp_context_error') b'Could not detect any camera' if logging set up
            self.hasCamInited = True
        except Exception as ex:
            self.lastException = ex
            if type(ex) == gp.GPhoto2Error: #gphoto2.GPhoto2Error:
                nocamimgpath = os.path.join(THISSCRIPTDIR, NOCAMIMG)
                temppixmap = QtGui.QPixmap(nocamimgpath)
                self.image_display.setPhoto(temppixmap)
        if self.hasCamInited:
            self.camera_config = self.camera.get_config()
            # from CameraHandler::Init:
            self.old_capturetarget = None
            # # get the camera model
            # OK, camera_model = gp.gp_widget_get_child_by_name(
            #     self.camera_config, 'cameramodel')
            # if OK < gp.GP_OK:
            #     OK, camera_model = gp.gp_widget_get_child_by_name(
            #         self.camera_config, 'model')
            # if OK >= gp.GP_OK:
            #     self.camera_model = camera_model.get_value()
            #     print('Camera model:', self.camera_model)
            # else:
            #     print('No camera model info')
            #     self.camera_model = ''
            self.camera_model = get_camera_model(self.camera_config)
            # if self.camera_model == 'unknown':
            #     # find the capture size class config item
            #     # need to set this on my Canon 350d to get preview to work at all
            #     OK, capture_size_class = gp.gp_widget_get_child_by_name(
            #         self.camera_config, 'capturesizeclass')
            #     if OK >= gp.GP_OK:
            #         # set value
            #         value = capture_size_class.get_choice(2)
            #         capture_size_class.set_value(value)
            #         # set config
            #         self.camera.set_config(self.camera_config)
            # else:
            #     # put camera into preview mode to raise mirror
            #     print(gp.gp_camera_capture_preview(self.camera)) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]
            put_camera_capture_preview_mirror(self.camera, self.camera_config, self.camera_model)
        self.updateStatusBar()

    def initialise(self):
        #~ # get camera config tree
        #~ self.camera.init()
        #~ self.camera_config = self.camera.get_config()
        self.CameraHandlerInit()
        if self.hasCamInited:
            # create corresponding tree of tab widgets
            self.setWindowTitle(self.camera_config.get_label())
            self.configsection = ccgoo.SectionWidget(self.config_changed, self.camera_config)
            self.widget.layout().addWidget(self.configsection, 0, 0, 1, 3)
            self.scrollconf.setWidget(self.widget)

    def config_changed(self):
        self.apply_button.setEnabled(True)

    def apply_changes(self):
        self.camera.set_config(self.camera_config)
        #QtWidgets.qApp.closeAllWindows()

    def load_settings(self):
        print("load_settings")

    def save_settings(self):
        print("save_settings")

    def zoom_original(self):
        #~ print("zoom_original")
        self.image_display.resetZoom()

    def zoom_fit_view(self):
        #~ print("zoom_fit_view")
        self.image_display.fitInView()

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
        #~ print("switch_splitter_layout")
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

    def _send_file(self, camera_file):
        file_data = camera_file.get_data_and_size()
        image = Image.open(io.BytesIO(file_data))
        image.load()
        self.new_image_sig.emit(image)

    @QtCore.pyqtSlot(object)
    def new_image(self, image):
        self.lastPreviewSize = image.size
        self.updateStatusBar()
        w, h = image.size
        image_data = image.tobytes('raw', 'RGB')
        self.q_image = QtGui.QImage(image_data, w, h, QtGui.QImage.Format_RGB888)
        self._draw_image()
        # # generate histogram and count clipped pixels
        # histogram = image.histogram()
        # q_image = QtGui.QImage(100, 256, QtGui.QImage.Format_RGB888)
        # q_image.fill(Qt.white)
        # clipping = []
        # start = 0
        # for colour in (0xff0000, 0x00ff00, 0x0000ff):
        #     stop = start + 256
        #     band_hist = histogram[start:stop]
        #     max_value = float(1 + max(band_hist))
        #     for x in range(len(band_hist)):
        #         y = float(1 + band_hist[x]) / max_value
        #         #y = 98.0 * max(0.0, 1.0 + (math.log10(y) / 5.0))
        #         q_image.setPixel(y,     x, colour)
        #         q_image.setPixel(y + 1, x, colour)
        #     #clipping.append(band_hist[-1])
        #     start = stop
        # pixmap = QtGui.QPixmap.fromImage(q_image)
        # self.histogram_display.setPixmap(pixmap)
        # self.clipping_display.setText(
        #     ', '.join(map(lambda x: '{:d}'.format(x), clipping)))
        # # measure focus by summing inter-pixel differences
        # shifted = ImageChops.offset(image, 1, 0)
        # diff = ImageChops.difference(image, shifted).crop((1, 0, w, h))
        # stats = ImageStat.Stat(diff)
        # h_rms = stats.rms
        # shifted = ImageChops.offset(image, 0, 1)
        # diff = ImageChops.difference(image, shifted).crop((0, 1, w, h))
        # stats = ImageStat.Stat(diff)
        # rms = stats.rms
        # for n in range(len(rms)):
        #     rms[n] += h_rms[n]
        # # "auto-ranging" of focus measurement
        # while self.focus_scale < 1.0e12 and (max(rms) * self.focus_scale) < 1.0:
        #     self.focus_scale *= 10.0
        #     print('+', self.focus_scale)
        # while self.focus_scale > 1.0e-12 and (max(rms) * self.focus_scale) > 100.0:
        #     self.focus_scale /= 10.0
        #     print('-', self.focus_scale)
        # self.focus_display.setText(
        #     ', '.join(map(lambda x: '{:.2f}'.format(x * self.focus_scale), rms)))

    def _draw_image(self):
        if not self.q_image:
            return
        self.pixmap = QtGui.QPixmap.fromImage(self.q_image)
        self.image_display.setPhoto(self.pixmap)

def getSaveCamConfJson(args):
    if (not(args.save_cam_conf_json)):
        print("getSaveCamConfJson: Sorry, unusable/empty output .json filename; aborting")
        sys.exit(1)
    jsonfile = os.path.realpath(args.save_cam_conf_json)
    print("getSaveCamConfJson: saving to {}".format(jsonfile))
    camera = gp.Camera()
    hasCamInited = False
    try:
        camera.init() # prints: WARNING: gphoto2: (b'gp_context_error') b'Could not detect any camera' if logging set up
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
        #if type(ex) == gp.GPhoto2Error: #gphoto2.GPhoto2Error:
        #    pass
    if hasCamInited:
        camera_config = camera.get_config() # may print: WARNING: gphoto2: (b'_get_config [config.c:7649]') b"Type of property 'Owner Name' expected: 0x4002 got: 0x0000"
        # from CameraHandler::Init:
        #~ old_capturetarget = None
        # get the camera model
        #OK, camera_model = gp.gp_widget_get_child_by_name(
        #    camera_config, 'cameramodel')
        #if OK < gp.GP_OK:
        #    OK, camera_model = gp.gp_widget_get_child_by_name(
        #        camera_config, 'model')
        #if OK >= gp.GP_OK:
        #    camera_model = camera_model.get_value()
        #    print('Camera model:', camera_model)
        #else:
        #    print('No camera model info')
        #    camera_model = ''
        #~ camera_model = get_camera_model(camera_config)
        #if camera_model == 'unknown':
        #    # find the capture size class config item
        #    # need to set this on my Canon 350d to get preview to work at all
        #    OK, capture_size_class = gp.gp_widget_get_child_by_name(
        #        camera_config, 'capturesizeclass')
        #    if OK >= gp.GP_OK:
        #        # set value
        #        value = capture_size_class.get_choice(2)
        #        capture_size_class.set_value(value)
        #        # set config
        #        camera.set_config(camera_config)
        #else:
        #    # put camera into preview mode to raise mirror
        #    print(gp.gp_camera_capture_preview(camera)) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]
        #~ put_camera_capture_preview_mirror(camera, camera_config, camera_model)
        print(camera_config) # <Swig Object of type '_CameraWidget *' at 0x7fac9b6e53e8>
        camconfobj = get_camera_config_object(camera_config)
        with open(jsonfile, 'wb') as f: # SO:14870531
            json.dump(camconfobj, codecs.getwriter('utf-8')(f), ensure_ascii=False, indent=2)
        print("Saved config to {}; exiting.".format(jsonfile))
        sys.exit(0)
    else: # camera not inited
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)

def copyFilterCamConfJson(args):
    if (not(args.load_cam_conf_json) or not(args.save_cam_conf_json)):
        print("copyFilterCamConfJson: Sorry, unusable/empty input or output .json filename; aborting")
        sys.exit(1)

def loadSetCamConfJson(args):
    if (not(args.load_cam_conf_json)):
        print("loadSetCamConfJson: Sorry, unusable/empty output .json filename; aborting")
        sys.exit(1)
    jsonfile = os.path.realpath(args.load_cam_conf_json)
    print("loadSetCamConfJson: saving to {}".format(jsonfile))
    camera = gp.Camera()
    hasCamInited = False
    try:
        camera.init() # prints: WARNING: gphoto2: (b'gp_context_error') b'Could not detect any camera' if logging set up
        hasCamInited = True
    except Exception as ex:
        lastException = ex
        print("No camera: {} {}; ".format( type(lastException).__name__, lastException.args))
        #if type(ex) == gp.GPhoto2Error: #gphoto2.GPhoto2Error:
        #    pass
    if hasCamInited:
        camera_config = camera.get_config()
        # from CameraHandler::Init:
        old_capturetarget = None
        # # get the camera model
        # OK, camera_model = gp.gp_widget_get_child_by_name(
        #     camera_config, 'cameramodel')
        # if OK < gp.GP_OK:
        #     OK, camera_model = gp.gp_widget_get_child_by_name(
        #         camera_config, 'model')
        # if OK >= gp.GP_OK:
        #     camera_model = camera_model.get_value()
        #     print('Camera model:', camera_model)
        # else:
        #     print('No camera model info')
        #     camera_model = ''
        camera_model = get_camera_model(camera_config)
        # if camera_model == 'unknown':
        #     # find the capture size class config item
        #     # need to set this on my Canon 350d to get preview to work at all
        #     OK, capture_size_class = gp.gp_widget_get_child_by_name(
        #         camera_config, 'capturesizeclass')
        #     if OK >= gp.GP_OK:
        #         # set value
        #         value = capture_size_class.get_choice(2)
        #         capture_size_class.set_value(value)
        #         # set config
        #         camera.set_config(camera_config)
        # else:
        #     # put camera into preview mode to raise mirror
        #     print(gp.gp_camera_capture_preview(camera)) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]
        put_camera_capture_preview_mirror(camera, camera_config, camera_model)
    else: # camera not inited
        print("Sorry, no camera present, cannot execute command; exiting.")
        sys.exit(1)

def main():
    # set up logging
    logging.basicConfig(
        format='%(filename)s:%(lineno)d %(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())

    # command line argument parser
    parser = argparse.ArgumentParser(description="{} - interact with camera via python-gphoto2. Called without command line arguments, it will start a Qt GUI.".format(APPNAME))
    #mexg = parser.add_mutually_exclusive_group() # mexg.add_argument
    parser.add_argument('--save-cam-conf-json', default=argparse.SUPPRESS, help='Get and save the camera configuration to .json file, if standalone (together with --load-cam-conf-json, can be used for filtering json files). The string argument is the filename, action is aborted if standalone and no camera online, or if the argument is empty. Note that if camera is online, but mirror is not raised, process will complete with errors and fewer properties collected in json file (default: suppress)') # "%(default)s"
    parser.add_argument('--load-cam-conf-json', default=argparse.SUPPRESS, help='Load and set the camera configuration from .json file, if standalone (together with --save-cam-conf-json, can be used for filtering json files). The string argument is the filename, action is aborted if standalone and no camera online, or if the argument is empty (default: suppress)') # "%(default)s"
    parser.add_argument('--include-names-json', default=argparse.SUPPRESS, help='Comma separated list of property names to be filtered/included. If only --save-cam-conf-json, then only those properties in the list are saved in the json file; if only --load-cam-conf-json, only those properties in the list found in the file are applied to the camera; if both, the output json contains only properties in the list found in input json. Can also use `ro=0` or `ro=1` as filtering criteria; ignored if empty (default: suppress)') # "%(default)s"
    args = parser.parse_args() # in case of --help, this also prints help and exits before Qt window is raised
    #~ print(args)
    if (hasattr(args, 'save_cam_conf_json') and not(hasattr(args, 'load_cam_conf_json'))):
        getSaveCamConfJson(args)
    elif (hasattr(args, 'load_cam_conf_json') and not(hasattr(args, 'save_cam_conf_json'))):
        loadSetCamConfJson(args)
    elif (hasattr(args, 'load_cam_conf_json') and hasattr(args, 'save_cam_conf_json')):
        copyFilterCamConfJson(args)

    # start Qt Gui
    app = QtWidgets.QApplication([APPNAME]) # SO: 18133302
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


# for testing https://stackoverflow.com/questions/40683840/zooming-and-panning-an-image-in-a-qscrollarea:
# sudo apt install qtbase5-dev # installs: libgles2-mesa-dev libqt5opengl5-dev qt5-qmake qt5-qmake-bin qtbase5-dev qtbase5-dev-tools
# I have qt5-qmake-bin -> use /usr/lib/qt5/bin/qmake, else qt4 version is used!

