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
        self.okButton.clicked.connect(self.saveSettings)
        self.obj = QSettings()
        self.retriveSettings()
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
            self.notificationCheckBox.setChecked(self.settings['notifications'])
            self.voffsetSlider.setMaximum(qApp.desktop().height())
            self.voffsetSlider.setValue(self.settings['drop_topoffset'])
        except KeyError:
            pass
       
    def saveSettings(self):
        self.loadSettings()
        password = self.settings['password']
        remember = self.settings['remember_pass']
        self.obj.setValue('username',self.settings['username'])
        
        if remember:
            self.obj.setValue('password',password)
        elif self.obj.contains('password'):
            self.obj.remove('password')

        self.obj.setValue('remember_pass',remember)
        self.obj.setValue('list_size', self.settings['list_size'])
        self.obj.setValue('auto_clipboard', self.settings['auto_clipboard'])
        self.obj.setValue('notifications', self.settings['notifications'])
        self.obj.setValue('drop_topoffset', self.settings['drop_topoffset'])
        self.signals.settingsChanged.emit()

    def loadSettings(self):
        """load settings from the preferences dialog"""
        self.settings['username'] = str(self.usernameLine.text())
        self.settings['password'] = str(self.passwordLine.text())
        self.settings['remember_pass'] = self.rememberCheckBox.isChecked()
        self.settings['list_size'] = self.fileListItems.value()
        self.settings['auto_clipboard'] = self.clipboardCheckBox.isChecked()
        self.settings['notifications'] = self.notificationCheckBox.isChecked()
        self.settings['drop_topoffset'] = self.voffsetSlider.value()
        
    def retriveSettings(self):
        """Retrive the saved settings"""
        self.settings['username'] = str(self.obj.value('username').toString())
        self.settings['password'] = str(self.obj.value('password').toString())
        self.settings['remember_pass'] = self.obj.value('remember_pass').toBool()
        self.settings['list_size'] = self.obj.value('list_size').toInt()[0]
        self.settings['auto_clipboard'] = self.obj.value('auto_clipboard').toBool()
        self.settings['notifications'] = self.obj.value('notifications').toBool()
        self.settings['drop_topoffset'] = self.obj.value('drop_topoffset').toInt()[0]

    class Signals(QObject):
        settingsChanged = pyqtSignal()
