#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

import gphoto2 as gp

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        self.do_init = QtCore.QEvent.registerEventType()
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Camera config")
        self.setMinimumWidth(600)
        # quit shortcut
        quit_action = QtGui.QAction('Quit', self)
        quit_action.setShortcuts(['Ctrl+Q', 'Ctrl+W'])
        quit_action.triggered.connect(QtGui.qApp.closeAllWindows)
        self.addAction(quit_action)
        # defer full initialisation (slow operation) until gui is visible
        QtGui.QApplication.postEvent(
            self, QtCore.QEvent(self.do_init), Qt.LowEventPriority - 1)

    def event(self, event):
        if event.type() != self.do_init:
            return QtGui.QMainWindow.event(self, event)
        event.accept()
        QtGui.QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.initialise()
        finally:
            QtGui.QApplication.restoreOverrideCursor()
        return True

    def initialise(self):
        # get camera config tree
        camera = gp.check_result(gp.gp_camera_new())
        context = gp.gp_context_new()
        gp.check_result(gp.gp_camera_init(camera, context))
        camera_config = gp.check_result(
            gp.gp_camera_get_config(camera, context))
        # create corresponding tree of tab widgets
        self.setWindowTitle(
            gp.check_result(gp.gp_widget_get_label(camera_config)))
        self.setCentralWidget(config_widget(camera_config))

class config_widget(QtGui.QWidget):
    def __init__(self, camera_config, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QFormLayout())
        child_count = gp.check_result(gp.gp_widget_count_children(camera_config))
        if child_count < 1:
            return
        tabs = None
        for n in range(child_count):
            child = gp.check_result(gp.gp_widget_get_child(camera_config, n))
            label = gp.check_result(gp.gp_widget_get_label(child))
            child_type = gp.check_result(gp.gp_widget_get_type(child))
            if child_type == gp.GP_WIDGET_SECTION:
                if not tabs:
                    tabs = QtGui.QTabWidget()
                    self.layout().insertRow(0, tabs)
                tabs.addTab(config_widget(child), label)
            elif child_type == gp.GP_WIDGET_TEXT:
                widget = QtGui.QLineEdit()
                value = gp.check_result(gp.gp_widget_get_value_text(child))
                if value:
                    widget.setText(value)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_RANGE:
                lo, hi, inc = gp.check_result(gp.gp_widget_get_range(child))
                value = gp.check_result(gp.gp_widget_get_value_float(child))
                widget = QtGui.QSlider(Qt.Horizontal)
                widget.setRange(int(lo * 1000.0), int(hi * 1000.0))
                widget.setSingleStep(int(inc * 1000.0))
                widget.setValue(value * 1000.0)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_TOGGLE:
                widget = QtGui.QCheckBox()
                value = gp.check_result(gp.gp_widget_get_value_int(child))
                widget.setChecked(value != 0)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_RADIO:
                widget = QtGui.QWidget()
                widget.setLayout(QtGui.QHBoxLayout())
                value = gp.check_result(gp.gp_widget_get_value_text(child))
                choice_count = gp.check_result(gp.gp_widget_count_choices(child))
                for n in range(choice_count):
                    choice = gp.check_result(gp.gp_widget_get_choice(child, n))
                    if choice:
                        button = QtGui.QRadioButton(choice)
                        widget.layout().addWidget(button)
                        if choice == value:
                            button.setChecked(True)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_MENU:
                widget = QtGui.QComboBox()
                value = gp.check_result(gp.gp_widget_get_value_text(child))
                choice_count = gp.check_result(gp.gp_widget_count_choices(child))
                for n in range(choice_count):
                    choice = gp.check_result(gp.gp_widget_get_choice(child, n))
                    if choice:
                        widget.addItem(choice)
                        if choice == value:
                            widget.setCurrentIndex(n)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_BUTTON:
                widget = QtGui.QPushButton()
                self.layout().addRow(label, widget)
            else:
                print 'Cannot make widget type %d for %s' % (child_type, label)

if __name__ == "__main__":
    app = QtGui.QApplication([])
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
