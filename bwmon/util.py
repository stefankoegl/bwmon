# -*- coding: utf-8 -*-
#
# Copyright 2010 Thomas Perl and Stefan Kögl. All rights reserved.
#
# Developed for a practical course (Large-scaled distributed computing) at the
# University of Technology Vienna in the 2010 summer term.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
    """Reads the monitor configuration file for the Aggregator

    @param configfile: path of the config file
    @return: a list of Monitor or PipeMonitor objects
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))

        if c['type'] == 'monitor':
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
    """Reads the notification config file for the Aggregator

    @param configfile: path to the config file
    @return: a list of tuples representing the notification settings (process_regex, in_threshold, out_threshold, interval, command)
    """
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    for section in config.sections():
        c = dict(config.items(section))
        yield ( c['process_filter'], int(c.get('in_threshold', 0)), int(c.get('out_threshold', 0)), int(c.get('interval', 1)), c.get('notification_command', '') )


class RingBuffer:
    """A ringbuffer
    """

    def __init__(self,size_max):
        """Initiates a new ringbuffer with the given size

        @param size_max: maximum number of entries
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
    """A full ringbuffer - not initialized directly
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


