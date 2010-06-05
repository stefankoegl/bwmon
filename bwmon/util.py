# -*- coding: utf-8 -*-

import curses
import sys
import ConfigParser

def clear():
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

def read_monitor_config(configfile):
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))

        if c['type'] == 'monitor':
            import monitor
            mon = monitor.Monitor()
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


def read_notification_config(configfile):
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))
        yield ( c['process_filter'], int(c.get('in_threshold', 0)), int(c.get('out_threshold', 0)), int(c.get('interval', 1)), c.get('notification_command', '') )


class RingBuffer:

    def __init__(self,size_max):
        self.max = size_max
        self.data = []

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur=0
            self.__class__ = RingBufferFull

    def get(self):
        """ return a list of elements from the oldest to the newest"""
        return self.data


class RingBufferFull:

    def __init__(self,n):
        raise "don't initialize FullRingBuffer directly"

    def append(self,x):
        self.data[self.cur]=x
        self.cur=(self.cur+1) % self.max

    def get(self):
        return self.data[self.cur:]+self.data[:self.cur]


