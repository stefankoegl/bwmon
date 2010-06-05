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

