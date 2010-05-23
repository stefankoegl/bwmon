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

            cmd_file = open(os.path.join(d, cmdline), 'r')
            cmd = cmd_file.read()

            m[inode] = {'inode': inode, 'cmd': cmd, 'pid': int(pid)}

    return m


def parse_ip_conntrack():

    connections = {}

    f = open('/proc/net/ip_conntrack', 'r')
    for line in f.readlines():

        values = {}

        parts = filter(lambda x: x, line.split(' '))
        for p in parts:
            if not '=' in p:
                continue
            key, value = p.split('=')

            # lines often contain src and dest reversed (for returning traffic)
            # we are just interested in one-way traffic
            if key in values:
                continue

            values[key] = value

        src = '%s:%s' % (values['src'], values['sport'])
        dst = '%s:%s' % (values['dst'], values['dport'])
        key = ip_hash(src, dst)
        connections[key] = values


def ip_hash(src_ip, dest_ip):
    return '%s-%s' % (src_ip, dest_ip)

