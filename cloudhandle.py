# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licenser under General Public License Ver 3

from PyQt4.QtCore import QThread, QObject, pyqtSignal, QFileInfo, QUrl
from cloud_api import CloudApi
import urllib.parse, logging

from preferences import PreferencesDialog

class CloudHandle(object):
    
    fileList = []
    
    def __init__(self):
        self.pdialog = PreferencesDialog()
        self.pdialog.signals.settingsChanged.connect(self.initializeApi)
        self.signals = self.Signals()
        self.initializeApi()

    def initializeApi(self):
        self.connected = False
        try:
            username = self.pdialog.settings['username']
            password = self.pdialog.settings['password']
            if username == '' or password == '':
               raise ValueError('Empty password or username')
            self.api = CloudApi(username, password)
            self.getFileList()
        except (KeyError, ValueError):
            self.pdialog.show()
            logging.warn("Couldn't reading settings")
        
    def getFileList(self):
        self.api.getFileList(self.pdialog.settings['list_size'], self.gotFileList)
        
    def gotFileList(self, l):
        self.connected = True
        self.fileList = l
        self.signals.gotFileList.emit(l)
        
    def addItem(self, url):
        url = str(url)
        if urllib.parse.urlparse(url).scheme == "file":
            self.api.uploadFile(url, self.itemAdded)
        else:
            self.api.bookmark(url, self.itemAdded)
        self.signals.uploadStarted.emit()
            
    def itemAdded(self, item):
        self.fileList.insert(0, item)
        self.fileList.pop()
        self.signals.gotFileList.emit(self.fileList)
        if self.pdialog.settings['auto_clipboard']:
            self.signals.loadClipboard.emit(item['url'])
        if self.pdialog.settings['notifications']:
            if item['item_type'] == 'bookmark':
                self.notify('Bookmarked - '+item['name'], item['url'])
            else:
                self.notify('File Uploaded - '+item['name'], item['url'])
        self.signals.uploadFinished.emit()
        
    def deleteItem(self, url):
        url = str(url)
        self.api.delete(url, self.deleted)
        
    def deleted(self, x):
        self.getFileList()
        if self.pdialog.settings['notifications']:
            self.notify("Deleted - "+x['name'], 'This item was removed from your CloudApp')

    def showPreferences(self):
        self.pdialog.show()
        
    def notify(self, title, text, icon="dialog-information"):
        try:
            from gi.repository import Notify as pynotify
            if pynotify.init("Cloud App"):
                n = pynotify.Notification.new(title, text, icon)
                n.set_timeout(5)
                n.show()
            else:
                logging.error("there was a problem initializing the pynotify module")
        except:
            logging.info("you don't seem to have pynotify installed")
        
        
    class Signals(QObject):
        gotFileList = pyqtSignal(list)
        loadClipboard = pyqtSignal(str)
        uploadStarted = pyqtSignal()
        uploadFinished = pyqtSignal()
