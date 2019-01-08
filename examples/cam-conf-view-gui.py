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
# started: sdaau 2019, on with python3-gphoto2, Ubuntu 18.04
# uses camera-config-gui-oo.py, focus-gui.py

from __future__ import print_function

from datetime import datetime
import io
import logging
import math
import sys, os

from PIL import Image, ImageChops, ImageStat

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import gphoto2 as gp

THISSCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1,THISSCRIPTDIR)
ccgoo = __import__('camera-config-gui-oo')
fg = __import__('focus-gui')

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
        self.save_action.setShortcuts(['Ctrl+S', 'Ctrl+W'])
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
        self.dopreview_action.setShortcuts(['Ctrl+P'])
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
        #~ quit_button = QtWidgets.QPushButton('cancel')
        #~ quit_button.clicked.connect(QtWidgets.qApp.closeAllWindows)
        #~ widget.layout().addWidget(quit_button, 1, 2)


    class ScrollAreaWheel(QtWidgets.QScrollArea): # SO:9475772
        def __init__(self, parent=None):
            super(MainWindow.ScrollAreaWheel, self).__init__(parent)
            self.parent = parent
        def wheelEvent(self, event):
            super(MainWindow.ScrollAreaWheel, self).wheelEvent(event)
            self.wheelDelta = 1 if (event.angleDelta().y() > 0) else -1
            #~ print("wheelEvent", event.angleDelta()) # PyQt5.QtCore.QPoint(0, 120) or (0, -120)
            #print("wheelEvent", event.pixelDelta()) # PyQt5.QtCore.QPoint()
            print("wheelEvent", self.wheelDelta)

    def replicate_fg_viewer(self):
        # image display area
        self.image_display = MainWindow.ScrollAreaWheel(self) # QtWidgets.QScrollArea()
        self.image_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.image_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.imgwid = fg.ImageWidget()
        #self.id_layout = QtWidgets.QHBoxLayout(self.image_display)
        self.id_layout = QtWidgets.QGridLayout(self.image_display)
        self.image_display.setWidget(self.id_layout.widget())
        #self.image_display.setWidget(self.imgwid)
        self.image_display.setWidgetResizable(True)
        self.image_display.setAlignment(Qt.AlignCenter)
        self.id_layout.addWidget(self.imgwid, 0, 0, Qt.AlignCenter)
        # (QWidget * widget, int fromRow, int fromColumn, int rowSpan, int columnSpan, Qt::Alignment alignment = 0)
        # If rowSpan and/or columnSpan is -1, then the widget will extend to the bottom and/or right edge, respectively.
        #~ print("AO: {} {}".format( self.contentview.frameGeometry().width(), self.contentview.frameGeometry().height() ) ) # 640 480?
        #~ print("AO: {} {}".format( self.contentview.geometry().width(), self.contentview.geometry().height() ) ) # 640 480?
        #~ screenShape = QtWidgets.QDesktopWidget().screenGeometry() # 1366 768
        #~ print("AO: {} {}".format( screenShape.width(), screenShape.height() ) )
        #~ self.contentview.layout().addWidget(self.image_display, 0, 0)#, 1, 1) #, Qt.AlignCenter)
        self.contentview.layout().addWidget(self.image_display) #, 0, 0) #, Qt.AlignCenter)
        #self.contentview.layout().setAlignment(self.image_display, Qt.AlignCenter)

        self.new_image_sig.connect(self.new_image)
        #self.contentview.triggered.connect(self.zoom_original)

    #~ def onContentViewResize(self, event):
        #~ print(event.size())

    def __init__(self):
        self.current_splitter_style=0
        self.do_init = QtCore.QEvent.registerEventType()
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Camera config cam-conf-view-gui.py")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
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
        #~ self.frameviewlayout = QtWidgets.QHBoxLayout(self.frameview)
        self.frameviewlayout = QtWidgets.QGridLayout(self.frameview)
        self.frameviewlayout.setSpacing(0);
        self.frameviewlayout.setContentsMargins(0,0,0,0);
        self.contentview = QtWidgets.QWidget()
        self.contentview.setLayout(QtWidgets.QGridLayout())
        #~ self.contentview.resizeEvent = self.onContentViewResize
        self.frameviewlayout.addWidget(self.contentview)
        self.replicate_fg_viewer()

        self.frameconf = QtWidgets.QFrame(self)
        self.frameconf.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameconf.setStyleSheet("padding: 0;") # nope
        self.frameconflayout = QtWidgets.QHBoxLayout(self.frameconf)
        self.frameconflayout.setSpacing(0);
        self.frameconflayout.setContentsMargins(0,0,0,0);
        self.scrollconf = QtWidgets.QScrollArea(self)
        self.scrollconf.setWidgetResizable(True)
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
        self.camera = gp.Camera()
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_init), Qt.LowEventPriority - 1)

    def getSizeToFit(self, inwfit, inhfit, inworig, inhorig):
        if (inhfit > inwfit):
            neww, newh = int(inwfit), int(inhorig*(inwfit/inworig))
        else:
            neww, newh = int(inworig*(inhfit/inhorig)), int(inhfit)
        return neww, newh

    def event(self, event):
        if event.type() != self.do_init:
            return QtWidgets.QMainWindow.event(self, event)
        event.accept()
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        #print("AO: {} {}".format( self.contentview.frameGeometry().width(), self.contentview.frameGeometry().height() ) ) # 187 258, OK
        # set initial size
        inwfit, inhfit = self.contentview.frameGeometry().width(), self.contentview.frameGeometry().height()
        # just start with arbitrary known aspect ratio
        neww, newh = self.getSizeToFit(inwfit, inhfit, 640, 480)
        self.imgwid.resize(neww, newh)
        try:
            self.initialise()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        return True

    def CameraHandlerInit(self):
        # get camera config tree
        self.camera.init()
        self.camera_config = self.camera.get_config()
        # from CameraHandler::Init:
        self.old_capturetarget = None
        # get the camera model
        OK, camera_model = gp.gp_widget_get_child_by_name(
            self.camera_config, 'cameramodel')
        if OK < gp.GP_OK:
            OK, camera_model = gp.gp_widget_get_child_by_name(
                self.camera_config, 'model')
        if OK >= gp.GP_OK:
            self.camera_model = camera_model.get_value()
            print('Camera model:', self.camera_model)
        else:
            print('No camera model info')
            self.camera_model = ''
        if self.camera_model == 'unknown':
            # find the capture size class config item
            # need to set this on my Canon 350d to get preview to work at all
            OK, capture_size_class = gp.gp_widget_get_child_by_name(
                self.camera_config, 'capturesizeclass')
            if OK >= gp.GP_OK:
                # set value
                value = capture_size_class.get_choice(2)
                capture_size_class.set_value(value)
                # set config
                self.camera.set_config(self.camera_config)
        else:
            # put camera into preview mode to raise mirror
            print(gp.gp_camera_capture_preview(self.camera)) # [0, <Swig Object of type 'CameraFile *' at 0x7fb5a0044a40>]

    def initialise(self):
        #~ # get camera config tree
        #~ self.camera.init()
        #~ self.camera_config = self.camera.get_config()
        self.CameraHandlerInit()
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
        print("zoom_original")

    def zoom_fit_view(self):
        print("zoom_fit_view")

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
        print("switch_splitter_layout")
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
        w, h = image.size
        image_data = image.tobytes('raw', 'RGB')
        self.q_image = QtGui.QImage(image_data, w, h, QtGui.QImage.Format_RGB888)
        self._draw_image()
        #~ # generate histogram and count clipped pixels
        #~ histogram = image.histogram()
        #~ q_image = QtGui.QImage(100, 256, QtGui.QImage.Format_RGB888)
        #~ q_image.fill(Qt.white)
        #~ clipping = []
        #~ start = 0
        #~ for colour in (0xff0000, 0x00ff00, 0x0000ff):
            #~ stop = start + 256
            #~ band_hist = histogram[start:stop]
            #~ max_value = float(1 + max(band_hist))
            #~ for x in range(len(band_hist)):
                #~ y = float(1 + band_hist[x]) / max_value
                #~ #y = 98.0 * max(0.0, 1.0 + (math.log10(y) / 5.0))
                #~ q_image.setPixel(y,     x, colour)
                #~ q_image.setPixel(y + 1, x, colour)
            #~ #clipping.append(band_hist[-1])
            #~ start = stop
        #~ pixmap = QtGui.QPixmap.fromImage(q_image)
        #~ self.histogram_display.setPixmap(pixmap)
        #~ self.clipping_display.setText(
            #~ ', '.join(map(lambda x: '{:d}'.format(x), clipping)))
        #~ # measure focus by summing inter-pixel differences
        #~ shifted = ImageChops.offset(image, 1, 0)
        #~ diff = ImageChops.difference(image, shifted).crop((1, 0, w, h))
        #~ stats = ImageStat.Stat(diff)
        #~ h_rms = stats.rms
        #~ shifted = ImageChops.offset(image, 0, 1)
        #~ diff = ImageChops.difference(image, shifted).crop((0, 1, w, h))
        #~ stats = ImageStat.Stat(diff)
        #~ rms = stats.rms
        #~ for n in range(len(rms)):
            #~ rms[n] += h_rms[n]
        #~ # "auto-ranging" of focus measurement
        #~ while self.focus_scale < 1.0e12 and (max(rms) * self.focus_scale) < 1.0:
            #~ self.focus_scale *= 10.0
            #~ print('+', self.focus_scale)
        #~ while self.focus_scale > 1.0e-12 and (max(rms) * self.focus_scale) > 100.0:
            #~ self.focus_scale /= 10.0
            #~ print('-', self.focus_scale)
        #~ self.focus_display.setText(
            #~ ', '.join(map(lambda x: '{:.2f}'.format(x * self.focus_scale), rms)))

    def _draw_image(self):
        if not self.q_image:
            return
        pixmap = QtGui.QPixmap.fromImage(self.q_image)
        #~ if not self.zoomed:
            #~ pixmap = pixmap.scaled(
                #~ self.image_display.viewport().size(),
                #~ Qt.KeepAspectRatio, Qt.SmoothTransformation)
        pixmap = pixmap.scaled(
            self.image_display.viewport().size(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #~ self.image_display.widget().setPixmap(pixmap)
        #~ self.id_layout.widget().setPixmap(pixmap)
        self.imgwid.setPixmap(pixmap)

    def my_wheelEvent(self, event):
        #self.zoom += event.angleDelta().y()/2880
        #self.view.scale(self.zoom, self.zoom)
        print("wheelEvent")

if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


