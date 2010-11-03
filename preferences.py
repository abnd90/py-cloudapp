# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licensed under General Public License Ver 3

from preferencesui import Ui_Properties
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class PreferencesDialog(QDialog, Ui_Properties):
    settings = {}
    def __init__(self, parent=None):
        super(PreferencesDialog, self).__init__(parent)
        self.setupUi(self)
        self.signals = self.Signals()
        self.setWindowTitle('Preferences')
        self.okButton.clicked.connect(self.saveSettings)
        self.obj = QSettings()
        self.getSettings()
        QCoreApplication.setOrganizationName("Abhinandh")
        QCoreApplication.setOrganizationDomain("abhinandh.com")
        QCoreApplication.setApplicationName("Cloud App")


    def showEvent(self, event):
        try:
            self.usernameLine.setText(self.settings['username'])
            self.passwordLine.setText(self.settings['password'])
            self.rememberCheckBox.setChecked(self.settings['remember_pass'])
            self.fileListItems.setValue(self.settings['list_size'])
            self.clipboardCheckBox.setChecked(self.settings['auto_clipboard'])
        except KeyError:
            pass
       
    def saveSettings(self):
        self.obj.setValue('username',self.usernameLine.text())
        self.obj.setValue('password',self.passwordLine.text())
        self.obj.setValue('remember_pass',self.rememberCheckBox.isChecked())
        self.obj.setValue('list_size', self.fileListItems.value())
        self.obj.setValue('auto_clipboard', self.clipboardCheckBox.isChecked())
        self.getSettings()
        self.signals.settingsChanged.emit()

    def getSettings(self):
        self.settings['username'] = str(self.obj.value('username').toString())
        self.settings['password'] = str(self.obj.value('password').toString())
        self.settings['remember_pass'] = self.obj.value('remember_pass').toBool()
        self.settings['list_size'] = self.obj.value('list_size').toInt()[0]
        self.settings['auto_clipboard'] = self.obj.value('auto_clipboard').toBool()

    class Signals(QObject):
        settingsChanged = pyqtSignal()
