# -*- coding: utf-8 -*-

import os

from zope.interface import implements

from twisted.internet import reactor, interfaces
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver, FileSender


class Saft(LineReceiver):

    def __init__(self, defer, fromAddr, toAddr, filename, filesize, fh, pg_cb):
        self.fromAddr = fromAddr
        self.toAddr = toAddr
        self.filename = filename
        self.filesize = filesize
        self.fh = fh
        self.pg_cb = pg_cb
        self.done_def = defer
        self.ncmd = self.send_FROM
        self.ersp = '220'

    def connectionMade(self):
        print 'connection made!'

    def lineReceived(self, line):
        print 'received', line
        if not line.startswith(self.ersp):
            print 'unexpected server answer:', line
            print 'aborting'
            self.done_def.errback(Exception('unexpected server answer: ' + line))
            self.transport.loseConnection()
            return
        if self.ncmd is None:
            self.transport.loseConnection()
        else:
            self.ncmd()
        
    def send_cmd(self, next_command, expected_response, line):
        self.sendLine(line)
        self.ncmd = next_command
        self.ersp = expected_response

    def sendLine(self, line):
        print 'sending', line
        LineReceiver.sendLine(self, line)

    def send_FROM(self):
        self.send_cmd(self.send_TO, '200', 'FROM ' + self.fromAddr)

    def send_TO(self):
        self.send_cmd(self.send_FILE, '200', 'TO ' + self.toAddr)

    def send_FILE(self):
        self.send_cmd(self.send_SIZE, '200', 'FILE ' + self.filename)

    def send_SIZE(self):
        self.send_cmd(self.send_DATA, '200', 'SIZE %(s)d %(s)d' % dict(s=self.filesize))

    def send_DATA(self):
        self.send_cmd(self.send_data, '302', 'DATA')

    def send_data(self):
        fs = SaftFileSender(self.fh, self.filesize, self.transport, self.pg_cb)
        fs.start()
        self.ncmd = self.send_QUIT
        self.ersp = '201'

    def send_QUIT(self, *a):
        self.send_cmd(None, '221', 'QUIT')

        
class SaftFileSender(object):
    implements(interfaces.IProducer)
    
    CHUNK_SIZE = 1024

    def __init__(self, fh, size, consumer, pg_cb):
        self.fh = fh
        self.size = float(size)
        self.consumer = consumer
        self.pg_cb = pg_cb
        self.bytes_done = 0

    def start(self):
        self.consumer.registerProducer(self, False)

    def resumeProducing(self):
        if self.fh is not None:
            chunk = self.fh.read(self.CHUNK_SIZE)
        if not chunk:
            self.fh = None
            self.consumer.unregisterProducer()
            return
        self.bytes_done += len(chunk)
        self.pg_cb(self.bytes_done/self.size)
        self.consumer.write(chunk)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        self.fh = None


class SaftFactory(ClientFactory):

    def __init__(self, defer, *a):
        self.d = defer
        self._args = a
     
    def buildProtocol(self, addr):
        return Saft(self.d, *self._args)

    def clientConnectionLost(self, connector, reason):
        self.d.callback(1)

        
def send_file(from_addr, to_addr, file, pg_cb):
    fh = open(file, 'rb')
    size = os.path.getsize(file)
    name = os.path.basename(file)
    user, host = to_addr.split('@')
    defer = Deferred()
    reactor.connectTCP(host, 487, SaftFactory(defer, from_addr, user, name, size, fh, pg_cb))
    return defer
    

def test():
    import sys
    def cb(n):
        print n
    def done(a):
        print 'done!'
        reactor.stop()
    def err(e):
        print 'Error:', e
    d = send_file('me', 'jan@bfoo.de', '/etc/passwd', cb)
    d.addCallback(done)
    d.addErrback(err)
    reactor.run()

if __name__ == '__main__':
    test()
