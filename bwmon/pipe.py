# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import socket
import threading
import time

from bwmon import model
from bwmon import util

class PipeThread(threading.Thread):
    """A uni-direcational data pipe thread

    Instances of this class will write from one file
    ("source") and write the read data to the other
    file ("sink"). The amount of bytes transferred
    will be logged internally and can be retrieved
    from the "traffic" attribute.
    """
    def __init__(self, source, sink):
        """Create a new PipeThread object

        @param source: The source file to be read from
        @param sink: The destination file to be written to
        """
        threading.Thread.__init__(self)
        self.source = source
        self.sink = sink
        self.traffic = 0
        self.finished = False

    def run(self):
        """Run this thread (start forwarding data)

        Data will be forwarded between the source and
        sink files (as given to the constructor), and
        the "traffic" attribute will be updated to tell
        the value of bytes transferred. The attribute
        "finished" will be set to True when the transfer
        is complete.
        """
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
    """A data pipe from a local port to a (possibly remote) port
    """
    def __init__(self, port, newhost, newport):
        """Create a new Pipe object

        @param port: The source (listening) port
        @param newhost: The target hostname
        @param newport: The target port
        """
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
        """Setup the internal state of this object

        This will automatically be called by the constructor,
        and there should never be the need to call this from
        outside.
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.port))
        self.sock.settimeout(5)
        self.sock.listen(5)

    def update(self):
        """Update the internal traffic stats and retire threads

        This method should be called periodically to sum up the
        traffic amounts. The total traffic of finished threads
        will be summed up, and the threads will be removed from
        the internal data structures.
        """
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
        """Start the pipe, including its "child" pipes

        This will listen for new connections until the
        pipe itself is closed.
        """
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
        """Close this Pipe, don't accept new threads"""
        self.closed = True

class PipeMonitor(object):
    """A lightweight monitoring object for Pipe objects

    This is a lightweight wrapper for Pipe objects. It can
    be used to obtain and expose monitoring data from the
    Pipe to the Monitor or Aggregator objects.
    """
    DEFAULT_TIMEOUT = 1

    def __init__(self, pipe):
        """Create a new PipeMonitor object

        @param pipe: A Pipe object to be monitored
        """
        self.pipe = pipe
        self.cmdline = 'pipe-%d:%s:%d' % (pipe.port, pipe.newhost, pipe.newport)
        self.timeout = self.DEFAULT_TIMEOUT
        self.entries = model.MonitorEntryCollection(self.timeout)

    def update(self, entry_collection):
        """Update the monitor values from the pipe

        Take the current traffic values from the Pipe object and
        add a new MonitorEntry object to the entry_collection.

        @param entry_collection: A MonitorEntryCollection object
        """
        bytes_in, bytes_out = self.pipe.update()
        entry = model.MonitorEntry(self.cmdline, bytes_in, bytes_out, time.time())
        entry_collection.add(entry)
        entry_collection.expire()

    def output(self):
        """Print out the current status of this monitor object

        This will print the current traffic to stdout.
        """
        util.clear()
        entries = sorted(self.entries.get_traffic())

        for bytes_in, bytes_out, cmd in entries:
            if bytes_in or bytes_out:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10d / %10d -- %s' % (bytes_in, bytes_out, cmd)
                sys.stdout.flush()

    def run(self):
        """Run the mainloop for this monitor

        This periodically updates and outputs the data.
        """
        while True:
            self.update(self.entries)
            self.output()
            time.sleep(self.timeout)

    def close(self):
        """Close the underlying pipe"""
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

