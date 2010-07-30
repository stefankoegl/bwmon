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
from optparse import OptionParser

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    from bwmon import monitor

    parser = OptionParser()
    parser.add_option('--include', dest='include_filter', type='string', action='append', help='include only processes that match the given regex')
    parser.add_option('--exclude', dest='exclude_filter', type='string', action='append', help='exclude processes that match the given regex')
    parser.add_option('--bandwidth', dest='bandwidth', action='store_true', default=False, help='print bandwidth instead of traffic')
    parser.add_option('--no-lookback', dest='lookback', action='store_false', default=True, help='don\'t try to measure traffic that was generated before the monitor has been started')
    parser.add_option('--ignore-local', dest='ignorelocal', action='store_true', default=False, help='ignore local traffic')

    (options, args) = parser.parse_args()

    m = monitor.Monitor(options.lookback, options.ignorelocal)
    m.set_filter(options.include_filter, options.exclude_filter)
    if options.bandwidth:
        m.loop(monitor.BANDWIDTH)
    else:
        m.loop(monitor.TRAFFIC)

