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
        self.signals = self.Signals()
        self.setAcceptDrops(1)
        self.resize(QSize(238,68))
        self.setAlignment(Qt.AlignCenter)
              
        self.trayIcon = TrayIcon()
        self.trayIcon.show()
        self.trayIcon.activated[QSystemTrayIcon.ActivationReason].connect(self.trayActivated)
        self.signals.itemDropped[str].connect(self.trayIcon.apiHandle.addItem)
        
        self.trayIcon.apiHandle.pdialog.voffsetSlider.valueChanged[int].connect(self.vmove)
        self.move(qApp.desktop().width()-227,self.trayIcon.apiHandle.pdialog.settings['drop_topoffset'])
        self.slideIn()

    def vmove(self, val):
        self.move(self.x(),val)

    def dragEnterEvent(self, event):
        if self.trayIcon.apiHandle.connected:
            event.acceptProposedAction()
            self.slideOut()

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
            self.toggle()
        elif reason == QSystemTrayIcon.Context:
            if hasattr(self.trayIcon, "deleteAction"):
                deleteCheckBox = self.trayIcon.deleteAction.widget.checkBox
                if deleteCheckBox.isChecked():
                    deleteCheckBox.toggle()

    def mousePressEvent(self, event):
        if event.x() in range(4,18):
            self.toggle()

    def slide(self, newRect):
        self.a = QPropertyAnimation(self, "geometry")
        self.a.setDuration(500)
        self.a.setStartValue(self.geometry())
        self.a.setEndValue(newRect)
        self.a.setEasingCurve(QEasingCurve.InOutQuad)
        self.a.start()          

    def slideOut(self):        
        current = self.geometry()
        new = QRect(current)
        new.moveTopLeft(QPoint(qApp.desktop().width() - 236, current.y()))
        bg = ':/bg/cloudapp_droptarget_out.png'
        self.setPixmap(QPixmap(bg))
        self.slide(new)

    def slideIn(self):
        current = self.geometry()
        new = QRect(current)
        bg = ':/bg/cloudapp_droptarget_in.png'
        self.setPixmap(QPixmap(bg))
        new.moveTopLeft(QPoint(qApp.desktop().width() - 19, current.y()))
        self.slide(new)

    def toggle(self):
        current = self.geometry()
        if current.x() > (qApp.desktop().width() - 236):
            self.slideOut()
        else:
            self.slideIn()

    class Signals(QObject):
        itemDropped = pyqtSignal(str)
