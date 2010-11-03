# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licenser under General Public License Ver 3

from PyQt4.QtCore import QThread, QObject, pyqtSignal, QFileInfo, QString, QUrl
from cloud_api import CloudApi
import urlparse

from preferences import PreferencesDialog

class CloudHandle(object):
    
    fileList = []
    
    def __init__(self):
        self.pdialog = PreferencesDialog()
        self.pdialog.signals.settingsChanged.connect(self.initializeApi)
        self.signals = self.Signals()
        self.initializeApi()

    def initializeApi(self):
        try:
            username = self.pdialog.settings['username']
            password = self.pdialog.settings['password']
            self.api = CloudApi(username, password)
            self.getFileList()
        except KeyError:
            self.pdialog.show()
            print "Couldn't read the settings"
        
        
    def getFileList(self):
        self.api.getFileList(self.pdialog.settings['list_size'], self.gotFileList)
        
    def gotFileList(self, l):
        self.fileList = l
        self.signals.gotFileList.emit(l)
        
    def addItem(self, url):
        url = str(url)
        if urlparse.urlparse(url).scheme == "file":
            self.api.uploadFile(url, self.itemAdded)
        else:
            self.api.bookmark(url, self.itemAdded)
            
    def itemAdded(self, item):
        self.fileList.insert(0, item)
        self.fileList.pop()
        self.signals.gotFileList.emit(self.fileList)
        if self.pdialog.settings['auto_clipboard']:
            self.signals.loadClipboard(item['url'])
        
    def deleteItem(self, url):
        url = str(url)
        self.api.delete(url, self.deleted)
        
    def deleted(self, x):
        self.getFileList()

    def showPreferences(self):
        self.pdialog.show()
        
    class Signals(QObject):
        gotFileList = pyqtSignal(list)
        loadClipboard = pyqtSignal(str)
