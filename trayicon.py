# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licenser under General Public License Ver 3

from PyQt4.QtGui import *
from PyQt4.QtCore import QString, QThread, QFileInfo, QUrl, QObject, pyqtSignal, QFileInfo

from cloudhandle import CloudHandle
import icons_rc

class TrayIcon(QSystemTrayIcon):
    
    fileList = []
    
    def __init__(self,parent = None):
        super(QSystemTrayIcon,self).__init__(parent)
        self.createContextMenu()
        self.signals = self.Signals()
        self.apiHandle = CloudHandle()
        self.connectActions()
        self.deleteAction = DeleteAction()
        self.noOfUploads = 0    
        self.setIcon(QIcon(":/icons/icons/icon.png"))
        self.setToolTip("Cloud App")
        
    def createContextMenu(self):
        self.contextMenu = QMenu()

        self.quitAction = QAction(QIcon(":/icons/icons/quit.png"), "Quit",self.contextMenu)
        self.prefAction = QAction(QIcon(":/icons/icons/preferences.png"), "Preferences",self.contextMenu)
        self.reloadAction = QAction(QIcon(":/icons/icons/reload.png"), "Reload",self.contextMenu)
        self.openWebAction = QAction(QIcon(":/icons/icons/web-interface.png"), "Open Web Interface",self.contextMenu)
        self.fileListMenu = QMenu("Loading File list...")
        self.fileListMenu.setIcon(QIcon(":/icons/icons/list-unordered.png"))
        self.fileListMenu.setEnabled(0)
        self.uploadStatus = QAction("",self.contextMenu)
        self.uploadStatus.setEnabled(0)
        self.uploadStatus.setVisible(0)
        self.queueStatus = QAction("",self.contextMenu)
        self.queueStatus.setEnabled(0)
        self.queueStatus.setVisible(0)

        self.contextMenu.addAction(self.uploadStatus)
        self.contextMenu.addAction(self.queueStatus)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.openWebAction)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.reloadAction)
        self.contextMenu.addMenu(self.fileListMenu)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.prefAction)
        self.contextMenu.addAction(self.quitAction)
        self.setContextMenu(self.contextMenu)

    def connectActions(self):
        self.quitAction.triggered.connect(qApp.quit)
        self.openWebAction.triggered.connect(self.openWebInterface)
        self.fileListMenu.triggered[QAction].connect(self.menuItemClicked)
        self.signals.delete[str].connect(self.apiHandle.deleteItem)
        self.prefAction.triggered.connect(self.apiHandle.showPreferences)
        self.apiHandle.signals.gotFileList[list].connect(self.populateFileList)
        self.apiHandle.signals.loadClipboard[str].connect(self.loadClipboardText)
        self.apiHandle.signals.uploadStarted.connect(self.uploadStatusAdd)
        self.apiHandle.signals.uploadFinished.connect(self.uploadStatusRemove)

    def populateFileList(self, fileList):
        #PyQt converts all Strings to QStrings, converting back.
        l = []
        for item in fileList:
            m = {}   
            for key in item:
                m[str(key)] = str(item[key])
            l.append(m)
        
        self.fileList = l
        self.fileListMenu.clear()
        self.fileListMenu.setTitle("File List")
        self.fileListMenu.setEnabled(1)
        
        for item in self.fileList:
            newAction = QAction(self)
            text = item["name"]
            newAction.setText(text[:20] + ('...' if len(text) > 20 else ''))
            newAction.setIcon(QIcon(":/icons/icons/" + QFileInfo(item["icon"]).fileName()))
            self.fileListMenu.addAction(newAction)
            item["action"] = newAction

        self.fileListMenu.addAction(self.deleteAction)

    def menuItemClicked(self, action):
        """Slot for click on file list actions"""
        for item in self.fileList:
            if item["action"] == action:
                deleteCheckBox = self.deleteAction.widget.checkBox
                if deleteCheckBox.isChecked():
                    self.signals.delete.emit(item["href"])
                else:
                    self.loadClipboardText(item["url"])
                break

    def loadClipboardText(self, text):
        """Loads the text into clipboard"""
        text = str(text)
        clipboard = qApp.clipboard()
        clipboard.setText(text)

    def openWebInterface(self):
        QDesktopServices().openUrl(QUrl('http://my.cl.ly'))

    def uploadStatusAdd(self):
        self.uploadStatus.setVisible(1)
        self.noOfUploads += 1
        text = "Adding "+ str(self.noOfUploads) + " File(s)." 
        self.uploadStatus.setText(text)

    def uploadStatusRemove(self):
        self.noOfUploads -= 1
        if self.noOfUploads == 0:
            self.uploadStatus.setVisible(0)
        else:
            text = "Adding "+ str(self.noOfUploads) + " File(s)." 
            self.uploadStatus.setText(text)


    class Signals(QObject):
        delete = pyqtSignal(str)


class DeleteAction(QWidgetAction):
    def __init__(self, parent=None):
        super(DeleteAction, self).__init__(parent)
        self.widget = DeleteActionWidget()
        self.setDefaultWidget(self.widget)
        
class DeleteActionWidget(QWidget):
    def __init__(self, parent=None):
        super(DeleteActionWidget, self).__init__(parent)
        self.checkBox = QCheckBox()
        self.checkBox.setFixedSize(32,32)
        
        self.label = QLabel('Delete')
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.checkBox)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
