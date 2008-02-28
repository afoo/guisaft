#!/usr/bin/env python
#
# GPL-3 ble

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade


class GuiSaftApp(object):

    GLADEFILE = './guisaft.glade'

    def __init__(self):
        self.glade = gtk.glade.XML(self.GLADEFILE)
        self.window = self.glade.get_widget('window1')
        self.window.connect('destroy', gtk.main_quit)
        self.glade.signal_autoconnect({
                'on_applyButton_clicked': self.onApplyClick,
                })
                
    def onApplyClick(self, widget):
        print 'apply button clicked!'

def main():
    app = GuiSaftApp()
    gtk.main()

if __name__ == '__main__':
    main()
