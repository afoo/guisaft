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
import gzip
import tempfile
import sys

DEBUG = True
def dprint(*a):
    if DEBUG:
        print a
        sys.stdout.flush()

class NoCallbackError(Exception):
    pass

class CallbackCancel(Exception):
    pass

class SaftClient(object):

    def __init__(self, fromaddr, toaddr, filename, compress=True):
        self.fromaddr = fromaddr
        self.toaddr = toaddr
        self.filename = os.path.basename(filename)
        self.progress_callbacks = list()
        self.compress = compress
        self.fileobj = open(filename, 'rb')
        self.filesize = os.path.getsize(filename) 
        self.sock = socket.socket()
        self.tmpfile = None

    def addCallback(self, callback):
        self.progress_callbacks.append(callback)

    def executeCallbacks(self, progress):
        dprint('executing callbacks', progress)
        for cb in self.progress_callbacks:
            if not cb(progress):
                raise CallbackCancel()

    def send(self):
        try:
            self._send()
        finally:
            self.fileobj.close()
            if self.tmpfile is not None:
                self.tmpfile.close()

    def scmd(self, cmd=''):
        self.sock.send(cmd + '\r\n')
        dprint(self.sock.recv(1024))
    
    def _send(self):
        if len(self.progress_callbacks) == 0:
            raise NoCallbackError()
        user, host = self.toaddr.split('@') # evtl doch seperat reingeben?
        self.sock.connect((host, 487))
        dprint(self.sock.recv(1024))
        self.scmd("FROM %s" % self.fromaddr) 
        self.scmd("TO %s" % user)
        self.scmd("FILE %s" % self.filename) 
        if self.compress:
            dprint('sending compressed')
            tmpfd, tmpname  = tempfile.mkstemp()
            self.tmpfile = gzip.GzipFile(tmpname, 'wb+', 9, os.fdopen(tmpfd, 'wb+'))
            block = self.fileobj.read(2048)
            while len(block) > 0:
                self.tmpfile.write(block)
                block = self.fileobj.read(2048)
            self.tmpfile.close()
            self.tmpfile = open(tmpname, 'rb')
            tmpsize = os.path.getsize(tmpname)
            dprint("Uncompressed size is: ", str(self.filesize))
            dprint("Compressed size is:   ", str(tmpsize))
            self.scmd("TYPE BINARY COMPRESSED") 
            self.scmd("SIZE %i %i" % (tmpsize, self.filesize))
            self.scmd("DATA")
            i = 0
            self.executeCallbacks(0.0)
            while i < tmpsize:       
                i += self.sock.send(self.tmpfile.read(1024)) 
                self.executeCallbacks(i/float(tmpsize))
            self.tmpfile.close()
            os.unlink(tmpname)
        else:
            dprint("Compress == False")
            self.scmd("SIZE %i %i" % (self.filesize, self.filesize))
            self.scmd("DATA")
            i = 0
            self.executeCallbacks(0.0)
            while i < self.filesize:           
                i += self.sock.send(self.fileobj.read(1024))
                self.executeCallbacks(i/float(self.filesize))
        self.scmd() 
        self.scmd("QUIT")
        self.fileobj.close()

        
if __name__ == '__main__':
    def cb(progress):
        #print progress
        return True

    user = os.environ.get('USER', 'me')
    c = SaftClient('me@localhost', '%s@localhost' % user, '/etc/passwd', True)
    c.addCallback(cb)
    c.send()
