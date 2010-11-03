# -*- coding: utf-8 -*-

#Copyright (C)2010 Abhinandh <abhinandh@gmail.com>
#This Program in licenser under General Public License Ver 3

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from trayicon import TrayIcon

class DropWidget(QLabel):

    def __init__(self, parent=None):
        super(QWidget,self).__init__(parent)
        self.setWindowFlags(Qt.X11BypassWindowManagerHint | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.move(qApp.desktop().width() - 236, 60)
        self.signals = self.Signals()
        self.setPixmap(QPixmap(':/bg/cloudapp_droptarget.png'))
        self.setAcceptDrops(1)
        self.resize(QSize(240,68))
        self.setAlignment(Qt.AlignCenter)
              
        self.trayIcon = TrayIcon()
        self.trayIcon.show()
        self.trayIcon.activated[QSystemTrayIcon.ActivationReason].connect(self.trayActivated)
        self.signals.itemDropped[str].connect(self.trayIcon.apiHandle.addItem)
        
        self.show()
        self.slide()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        mimeData = event.mimeData()
        pos = event.pos()
        if pos.x() > 25:
            if mimeData.hasUrls():
                for url in mimeData.urls():
                    if url.scheme() in ('file', 'http','https','ftp'):
                        self.signals.itemDropped.emit(url.toString())
            
    def trayActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.slide()
        elif reason == QSystemTrayIcon.Context:
            if hasattr(self.trayIcon, "deleteAction"):
                deleteCheckBox = self.trayIcon.deleteAction.widget.checkBox
                if deleteCheckBox.isChecked():
                    deleteCheckBox.toggle()
                    
    def mousePressEvent(self, event):
        if event.x() in range(4,18):
            self.slide()
        
    def slide(self):
        current = self.geometry()
        new = QRect(current)
        if current.x() > (qApp.desktop().width() - 236):
            new.moveTopLeft(QPoint(qApp.desktop().width() - 236, current.y()))
        else:
            new.moveTopLeft(QPoint(qApp.desktop().width() - 19, current.y()))
        self.a = QPropertyAnimation(self, "geometry")
        self.a.setDuration(500)
        self.a.setStartValue(current)
        self.a.setEndValue(new)
        self.a.setEasingCurve(QEasingCurve.InOutQuad)
        self.a.start()          
    
    class Signals(QObject):
        itemDropped = pyqtSignal(str)
    
