#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
from bwmon.pipe import Pipe, PipeMonitor

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        port = newport = int(sys.argv[1])
        newhost = sys.argv[2]
        if len(sys.argv) == 4:
            newport = int(sys.argv[3])
        pipe = Pipe(port, newhost, newport)
        monitor = PipeMonitor(pipe)
        pipe.start()
        try:
            monitor.run()
        except KeyboardInterrupt:
            pipe.close()
            print 'Waiting for threads to finish...'

    else:
        import sys
        print >> sys.stderr, '''
Usage:
    runpipe.py <port> <remotehost>
    runpipe.py <localport> <remotehost> <remoteport>

'''

