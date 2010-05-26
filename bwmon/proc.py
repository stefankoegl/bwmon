# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import re
import hashlib

def get_connections(conn_type='tcp'):
    """
    returns the connections from /proc/net/tcp indexed by their id (first 
    column).
    """
    f = open('/proc/net/%s' % conn_type, 'r')
    connections = {}

    #documentation for /proc/net/tcp in
    #http://lkml.indiana.edu/hypermail/linux/kernel/0409.1/2166.html

    for line in f.readlines():
        line = line.strip()

        # header line
        if line.startswith('s'):
            continue

        parts = filter(lambda x: x, line.split(' '))
        index = parts[0].strip()[:-1]
        local_addr = ip_repr(parts[1])
        rem_addr = ip_repr(parts[2])
        inode = int(parts[9])

        connections[index] = {
            'local': local_addr,
            'remote': rem_addr,
            'inode': inode
        }

    return connections


def ip_repr(ip):
    """
    returns the dotted-decimal representation of an IP addresse when given
    the formated used in /proc/net/tcp

    >>> ip_repr('C8BCED82:1A0B')
    '130.237.188.200:6667'
    """

    if ':' in ip:
        ip, port = ip.split(':')
    else:
        port = None

    s = '.'.join([ repr(int(ip[x-2:x], 16)) for x in range(8, 0, -2) ])
    if port:
        s += ':%d' % int(port, 16)

    return s


def get_fd_map():
    """ returns a dictionary mapping filedescriptors to process information"""

    proc = '/proc/'
    fd = 'fd'
    pid_dir = r'\d+'
    socket_regex = r'socket:\[(\d+)\]'
    cmdline = 'cmdline'
    m = {}

    for pid in os.listdir(proc):

        # process directories
        d = os.path.join(proc, pid)
        if not os.path.isdir(d):
            continue

        if not re.match(pid_dir, pid):
            continue

        fd_dir = os.path.join(d, fd)
        for x in os.listdir(fd_dir):
            path = os.path.join(fd_dir, x)
            try:
                f_desc = os.readlink(path)
            except OSError:
                continue

            # search for socket file-descriptors
            match = re.match(socket_regex, f_desc)
            if match:
                inode = int(match.group(1))
            else:
                continue

            cmd_file = open(os.path.join(d, cmdline), 'rb')
            cmd = cmd_file.read()

            # Command line arguments are splitted by '\0'
            cmd = cmd.replace('\0', ' ')

            m[inode] = {'inode': inode, 'cmd': cmd, 'pid': int(pid)}

    return m


def parse_ip_conntrack():
    connections = {}

    # http://www.faqs.org/docs/iptables/theconntrackentries.html
    for line in open('/proc/net/ip_conntrack'):
        parts = line.split()

        entry = {}
        for (k, v) in [x.split('=', 1) for x in parts if '=' in x]:
            # key-value pairs occur twice per line; if first key occurs
            # again, we finish the first entry and start the next one
            if k in entry:
                key = get_key(entry)
                connections[key] = entry
                entry = {}

            entry[k] = v

        key = get_key(entry)
        connections[key] = entry

    return connections


def get_key(values):
    src = '%s:%s' % (values['src'], values['sport'])
    dst = '%s:%s' % (values['dst'], values['dport'])
    return ip_hash(src, dst)


def ip_hash(src_ip, dest_ip):
    return '%s-%s' % (src_ip, dest_ip)

