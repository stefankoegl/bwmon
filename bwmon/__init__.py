# -*- coding: utf-8 -*-

from __future__ import absolute_import

from bwmon import proc

import collections
import time
import sys
import curses

def clear():
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

class Monitor(object):
    def __init__(self):
        self.fd_map = {}
        self.conntrack = {}
        self.connections = {}
        self.tracking = collections.defaultdict(int)

    def update(self):
        self.fd_map.update(proc.get_fd_map())
        self.conntrack.update(proc.parse_ip_conntrack())
        self.connections.update(proc.get_connections())

    def convert(self):
        self.tracking.clear()
        for con in self.connections.itervalues():
            inode = con.get('inode', None)
            process = self.fd_map.get(inode, None)

            if process is None:
                continue

            key1 = proc.ip_hash(con['local'], con['remote'])
            key2 = proc.ip_hash(con['remote'], con['local'])
            key = None

            if key1 in self.conntrack:
                key = key1
            elif key2 in self.conntrack:
                key = key2

            if key and 'bytes' in self.conntrack[key]:
                bytes = int(self.conntrack[key]['bytes'])
                self.tracking[process['cmd']] += bytes

    def output(self):
        def compare(a, b):
            return cmp(a[1], b[1])

        clear()
        for cmd, bytes in sorted(self.tracking.iteritems(), cmp=compare):
            if len(cmd) > 60:
                cmd = cmd[:57] + '...'
            print '%10d -- %s' % (bytes, cmd)

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

