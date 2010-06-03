# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import socket
import threading
import time

from bwmon import model
from bwmon import util

class PipeThread(threading.Thread):
    def __init__(self, source, sink):
        threading.Thread.__init__(self)
        self.source = source
        self.sink = sink
        self.traffic = 0
        self.finished = False

    def run(self):
        while True:
            try:
                data = self.source.recv(1024)
                if not data:
                    break
                self.traffic += len(data)
                self.sink.send(data)
            except:
                break

        #print >>sys.stderr, 'Closing: (%s->%s) with total traffic %d' % (self.source.getpeername(),
        #        self.sink.getpeername(), self.traffic)
        self.finished = True

class Pipe(threading.Thread):
    def __init__(self, port, newhost, newport):
        threading.Thread.__init__(self)
        self.closed = False
        self.port = port
        self.newhost = newhost
        self.newport = newport
        self.pipes_in = []
        self.pipes_out = []
        self.total_in = 0
        self.total_out = 0
        self.setup()

    def setup(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.port))
        self.sock.settimeout(5)
        self.sock.listen(5)

    def update(self):
        sum_in, sum_out = self.total_in, self.total_out

        # Calculate input traffic + retire finished sessions
        for pipe in list(self.pipes_in):
            sum_in += pipe.traffic
            if pipe.finished:
                self.total_in += pipe.traffic
                self.pipes_in.remove(pipe)

        # Calculate output traffic + retire finished sessions
        for pipe in list(self.pipes_out):
            sum_out += pipe.traffic
            if pipe.finished:
                self.total_out += pipe.traffic
                self.pipes_out.remove(pipe)

        return sum_in, sum_out

    def run(self):
        while not self.closed:
            try:
                newsock, address = self.sock.accept()
            except socket.timeout:
                continue
            fwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fwd.connect((self.newhost, self.newport))
            in_pipe = PipeThread(newsock, fwd)
            out_pipe = PipeThread(fwd, newsock)
            self.pipes_in.append(in_pipe)
            self.pipes_out.append(out_pipe)
            in_pipe.start()
            out_pipe.start()

    def close(self):
        self.closed = True

class PipeMonitor(object):
    DEFAULT_TIMEOUT = 1

    def __init__(self, pipe):
        self.pipe = pipe
        self.cmdline = 'pipe-%d:%s:%d' % (pipe.port, pipe.newhost, pipe.newport)
        self.timeout = self.DEFAULT_TIMEOUT
        self.entries = model.MonitorEntryCollection(self.timeout)

    def update(self, entry_collection):
        bytes_in, bytes_out = self.pipe.update()
        entry = model.MonitorEntry(self.cmdline, bytes_in, bytes_out, time.time())
        entry_collection.add(entry)
        entry_collection.expire()

    def output(self):
        util.clear()
        entries = sorted(self.entries.get_traffic())

        for bytes_in, bytes_out, cmd in entries:
            if bytes_in or bytes_out:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10d / %10d -- %s' % (bytes_in, bytes_out, cmd)
                sys.stdout.flush()

    def run(self):
        while True:
            self.update(self.entries)
            self.output()
            time.sleep(self.timeout)

    def close(self):
        self.pipe.close()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = newport = int(sys.argv[1])
        newhost = sys.argv[2]
        if len(sys.argv) == 4:
            newport = int(sys.argv[3])
        pipe = Pipe(port, newhost, newport)
        monitor = PipeMonitor(pipe)
        pipe.start()
        try:
            monitor.run()
        except KeyboardInterrupt:
            pipe.close()
            print 'Waiting for threads to finish...'

