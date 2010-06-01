# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import sys
import threading
import re
import BaseHTTPServer

from bwmon import util
from bwmon import model
from bwmon import http

class Aggregator(object):
    def __init__(self):
        self.monitors = []
        self.update_frequency = 1
        self.entries = model.MonitorEntryCollection(self.update_frequency, self.get_app)
        self.app_configs = {}
        http.RequestHandler.monitor = self.entries

    def add_monitor(self, monitor):
        self.monitors.append(monitor)


    def set_app_config(self, app, regex_list):
        self.app_configs[app] = regex_list


    def run(self):
        def thread_proc():
            server = BaseHTTPServer.HTTPServer(('', 8000), http.RequestHandler)
            while True:
                server.handle_request()
        t = threading.Thread(target=thread_proc)
        t.setDaemon(True)
        t.start()

        while True:
            for monitor in self.monitors:
                monitor.update(self.entries)
            self.output()
            time.sleep(self.update_frequency)

    def get_app(self, cmd):
        for app, regex in self.app_configs.iteritems():
            if any([re.search(x, cmd) for x in regex]):
                return app

        return cmd

    def output(self):
        #util.clear()
        entries = sorted(self.entries.get_usage())

        for bytes_in, bytes_out, cmd in entries:
            if bytes_in > 1024. or bytes_out > 1024.:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10.2f KiB / %10.2f KiB -- %s' % (bytes_in/1024., bytes_out/1024., cmd)
                sys.stdout.flush()

