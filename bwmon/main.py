#!/usr/bin/python
import proc
import time

def list_connections():
    """
    prints a list of processes
    """

    fd_map = {}
    conntrack = {}
    connections = {}

    while True:
        fd_map.update(proc.get_fd_map())
        conntrack.update(proc.parse_ip_conntrack())

        connections.update(proc.get_connections())
        for con in connections.itervalues():

            if not con['inode']:
                continue

            if not con['inode'] in fd_map:
                print 'inode %s not im map' % con['inode']
                continue

            process = fd_map[con['inode']]


            key1 = proc.ip_hash(con['local'], con['remote'])
            key2 = proc.ip_hash(con['remote'], con['local'])
            key = None

            if key1 in conntrack:
                key = key1
            elif key2 in conntrack:
                key = key2

            if key and 'bytes' in conntrack[key]:
                byte_count = conntrack[key]['bytes']
            else:
                byte_count = '?'

            print '%d: %s: %s -> %s (%s Bytes)' % (process['pid'], process['cmd'], con['local'], con['remote'], byte_count)
        time.sleep(1)


if __name__ == '__main__':
    list_connections()

