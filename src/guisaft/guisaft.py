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

from twisted.internet import gtk2reactor
gtk2reactor.install()

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

from twisted.internet import reactor

try:
    import win32api
except ImportError:
    have_win32api = False
else:
    have_win32api = True

import sys
import os
import socket

from gettext import gettext as _

from saft.tclient import send_file

OWNPATH = os.path.dirname(__file__)
    
class GuiSaftApp(object):

    def __init__(self):
        win = gtk.Window()
        win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        win.set_position(gtk.WIN_POS_CENTER)
        win.set_border_width(5)
        win.set_title('guisaft')
        win.connect('destroy', self.quit)

        vbox = gtk.VBox()
        vbox.set_spacing(5)
        win.add(vbox)
        
        self.filechooser = gtk.FileChooserButton('file to send')
        self.filechooser.connect('file_set', self.onFileSet)
        vbox.add(self.filechooser)

        hbox = gtk.HBox()

        l = gtk.Label()
        l.set_text(_('Recipient'))
        hbox.add(l)
        
        self.toEntry = gtk.Entry()
        hbox.add(self.toEntry)

        vbox.add(hbox)
        
        ab = gtk.Button()
        ab.set_label('gtk-apply')
        ab.set_use_stock(True)
        ab.connect('clicked', self.onApplyClick)
        vbox.add(ab)

        win.show_all()
        self.window = win

        self.filename = None
        username = self.getUserName()
        hostname = socket.gethostname()
        self.fromaddr = '%s@%s' % (username, hostname)

    def quit(self, *a):
        reactor.stop()
        
    def getUserName(self):
        if have_win32api:
            return win32api.GetUserName().replace(' ', '')
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
            self.progressWindow = ProgressWindow(self.window)
            sc = send_file(self.fromaddr, toaddr, self.filename,
                           self.progressWindow.scCallback)
            sc.addCallback(self.progressWindow.scDone)
            sc.addErrback(self.showError)

    def onFileSet(self, widget):
        self.filename = widget.get_filename()

    def showError(self, msg):
        msg = str(msg)
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, 
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
        dialog.run()
        dialog.destroy()


class ProgressWindow(object):

    def __init__(self, parent):
        win = gtk.Window()
        win.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        win.set_position(gtk.WIN_POS_CENTER)
        win.set_border_width(5)
        win.set_title('sending file...')

        vbox = gtk.VBox()
        vbox.set_spacing(5)

        self.progressBar = gtk.ProgressBar()
        vbox.add(self.progressBar)

        cb = gtk.Button()
        cb.set_label('gtk-cancel')
        cb.set_use_stock(True)
        cb.connect('clicked', self.onCancel)
        vbox.add(cb)

        win.add(vbox)
        win.show_all()
        self.window = win

    def onCancel(self, widget):
        # TODO: actually cancel the transfer 
        self.window.destroy()

    def scCallback(self, progress):
        self.progressBar.set_fraction(progress)

    def scDone(self, a):
        self.progressBar.set_fraction(1.0)

        
def main():
    app = GuiSaftApp()
    reactor.run()
