# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

class MonitorEntry(object):
    def __init__(self, cmdline, inbytes, outbytes, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        self.cmdline = cmdline
        self.inbytes = int(inbytes)
        self.outbytes = int(outbytes)
        self.timestamp = timestamp

    def __repr__(self):
        return '<%s cmd="%s" in=%d out=%d time=%d>' % (self.__class__.__name__,
                self.cmdline,
                self.inbytes,
                self.outbytes,
                int(self.timestamp),)

class MonitorEntryCollection(object):
    TIMEOUT = 60*5

    def __init__(self):
        self._data = []
        self._latest = {}

    def expire(self):
        cutoff = time.time() - self.TIMEOUT
        self._data = filter(lambda e: e.timestamp >= cutoff, self._data)

    def get_last_bytes(self, cmdline):
        (current, previous) = self._latest.get(cmdline, (None, None))

        if current is not None:
            return (current.inbytes, current.outbytes)

        return (0, 0)

    def get_bandwidth(self, cmdline):
        (current, previous) = self._latest.get(cmdline, (None, None))
        if current is not None and previous is not None:
            d_time = float(current.timestamp - previous.timestamp)
            d_in = float(current.inbytes - previous.inbytes)
            d_out = float(current.outbytes - previous.outbytes)
            return (d_in/d_time, d_out/d_time)
        else:
            return (0, 0)

    def add(self, entry):
        (current, previous) = self._latest.get(entry.cmdline, (None, None))

        self._latest[entry.cmdline] = (entry, current)
        self._data.append(entry)

    def get_traffic(self):
        for cmdline in self._latest:
            bytes_in, bytes_out = self.get_last_bytes(cmdline)
            yield (bytes_in, bytes_out, cmdline)

    def get_usage(self):
        for cmdline in self._latest:
            bytes_in, bytes_out = self.get_bandwidth(cmdline)
            yield (bytes_in, bytes_out, cmdline)

