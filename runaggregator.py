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
import ConfigParser

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    from bwmon import aggregator
    from bwmon import monitor
    from bwmon import pipe
    from bwmon import util

    parser = OptionParser()
    parser.add_option('--app-config', dest='appconfig', type='string', action='store', default=None, help='app-grouping configuration file')
    parser.add_option('--monitor-config', dest='monitorconfig', type='string', action='store', default=None, help='monitor configuration file'),
    parser.add_option('--notification-config', dest='notificationconfig', type='string', action='store', default=None, help='notification configuration file'),
    parser.add_option('--auto-group', dest='autogroup', action='store_true', default=False, help='automatically group processes by their apllication basename')
    (options, args) = parser.parse_args()


    agg = aggregator.Aggregator()

    if options.appconfig:
        config = ConfigParser.ConfigParser()
        config.read(options.appconfig)
        for app in config.sections():
            agg.set_app_config(app, [o[1] for o in config.items(app)])

    if options.monitorconfig:
        for mon in util.read_monitor_config(options.monitorconfig):
            agg.add_monitor(mon)

    else:
        # System monitor (connection tracker)
        agg.add_monitor(monitor.Monitor())


    if options.notificationconfig:
        for (re, in_t, out_t, interval, cmd) in util.read_notification_config(options.notificationconfig):
            agg.add_notification(re, in_t, out_t, interval, cmd)


    agg.auto_group = options.autogroup


    try:
        agg.run()
    except KeyboardInterrupt:
        print 'Please wait...'
        agg.close()

