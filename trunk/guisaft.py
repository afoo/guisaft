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
 
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade


class GuiSaftApp(object):

    GLADEFILE = './guisaft.glade'

    def __init__(self):
        self.glade = gtk.glade.XML(self.GLADEFILE)
        self.window = self.glade.get_widget('window1')
        self.filechooser = self.glade.get_widget('filechooserbutton1')
        self.window.connect('destroy', gtk.main_quit)
        self.glade.signal_autoconnect({
                'on_applyButton_clicked': self.onApplyClick,
                'on_filechooserbutton1_file_set': self.onFileSet,
                })
        self.filename = None
                
    def onApplyClick(self, widget):
        print 'apply button clicked!'
        if self.filename is None:
            self.showError('no file selected')
        else:
            print self.filename

    def onFileSet(self, widget):
        self.filename = widget.get_filename()

    def showError(self, msg):
        dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL, 
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, msg)
        dialog.run()
        dialog.destroy()
        

def main():
    app = GuiSaftApp()
    gtk.main()

if __name__ == '__main__':
    main()
