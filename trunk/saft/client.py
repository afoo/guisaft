

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


    
