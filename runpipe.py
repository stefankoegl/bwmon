#!/usr/bin/python
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

