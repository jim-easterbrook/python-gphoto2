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
# uses camera-config-gui-oo.py

from __future__ import print_function

from datetime import datetime
import logging
import sys, os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import gphoto2 as gp

THISSCRIPTDIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1,THISSCRIPTDIR)
ccgoo = __import__('camera-config-gui-oo')

class MainWindow(QtWidgets.QMainWindow):
    quit_action = None

    def set_splitter(self, inqtsplittertype, inwidget1, inwidget2):
        self.splitter1 = QtWidgets.QSplitter(Qt.Horizontal)
        self.splitter1.addWidget(inwidget1)
        self.splitter1.addWidget(inwidget2)

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
        self.switchlayout_action.setShortcuts(['Ctrl-A'])
        self.switchlayout_action.triggered.connect(self.switch_layout)
        self.viewMenu.addAction(self.zoomorig_action)
        self.viewMenu.addAction(self.zoomfitview_action)
        self.viewMenu.addAction(self.switchlayout_action)

    def __init__(self):
        self.do_init = QtCore.QEvent.registerEventType()
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Camera config cam-conf-view-gui.py")
        self.setMinimumWidth(600)
        # quit shortcut
        self.quit_action = QtWidgets.QAction('Quit', self)
        self.quit_action.setShortcuts(['Ctrl+Q', 'Ctrl+W'])
        self.quit_action.setStatusTip('Exit application')
        self.quit_action.triggered.connect(QtWidgets.qApp.closeAllWindows)
        self.addAction(self.quit_action)
        # main menu
        self.create_main_menu()
        # main widget
        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(QtWidgets.QGridLayout())
        self.setCentralWidget(self.widget)
        # frames
        self.frameview = QtWidgets.QFrame(self)
        self.frameview.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameconf = QtWidgets.QFrame(self)
        self.frameconf.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameconf.setStyleSheet("padding: 0;")
        self.frameconflayout = QtWidgets.QHBoxLayout(self.frameconf)
        self.frameconflayout.setSpacing(0);
        self.frameconflayout.setContentsMargins(0,0,0,0);
        self.scrollconf = QtWidgets.QScrollArea(self)
        self.scrollconf.setWidgetResizable(True)
        self.contentconf = QtWidgets.QWidget()
        self.scrollconf.setWidget(self.contentconf)
        self.frameconflayout.addWidget(self.scrollconf)

        self.set_splitter(Qt.Horizontal, self.frameview, self.frameconf)
        self.widget.layout().addWidget(self.splitter1, 1, 1)
        self.widget.layout().setContentsMargins(2,2,2,2);

        # defer full initialisation (slow operation) until gui is visible
        self.camera = gp.Camera()
        QtWidgets.QApplication.postEvent(
            self, QtCore.QEvent(self.do_init), Qt.LowEventPriority - 1)

    def event(self, event):
        if event.type() != self.do_init:
            return QtWidgets.QMainWindow.event(self, event)
        event.accept()
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.initialise()
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        return True

    def initialise(self):
        # get camera config tree
        self.camera.init()
        self.camera_config = self.camera.get_config()
        # create corresponding tree of tab widgets
        self.setWindowTitle(self.camera_config.get_label())
        #~ self.centralWidget().layout().addWidget(SectionWidget(
            #~ self.config_changed, self.camera_config), 0, 0, 1, 3)

    def config_changed(self):
        self.apply_button.setEnabled(True)

    def apply_changes(self):
        self.camera.set_config(self.camera_config)
        QtWidgets.qApp.closeAllWindows()

    def load_settings(self):
        print("load_settings")

    def save_settings(self):
        print("save_settings")

    def zoom_original(self):
        print("zoom_original")

    def zoom_fit_view(self):
        print("zoom_fit_view")

    def switch_layout(self):
        print("switch_layout")


if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    app = QtWidgets.QApplication([])
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


