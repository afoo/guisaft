#!/usr/bin/env python
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

# major TODO: add i18n

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

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

from gettext import gettext as _

from saft.client import SaftClient

class GuiSaftApp(object):

    MAINWIN_GLADEFILE = './guisaft.glade'
    SENDWIN_GLADEFILE = ''

    def __init__(self):
        self.glade = gtk.glade.XML(self.MAINWIN_GLADEFILE)
        # TODO: set labels programmaticly to facilitate i18n
        self.window = self.glade.get_widget('window1')
        self.filechooser = self.glade.get_widget('filechooserbutton1')
        self.toEntry = self.glade.get_widget('toEntry') # TODO: actually change the control to have that name
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
        elif toaddr = '' or '@' not in toaddr:
            self.showError(_('no (valid) recipient address given'))
        else:
            sc = SaftCient(self.fromaddr, toaddr, self.filename, self.progressCallback)
            self.sendThread = SendThread(sc)
            self.sendthread.start()
            
    def onFileSet(self, widget):
        self.filename = widget.get_filename()

    def progressCallback(self, progress):
        # update progressbar
        pass
    
    def showError(self, msg):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, 
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
        dialog.run()
        dialog.destroy()
        
class SendThread(Thread):

    def __init__(self, sc):
        self.sc = sc

    def run(self):
        self.sc.send()

def main():
    app = GuiSaftApp()
    gtk.main()

if __name__ == '__main__':
    main()
