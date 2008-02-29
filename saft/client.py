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

class SaftClient(object):

    __slots__ = (
        'fromaddr', # str
        'toaddr', # str 
        'filename', # str
        'fileobj', # file
        'filesize', # int (bytes?)
        'progress_callback', # func
        'compress', # bool
        'sock', # socket
        )

    def __init__(self, fromaddr, toaddr, filename, prog_cb, compress=True):
        self.fromaddr = fromaddr
        self.toaddr = toaddr
        self.filename = filename
        self.progress_callback = prog_cb
        self.compress = compress

        self.fileobj = open(filename, 'b')
        self.filesize = os.path.getsize(filename)
  
        self.sock = socket.socket()

    def send(self):
        user, host = self.toaddr.split('@') # evtl doch seperat reingeben?
        self.sock.connect((host, 487))
        # ...


    
