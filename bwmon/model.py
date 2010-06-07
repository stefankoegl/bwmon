# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time

class MonitorEntry(object):
    """Entity object for one monitoring "event"

    This class encapsulates all data that's measured in
    one single monitoring event.
    """
    def __init__(self, cmdline, inbytes, outbytes, timestamp=None):
        """Creates a new MonitorEntry object

        If the parameter timestamp is omitted, it will default to
        "now" (i.e. the measurement has taken place right now).

        @param cmdline: The command line of the measured process
        @param inbytes: The current incoming total data, in bytes
        @param outbytes: The current outgoing total data, in bytes
        @param timestamp: Unix timestamp (UTC) of the event
        """
        if timestamp is None:
            timestamp = time.time()

        self.cmdline = cmdline
        self.inbytes = int(inbytes)
        self.outbytes = int(outbytes)
        self.timestamp = timestamp

    def __repr__(self):
        """Create a string representation of this entry

        This is mostl used for debugging, and will simply
        return all the values in a user-readable string.

        @return: The string representation of this object
        """
        return '<%s cmd="%s" in=%d out=%d time=%d>' % (self.__class__.__name__,
                self.cmdline,
                self.inbytes,
                self.outbytes,
                int(self.timestamp),)

class MonitorEntryCollection(object):
    """A (linear) collection of multiple MonitorEntry objects

    This object is used by the monitor and the aggregator to
    combine several single MonitorEntry objects and provide
    a unified view on the current state of the objects.
    """
    TIMEOUT = 60

    def __init__(self, update_frequency, get_app=lambda x: x):
        """Create a new MonitorEntryCollection object

        The update_frequency should match the update frequency
        of the "calling object" (either a simple Monitor or the
        aggregator itself), as it's used for calculations that
        will be exposed to the calling object.

        @param update_frequency: Update frequency (in seconds)
        @param get_app: Callback to determine the app from a command
        """
        self._data = []
        self._latest = {}
        self.update_frequency = update_frequency
        self.get_app = get_app

    def expire(self):
        """Compact the internal state (expire old entries)

        Remove all the measurement data that's too old and
        has already been processed. This will usually be
        called internally and remove all items older than
        the "TIMEOUT" value for this class.
        """
        cutoff = time.time() - self.TIMEOUT
        d = filter(lambda e: e.timestamp >= cutoff, self._data)
        self._data = d
        for key in self._latest.keys():
            current, previous = self._latest[key]
            if current is not None and current.timestamp < cutoff:
                del self._latest[key]

    def get_last_bytes(self, cmdline):
        """Return a (inbytes, outbytes, timestamp) for a command

        In case no measurement for the given command is
        available, a (0, 0, 0) three-tuple will be returned.

        Otherwise, the cumulative traffic data (inbytes, outbytes
        and a UTC unix timestamp) will be returned, as of the
        last measurement.

        @return: A three-tuple or (0, 0, 0)
        """
        (current, previous) = self._latest.get(cmdline, (None, None))

        if current is not None:
            return (current.inbytes, current.outbytes, current.timestamp)

        return (0, 0, 0)

    def get_bandwidth(self, cmdline):
        """Return a (inbytespersec, outbytespersec, timestamp) for a command

        The semantics of this command are the same as the
        get_last_bytes() command, but it returns the CURRENT
        bandwidth usage (in bytes) instead of the cumulative
        bytes transferred.

        When the current bandwidth usage cannot be determined,
        this function returns (0, 0, 0). This is the case when
        not enough measurements are available (< 2) or the
        command is not monitored at all by the installed monitors.

        @return: A three-tuple or (0, 0, 0)
        """
        (current, previous) = self._latest.get(cmdline, (None, None))
        if current is not None and previous is not None:
            d_time = float(current.timestamp - previous.timestamp)
            d_in = float(current.inbytes - previous.inbytes)
            d_out = float(current.outbytes - previous.outbytes)
            return (d_in/d_time, d_out/d_time, current.timestamp)
        else:
            return (0, 0, 0)

    def add(self, entry):
        """Add a new entry to this collection

        This adds a new MonitorEntry to this collection and
        makes sure that it is picked up from the aggregation
        commands.

        @param entry: A MonitorEntry object to be added
        """
        entry.cmdline = self.get_app(entry.cmdline)
        (current, previous) = self._latest.get(entry.cmdline, (None, None))

        # throttle comparison; don't always take the lastest two
        #prev = current if current and (entry.timestamp - current.timestamp) else previous
        #self._latest[entry.cmdline] = (entry, prev)

        self._latest[entry.cmdline] = (entry, current)
        self._data.append(entry)

    def get_history(self, cmdline):
        """Return the bandwidth history for a given command

        @param cmdline: The command line / app name to be queried
        """
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
        """TODO

        @return: TODO
        """
        items = [self.get_history(cmdline) for bin, bout, cmdline in self.get_usage()]
        if not items:
            return [], []

        def check_items(l):
            return max(l) > 20.
        items = filter(check_items, items)

        return range(len(min(items, key=len))), items

    def get_traffic(self):
        """Get the current view on the traffic

        This returns a generator object that will yield
        (bytes_in, bytes_out, cmdline) tuples describing
        the current traffic on a per-command/-app basis.

        @return: Generator yielding (bytes_in, bytes_out, cmdline)
        """
        for cmdline in self._latest:
            bytes_in, bytes_out, timestamp = self.get_last_bytes(cmdline)
            yield (bytes_in, bytes_out, cmdline)

    def get_usage(self):
        """Get the current view on the bandwidth (usage)

        This returns a generator object that will yield
        (bytes_in, bytes_out, cmdline) tuples describing
        the current bandwidth usage on a per-command/-app
        basis.

        @return: Generator yielding (bytes_in, bytes_out, cmdline)
        """
        cutoff = time.time() - self.update_frequency
        for cmdline in self._latest:
            bytes_in, bytes_out, timestamp = self.get_bandwidth(cmdline)
            if timestamp > cutoff:
                yield (bytes_in, bytes_out, cmdline)

