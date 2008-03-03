# -*- coding: utf-8 -*- 

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


import socket
import os

DEBUG = True
def dprint(*a):
    if DEBUG:
        print a

class SaftClient(object):

    __slots__ = (
        'fromaddr', # str
        'toaddr', # str 
        'filename', # str
        'fileobj', # file
        'filesize', # int (bytes)
        'progress_callbacks', # list of functions
        'compress', # bool
        'sock', # socket
        )

    def __init__(self, fromaddr, toaddr, filename, compress=True):
        self.fromaddr = fromaddr
        self.toaddr = toaddr
        self.filename = filename
        self.progress_callbacks = list()
        self.compress = compress

        self.fileobj = open(filename, 'r')
        self.filesize = os.path.getsize(filename)
  
        self.sock = socket.socket()

    def addCallback(self, callback):
        self.progress_callbacks.append(callback)

    def executeCallbacks(self, progress):
        for cb in self.progress_callbacks:
            if not cb(progress):
                return False
        return True

    def send(self):
        if len(self.progress_callbacks) == 0:
            raise 'some exception'
        user, host = self.toaddr.split('@') # evtl doch seperat reingeben?
        self.sock.connect((host, 487))
        self.sock.send("FROM %s\r\n" % self.fromaddr) 
        dprint(self.sock.recv(1024))
        self.sock.send("TO %s\r\n" % user)
        dprint(self.sock.recv(1024))
        self.sock.send("FILE %s\r\n" % self.filename) 
        dprint(self.sock.recv(1024))
        self.sock.send("SIZE %i %i\r\n" % (self.filesize, self.filesize))
        dprint(self.sock.recv(1024))
        self.sock.send("DATA\r\n")
        dprint(self.sock.recv(1024))

        i = 0
        if not self.executeCallbacks(0.0):
            return
        while i < self.filesize:           
            i += self.sock.send(self.fileobj.read(1024)) #eh? error ones?
            if not self.executeCallbacks(i/float(self.filesize)):
                return

        self.sock.send("\r\n") 
        dprint(self.sock.recv(1024))
        self.sock.send("QUIT \r\n")
        dprint(self.sock.recv(1024))
        
        
if __name__ == '__main__':
    def cb(progress): pass
    #def cb(p):
        #print p

    c = SaftClient('me@localhost', 'stephan@localhost', '/etc/passwd', cb)
    c.send()
