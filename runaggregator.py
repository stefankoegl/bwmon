#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    from bwmon import aggregator
    from bwmon import monitor
    from bwmon import pipe

    agg = aggregator.Aggregator()

    # System monitor (connection tracker)
    agg.add_monitor(monitor.Monitor())

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

