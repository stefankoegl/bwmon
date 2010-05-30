# -*- coding: utf-8 -*-

from __future__ import absolute_import

from bwmon import proc

import collections
import time
import sys
import curses
import copy
import re

def clear():
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

class Monitor(object):
    def __init__(self):
        self.fd_map = {}
        self.conntrack = {}
        self.last_conntrack = {}
        self.connections = {}
        self.tracking = {}
        self.include_filter = []
        self.exclude_filter = []

    def update(self):
        self.fd_map.update(proc.get_fd_map())
        self.last_conntrack = copy.deepcopy(self.conntrack)
        self.conntrack.update(proc.parse_ip_conntrack())
        self.connections.update(proc.get_connections())

    def set_filter(self, include_filter, exclude_filter):
        self.include_filter = [re.compile(f) for f in include_filter] if include_filter else []
        self.exclude_filter = [re.compile(f) for f in exclude_filter] if exclude_filter else []

    def convert(self):
        for con in self.connections.itervalues():
            inode = con.get('inode', None)
            process = self.fd_map.get(inode, None)

            if process is None:
                continue

            if self.include_filter and not any([f.search(process['cmd']) for f in self.include_filter]):
                continue

            if self.exclude_filter and any([f.search(process['cmd']) for f in self.exclude_filter]):
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

            if process['cmd'] in self.tracking:
                old_in, old_out = self.tracking[process['cmd']]
            else:
                old_in = 0
                old_out = 0

            self.tracking[process['cmd']] = (old_in + new_byte['in'], old_out + new_byte['out'])

    def output(self):
        def compare(a, b):
            return cmp(a[1], b[1])

        clear()
        for cmd, bytes in sorted(self.tracking.iteritems(), cmp=compare):
            if len(cmd) > 60:
                cmd = cmd[:57] + '...'
            print '%10d / %10d -- %s' % (bytes[0], bytes[1], cmd)
            sys.stdout.flush()

    def loop(self):
        while True:
            self.update()
            self.convert()
            self.output()
            time.sleep(1)

#def loop():
#    """
#    prints a list of processes
#    """
#
#    while True:
#        for con in connections.itervalues():
#
#            if not con['inode']:
#                continue
#
#            if not con['inode'] in fd_map:
#                print 'inode %s not im map' % con['inode']
#                continue
#
#            process = fd_map[con['inode']]
#
#
#            key1 = proc.ip_hash(con['local'], con['remote'])
#            key2 = proc.ip_hash(con['remote'], con['local'])
#            key = None
#
#            if key1 in conntrack:
#                key = key1
#            elif key2 in conntrack:
#                key = key2
#
#            if key and 'bytes' in conntrack[key]:
#                byte_count = conntrack[key]['bytes']
#            else:
#                byte_count = '?'
#
#            print '%d: %s: %s -> %s (%s Bytes)' % (process['pid'], process['cmd'], con['local'], con['remote'], byte_count)
#        time.sleep(1)
#
#

