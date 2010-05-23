import proc

if __name__ == '__main__':
    list_connections()


def list_connections():
    """
    prints a list of processes
    """
    fd_map = proc.get_fd_map()
    conntrack = proc.parse_ip_conntrack()

    connections = proc.get_connections()
    for con in connections.itervalues():

        if not con['inode']:
            continue

        if not con['inode'] in fd_map:
            print 'inode %s not im map' % con['inode']
            continue

        process = fd_map[con['inode']]

        key = proc.ip_hash(con['local'], con['remote'])

        byte_count = ''
        if key in conntrack:
            connt = conntrack[key]
            if 'bytes' in connt:
                byte_count = connt['bytes']

        print '%d: %s: %s -> %s (%s Bytes)' % (process['pid'], process['cmd'], con['local'], con['remote'], byte_count)



