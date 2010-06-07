# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import re
import hashlib

def get_connections(conn_type='tcp'):
    """Get connections from /proc/net/

    Read the currently-running connections from the
    /proc/ filesystem.

    @param conn_type: The connection type ('tcp' or 'udp')
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
    """Get the dotted-decimal representation of an IP

    @param ip: The IP as formatted in /proc/net/tcp
    @return: the dotted-decimal representation of an IP

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
    """Get a filedescriptor-to-process mapping

    @return: A dictionary mapping file descriptors to process infos
    """

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
    """Get a parsed representation of /proc/net/ip_conntrack

    @return: A dictionary of connections
    """
    connections = {}

    # http://www.faqs.org/docs/iptables/theconntrackentries.html
    for line in open('/proc/net/ip_conntrack'):
        parts = line.split()

        # We only care about TCP and UDP connections
        if parts[0] not in ('udp', 'tcp'):
            continue

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
    """Build a hashed key out of a ip_conntrack connection

    This takes the source IP, source port and destination
    IP and destination port and returns a unique key.

    @param values: An entry from the ip_conntrack table
    @return: The hashed key for this connection pair
    """
    src = '%s:%s' % (values['src'], values['sport'])
    dst = '%s:%s' % (values['dst'], values['dport'])
    return ip_hash(src, dst)


def ip_hash(src_ip, dest_ip):
    """Hash an IP pair

    @param src_ip: The IP address of the source
    @param dest_ip: The IP address of the destination
    @return: A string that combines both parameters
    """
    return '%s-%s' % (src_ip, dest_ip)

