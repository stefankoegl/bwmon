# -*- coding: utf-8 -*-

from __future__ import absolute_import

from bwmon import proc
from bwmon import util
from bwmon import model

import collections
import time
import sys
import copy
import re

BANDWIDTH, TRAFFIC = range(2)

class Monitor(object):
    DEFAULT_UPDATE_FREQUENCY = 1

    def __init__(self, lookback=True, ignorelocal=False):
        self.fd_map = {}
        self.sample_time = time.time()
        self.conntrack = {}
        self.last_conntrack = {}
        self.init_conntrack = {} if lookback else proc.parse_ip_conntrack()
        self.connections = {}
        self.update_frequency = self.DEFAULT_UPDATE_FREQUENCY
        self.entries = model.MonitorEntryCollection(self.update_frequency)
        self.include_filter = []
        self.exclude_filter = []
        self.ignorelocal = ignorelocal

    def update(self, entry_collection):
        self.fd_map.update(proc.get_fd_map())
        self.last_conntrack = copy.deepcopy(self.conntrack)
        self.conntrack.update( self.sub_conntrack(proc.parse_ip_conntrack(), self.init_conntrack) )
        self.connections.update(proc.get_connections())
        entry_collection.expire()
        self.sample_time = time.time()
        self.convert(entry_collection)

    def sub_conntrack(self, conntrack_current, conntrack_init):
        for (k, v_init) in conntrack_init.iteritems():
            if k in conntrack_current:
                v_current = conntrack_current[k]
                v_current['bytes'] = int(v_current['bytes']) - int(v_init['bytes'])
                v_current['packets'] = int(v_current['packets']) - int(v_init['packets'])
                conntrack_current[k] = v_current

        return conntrack_current

    def set_filter(self, include_filter, exclude_filter):
        self.include_filter = [re.compile(f) for f in include_filter] if include_filter else []
        self.exclude_filter = [re.compile(f) for f in exclude_filter] if exclude_filter else []

    def convert(self, entry_collection):
        entries = collections.defaultdict(lambda: (0, 0))
        for con in self.connections.itervalues():
            inode = con.get('inode', None)
            process = self.fd_map.get(inode, None)

            if process is None:
                continue

            if self.include_filter and not any([f.search(process['cmd']) for f in self.include_filter]):
                continue

            if self.exclude_filter and any([f.search(process['cmd']) for f in self.exclude_filter]):
                continue

            if self.ignorelocal and islocal(con['remote']) and islocal(con['local']):
                continue

            key_in  = proc.ip_hash(con['remote'], con['local'])
            key_out = proc.ip_hash(con['local'], con['remote'])
            keys = {'in': key_in, 'out': key_out}
            new_byte = {'in': 0, 'out': 0}

            for direction in ('in', 'out'):
                k = keys[direction]
                if k in self.conntrack:
                    if key_in in self.last_conntrack:
                        new_byte[direction] = int(self.conntrack[k]['bytes']) - int(self.last_conntrack[k]['bytes'])
                    else:
                        new_byte[direction] = int(self.conntrack[k]['bytes'])

            current_in, current_out = entries[process['cmd']]
            new_in, new_out = (new_byte['in'], new_byte['out'])

            entries[process['cmd']] = (current_in + new_in, current_out + new_out)

        for key in entries:
            new_in, new_out = entries[key]
            old_in, old_out, timestamp = entry_collection.get_last_bytes(key)
            entry = model.MonitorEntry(key, old_in + new_in, old_out + new_out, self.sample_time)
            entry_collection.add(entry)

    def output(self, mode=TRAFFIC):
        util.clear()
        if mode == TRAFFIC:
            entries = sorted(self.entries.get_traffic())
        else:
            entries = sorted(self.entries.get_usage())

        for bytes_in, bytes_out, cmd in entries:
            if bytes_in or bytes_out:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10d / %10d -- %s' % (bytes_in, bytes_out, cmd)
                sys.stdout.flush()

    def loop(self, mode):
        while True:
            self.update(self.entries)
            self.output(mode)
            time.sleep(self.update_frequency)

    def close(self):
        pass


def islocal(ip):
    return ip.startswith('127.0.0.') or ip.startswith('0.0.0.0')

