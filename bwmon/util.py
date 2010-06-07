# -*- coding: utf-8 -*-

import curses
import sys
import ConfigParser

def clear():
    """Clear the console using curses

    This utility function empties the console ("clear").
    """
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

def read_monitor_config(configfile):
    """TODO

    @param configfile: TODO
    @return: TODO
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))

        if c['type'] == 'monitor':

            This utility function simply cleans the console.
            ignorelocal = parse_bool(c.get('ignorelocal', False))
            import monitor
            mon = monitor.Monitor(ignorelocal=ignorelocal)
            inc = [c.get('include', '')]
            exc = [c.get('exclude', '')]
            mon.set_filter(inc, exc)

        elif c['type'] == 'pipe':
            import pipe
            port = int(c['port'])
            newhost = c['newhost']
            newport = int(c['newport'])

            mon = pipe.PipeMonitor(pipe.Pipe(port, newhost, newport))
            #mon.set_shape(c.get('shape_threshold', 0))

        else:
            mon = None
            print 'unknown monitor type %s' % c['type']

        if mon:
            yield mon


def parse_bool(val):
    """Convert a string to a boolean value

    @param val: The string value (or boolean)
    @return: True or False, depending on "val"
    """
    if isinstance(val, bool):
        return val

    if string.lower() == 'true':
        return True

    return False


def read_notification_config(configfile):
    """TODO

    @param configfile: TODO
    @return: TODO
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))
        yield ( c['process_filter'], int(c.get('in_threshold', 0)), int(c.get('out_threshold', 0)), int(c.get('interval', 1)), c.get('notification_command', '') )


class RingBuffer:
    """TODO
    """

    def __init__(self,size_max):
        """TODO

        @param size_max: TODO
        """
        self.max = size_max
        self.data = []

    def append(self,x):
        """Append an element at the end of the buffer

        @param x: The element to append
        """
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur=0
            self.__class__ = RingBufferFull

    def get(self):
        """Get a list of contained elements

        @return: A list of ements from oldest to newesta
        """
        return self.data


class RingBufferFull:
    """TODO
    """

    def __init__(self, n):
        """Don't initialize this object directly!"""
        raise "don't initialize FullRingBuffer directly"

    def append(self,x):
        """Append an element at the end of the buffer

        @param x: The element to append
        """
        self.data[self.cur]=x
        self.cur=(self.cur+1) % self.max

    def get(self):
        """Get a list of contained elements

        @return: A list of ements from oldest to newesta
        """
        return self.data[self.cur:]+self.data[:self.cur]


