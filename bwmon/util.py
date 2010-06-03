# -*- coding: utf-8 -*-

import curses
import sys
import ConfigParser

def clear():
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

def read_monitor_config(configfile):
    monitors = []
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

