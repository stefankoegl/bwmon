#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
from optparse import OptionParser
import ConfigParser

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    from bwmon import aggregator
    from bwmon import monitor
    from bwmon import pipe

    parser = OptionParser()
    parser.add_option('--app-config', dest='appconfig', type='string', action='store', default=None, help='set the file from which the app-grouping information is read')
    (options, args) = parser.parse_args()


    agg = aggregator.Aggregator()

    # System monitor (connection tracker)
    agg.add_monitor(monitor.Monitor())

    if options.appconfig:
        config = ConfigParser.ConfigParser()
        config.read(options.appconfig)
        for app in config.sections():
            agg.set_app_config(app, [o[1] for o in config.items(app)])


    # Pipe monitors (port based)
    pipes = []
    pipes.append(pipe.Pipe(2222, 'khan.thpinfo.com', 22))

    for p in pipes:
        p.start()
        agg.add_monitor(pipe.PipeMonitor(p))

    try:
        agg.run()
    except KeyboardInterrupt:
        print 'Please wait...'
        for p in pipes:
            p.close()

