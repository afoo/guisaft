# -*- coding: utf-8 -*-
#
# This file is part of guisaft
# 
# guisaft is free software: you can redistribute it and/or modify
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


import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

try:
    import win32api
except ImportError:
    have_win32api = False
else:
    have_win32api = True

import sys
import os
import socket
from threading import Thread
from Queue import Queue

from gettext import gettext as _

from saft.client import SaftClient

OWNPATH = os.path.dirname(__file__)
    
class GuiSaftApp(object):

    GLADEFILE = os.path.join(OWNPATH, 'data/main_window.glade')

    def __init__(self):
        self.glade = gtk.glade.XML(self.GLADEFILE)
        # TODO: set labels programmaticly to facilitate i18n
        # (or use gettext with glade?)
        self.window = self.glade.get_widget('mainWindow')
        self.filechooser = self.glade.get_widget('filechooserbutton1')
        self.toEntry = self.glade.get_widget('toEntry')
        self.window.connect('destroy', self.quit)
        self.glade.signal_autoconnect({
                'on_applyButton_clicked': self.onApplyClick,
                'on_filechooserbutton1_file_set': self.onFileSet,
                })
        self.filename = None
        username = self.getUserName()
        hostname = socket.gethostname()
        self.fromaddr = '%s@%s' % (username, hostname)
        self.sendThread = None

    def quit(self, *a):
        if self.sendThread is not None:
            self.sendThread.join()
        gtk.main_quit()
        
    def getUserName(self):
        if have_win32api:
            return win32api.GetUserName()
        else:
            return os.environ.get('USER', 'unknown')
                
    def onApplyClick(self, widget):
        print 'apply button clicked!'
        toaddr = self.toEntry.get_text()
        if self.filename is None:
            self.showError(_('no file selected'))
        elif not os.path.isfile(self.filename):
            self.showError(_('%s is not a valid file') % self.filename)
        elif toaddr == '' or '@' not in toaddr:
            self.showError(_('no (valid) recipient address given'))
        else:
            sc = SaftClient(self.fromaddr, toaddr, self.filename)
            self.progressWindow = ProgressWindow(sc, self.window)

    def updateProgress(self):
        if not self.pgQueue.empty():
            self.progressBar.set_fraction(self.pgQueue.get())
            
    def onFileSet(self, widget):
        self.filename = widget.get_filename()

    def showError(self, msg):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, 
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
        dialog.run()
        dialog.destroy()


class ProgressWindow(object):

    GLADEFILE = os.path.join(OWNPATH, 'data/progress_window.glade')
    
    def __init__(self, saftClient, parent):
        self.saftClient = saftClient
        self.saftClient.addCallback(self.scCallback)
        self.glade = gtk.glade.XML(self.GLADEFILE)
        self.window = self.glade.get_widget('progressWindow')
        #self.window.parent = parent
        self.progressBar = self.glade.get_widget('progressBar')
        self.glade.signal_autoconnect({
                'on_cancelButton_clicked': self.onCancel})
        self.quitQueue = Queue()
        self.pgQueue = Queue()
        self.sendThread = SendThread(self.saftClient)
        self.sendThread.start()
        gobject.timeout_add(100, self.checkProgress)

    def onCancel(self, widget):
        self.quitQueue.put_nowait('quit')
        self.window.destroy()
        self.sendThread.join()

    def scCallback(self, progress):
        if not self.quitQueue.empty():
            return False
        self.pgQueue.put_nowait(progress)
        return True

    def checkProgress(self):
        if not self.sendThread.isAlive():
            return False
        if not self.pgQueue.empty():
            self.progressBar.set_fraction(self.pgQueue.get())
        return True
        

        
class SendThread(Thread):

    def __init__(self, sc):
        self.sc = sc
        Thread.__init__(self)

    def run(self):
        self.sc.send()


def main():
    app = GuiSaftApp()
    gtk.main()
