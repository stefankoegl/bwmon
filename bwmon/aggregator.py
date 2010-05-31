# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import sys

from bwmon import util
from bwmon import model

class Aggregator(object):
    def __init__(self):
        self.monitors = []
        self.update_frequency = 1
        self.entries = model.MonitorEntryCollection(self.update_frequency)

    def add_monitor(self, monitor):
        self.monitors.append(monitor)

    def run(self):
        while True:
            for monitor in self.monitors:
                monitor.update(self.entries)
            self.output()
            time.sleep(self.update_frequency)

    def output(self):
        util.clear()
        entries = sorted(self.entries.get_usage())

        for bytes_in, bytes_out, cmd in entries:
            if bytes_in > 1024. or bytes_out > 1024.:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10.2f KiB / %10.2f KiB -- %s' % (bytes_in/1024., bytes_out/1024., cmd)
                sys.stdout.flush()

