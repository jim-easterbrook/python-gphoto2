#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

from __future__ import print_function

from datetime import datetime
import logging
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
        # main widget
        widget = QtGui.QWidget()
        widget.setLayout(QtGui.QGridLayout())
        widget.layout().setColumnStretch(0, 1)
        self.setCentralWidget(widget)
        # 'apply' button
        self.apply_button = QtGui.QPushButton('apply changes')
        self.apply_button.setEnabled(False)
        self.apply_button.clicked.connect(self.apply_changes)
        widget.layout().addWidget(self.apply_button, 1, 1)
        # 'cancel' button
        quit_button = QtGui.QPushButton('cancel')
        quit_button.clicked.connect(QtGui.qApp.closeAllWindows)
        widget.layout().addWidget(quit_button, 1, 2)
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
        self.camera = gp.check_result(gp.gp_camera_new())
        self.context = gp.gp_context_new()
        gp.check_result(gp.gp_camera_init(self.camera, self.context))
        self.camera_config = gp.check_result(
            gp.gp_camera_get_config(self.camera, self.context))
        # create corresponding tree of tab widgets
        self.setWindowTitle(
            gp.check_result(gp.gp_widget_get_label(self.camera_config)))
        self.centralWidget().layout().addWidget(SectionWidget(
            self.config_changed, self.camera_config), 0, 0, 1, 3)

    def config_changed(self):
        self.apply_button.setEnabled(True)

    def apply_changes(self):
        gp.check_result(gp.gp_camera_set_config(
            self.camera, self.camera_config, self.context))
        QtGui.qApp.closeAllWindows()

class SectionWidget(QtGui.QWidget):
    def __init__(self, config_changed, camera_config, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setLayout(QtGui.QFormLayout())
        if gp.check_result(gp.gp_widget_get_readonly(camera_config)):
            self.setDisabled(True)
        child_count = gp.check_result(gp.gp_widget_count_children(camera_config))
        if child_count < 1:
            return
        tabs = None
        for n in range(child_count):
            child = gp.check_result(gp.gp_widget_get_child(camera_config, n))
            label = gp.check_result(gp.gp_widget_get_label(child))
            name = gp.check_result(gp.gp_widget_get_name(child))
            label = '{} ({})'.format(label, name)
            child_type = gp.check_result(gp.gp_widget_get_type(child))
            if child_type == gp.GP_WIDGET_SECTION:
                if not tabs:
                    tabs = QtGui.QTabWidget()
                    self.layout().insertRow(0, tabs)
                tabs.addTab(SectionWidget(config_changed, child), label)
            elif child_type == gp.GP_WIDGET_TEXT:
                self.layout().addRow(label, TextWidget(config_changed, child))
            elif child_type == gp.GP_WIDGET_RANGE:
                self.layout().addRow(label, RangeWidget(config_changed, child))
            elif child_type == gp.GP_WIDGET_TOGGLE:
                self.layout().addRow(label, ToggleWidget(config_changed, child))
            elif child_type == gp.GP_WIDGET_RADIO:
                choice_count = gp.check_result(gp.gp_widget_count_choices(
                    child))
                if choice_count > 3:
                    widget = MenuWidget(config_changed, child)
                else:
                    widget = RadioWidget(config_changed, child)
                self.layout().addRow(label, widget)
            elif child_type == gp.GP_WIDGET_MENU:
                self.layout().addRow(label, MenuWidget(config_changed, child))
            elif child_type == gp.GP_WIDGET_DATE:
                self.layout().addRow(label, DateWidget(config_changed, child))
            else:
                print('Cannot make widget type %d for %s' % (child_type, label))

class TextWidget(QtGui.QLineEdit):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        value = gp.check_result(gp.gp_widget_get_value(config))
        if value:
            self.setText(value)
        self.editingFinished.connect(self.new_value)

    def new_value(self):
        value = str(self.text())
        gp.check_result(gp.gp_widget_set_value(self.config, value))
        self.config_changed()

class RangeWidget(QtGui.QSlider):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QSlider.__init__(self, Qt.Horizontal, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        lo, hi, self.inc = gp.check_result(gp.gp_widget_get_range(config))
        value = gp.check_result(gp.gp_widget_get_value(config))
        self.setRange(int(lo * self.inc), int(hi * self.inc))
        self.setValue(int(value * self.inc))
        self.sliderReleased.connect(self.new_value)

    def new_value(self):
        value = float(self.value()) * self.inc
        gp.check_result(gp.gp_widget_set_value(self.config, value))
        self.config_changed()

class ToggleWidget(QtGui.QCheckBox):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QCheckBox.__init__(self, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        value = gp.check_result(gp.gp_widget_get_value(config))
        self.setChecked(value != 0)
        self.clicked.connect(self.new_value)

    def new_value(self):
        value = self.isChecked()
        gp.check_result(gp.gp_widget_set_value(self.config, (0, 1)[value]))
        self.config_changed()

class RadioWidget(QtGui.QWidget):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        self.setLayout(QtGui.QHBoxLayout())
        value = gp.check_result(gp.gp_widget_get_value(config))
        choice_count = gp.check_result(gp.gp_widget_count_choices(config))
        self.buttons = []
        for n in range(choice_count):
            choice = gp.check_result(gp.gp_widget_get_choice(config, n))
            if choice:
                button = QtGui.QRadioButton(choice)
                self.layout().addWidget(button)
                if choice == value:
                    button.setChecked(True)
                self.buttons.append((button, choice))
                button.clicked.connect(self.new_value)

    def new_value(self):
        for button, choice in self.buttons:
            if button.isChecked():
                gp.check_result(gp.gp_widget_set_value(self.config, choice))
                self.config_changed()
                return

class MenuWidget(QtGui.QComboBox):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        value = gp.check_result(gp.gp_widget_get_value(config))
        choice_count = gp.check_result(gp.gp_widget_count_choices(config))
        for n in range(choice_count):
            choice = gp.check_result(gp.gp_widget_get_choice(config, n))
            if choice:
                self.addItem(choice)
                if choice == value:
                    self.setCurrentIndex(n)
        self.currentIndexChanged.connect(self.new_value)

    def new_value(self, value):
        value = str(self.itemText(value))
        gp.check_result(gp.gp_widget_set_value(self.config, value))
        self.config_changed()

class DateWidget(QtGui.QDateTimeEdit):
    def __init__(self, config_changed, config, parent=None):
        QtGui.QDateTimeEdit.__init__(self, parent)
        self.config_changed = config_changed
        self.config = config
        if gp.check_result(gp.gp_widget_get_readonly(config)):
            self.setDisabled(True)
        assert gp.check_result(gp.gp_widget_count_children(config)) == 0
        value = gp.check_result(gp.gp_widget_get_value(config))
        if value:
            self.setDateTime(datetime.fromtimestamp(value))
        self.dateTimeChanged.connect(self.new_value)
        self.setDisplayFormat('yyyy-MM-dd hh:mm:ss')

    def new_value(self, value):
        value = value.toPyDateTime() - datetime.fromtimestamp(0)
        value = int(value.total_seconds())
        gp.check_result(gp.gp_widget_set_value(self.config, value))
        self.config_changed()

if __name__ == "__main__":
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    app = QtGui.QApplication([])
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
