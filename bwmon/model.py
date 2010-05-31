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
    TIMEOUT = 60

    def __init__(self, update_frequency):
        self._data = []
        self._latest = {}
        self.update_frequency = update_frequency

    def expire(self):
        cutoff = time.time() - self.TIMEOUT
        d = filter(lambda e: e.timestamp >= cutoff, self._data)
        self._data = d
        for key in self._latest.keys():
            current, previous = self._latest[key]
            if current is not None and current.timestamp < cutoff:
                del self._latest[key]

    def get_last_bytes(self, cmdline):
        (current, previous) = self._latest.get(cmdline, (None, None))

        if current is not None:
            return (current.inbytes, current.outbytes, current.timestamp)

        return (0, 0, 0)

    def get_bandwidth(self, cmdline):
        (current, previous) = self._latest.get(cmdline, (None, None))
        if current is not None and previous is not None:
            d_time = float(current.timestamp - previous.timestamp)
            d_in = float(current.inbytes - previous.inbytes)
            d_out = float(current.outbytes - previous.outbytes)
            return (d_in/d_time, d_out/d_time, current.timestamp)
        else:
            return (0, 0, 0)

    def add(self, entry):
        (current, previous) = self._latest.get(entry.cmdline, (None, None))

        self._latest[entry.cmdline] = (entry, current)
        self._data.append(entry)

    def get_history(self, cmdline):
        x = []
        last_inbytes = -1
        for e in self._data:
            if e.cmdline == cmdline:
                if last_inbytes == -1:
                    last_inbytes = e.inbytes
                x.append(e.inbytes-last_inbytes)
                last_inbytes = e.inbytes
        return x

    def get_datapoints(self):
        items = [self.get_history(cmdline) for bin, bout, cmdline in self.get_usage()]
        if not items:
            return [], []

        def check_items(l):
            return max(l) > 20.
        items = filter(check_items, items)

        return range(len(min(items, key=len))), items

    def get_traffic(self):
        for cmdline in self._latest:
            bytes_in, bytes_out, timestamp = self.get_last_bytes(cmdline)
            yield (bytes_in, bytes_out, cmdline)

    def get_usage(self):
        cutoff = time.time() - self.update_frequency
        for cmdline in self._latest:
            bytes_in, bytes_out, timestamp = self.get_bandwidth(cmdline)
            if timestamp > cutoff:
                yield (bytes_in, bytes_out, cmdline)

