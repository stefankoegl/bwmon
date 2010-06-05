# -*- coding: utf-8 -*-

from __future__ import absolute_import

import time
import sys
import threading
import re
import shlex
import os.path
import BaseHTTPServer
from datetime import datetime

from bwmon import util
from bwmon import model
from bwmon import http

class Aggregator(object):
    def __init__(self):
        self.monitors = []
        self.update_frequency = 1
        self.entries = model.MonitorEntryCollection(self.update_frequency)
        self.apps = {}
        self.app_configs = {}
        self.auto_group = False
        self.notification_configs = []
        self.notification_handler = {}
        http.RequestHandler.monitor = self.entries

    def add_monitor(self, monitor):
        self.monitors.append(monitor)


    def add_notification(self, regex, in_threshold, out_threshold, interval, command):
        self.notification_configs.append( (re.compile(regex), in_threshold, out_threshold, interval, command) )


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
            self.group()
            self.notify()
            self.output()
            time.sleep(self.update_frequency)

    def get_app(self, cmd):
        for app, regex in self.app_configs.iteritems():
            if any([re.search(x, cmd) for x in regex]):
                return app

        if self.auto_group:
            cmds = shlex.split(cmd)
            return os.path.basename(cmds[0])

        return cmd

    def group(self):
        self.apps = {}
        entries = sorted(self.entries.get_usage())
        for bytes_in, bytes_out, cmd in entries:
            cmd = self.get_app(cmd)
            (b_in, b_out) = self.apps[cmd] if cmd in self.apps else (0, 0)
            self.apps[cmd] = (b_in + bytes_in, b_out + bytes_out)

    def notify(self):
        for (cmd, (bytes_in, bytes_out)) in self.apps.iteritems():

            # App does not have notifications yet
            if not cmd in self.notification_handler:
                self.notification_handler[cmd] = []
                for (regex, in_threshold, out_threshold, interval, not_command) in self.notification_configs:
                    if regex.search(cmd):
                        self.notification_handler[cmd].append(NotificationHandler(cmd, in_threshold, out_threshold, interval, not_command))


            for handler in self.notification_handler[cmd]:
                handler.report_data(bytes_in / 1024, bytes_out / 1024)
                handler.check_notify()


    def output(self):
        util.clear()

        for (cmd, (bytes_in, bytes_out)) in self.apps.iteritems():
            if bytes_in > 1024. or bytes_out > 1024.:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10.2f KiB / %10.2f KiB -- %s' % (bytes_in/1024., bytes_out/1024., cmd)
                sys.stdout.flush()


    def close(self):
        for mon in self.monitors:
            mon.close()




class NotificationHandler(object):

    def __init__(self, cmd, in_threshold, out_threshold, interval, notify_command):
        self.cmd = cmd
        self.in_threshold = in_threshold
        self.out_threshold = out_threshold
        self.in_data = util.RingBuffer(interval)
        self.out_data = util.RingBuffer(interval)
        self.notify_command = notify_command

    def report_data(self, in_value, out_value):
        self.in_data.append(in_value)
        self.out_data.append(out_value)


    def check_notify(self):
        in_avg = avg(self.in_data.get())
        if self.in_threshold and in_avg > self.in_threshold:
            self.notify('in', self.in_threshold, in_avg)

        out_avg= avg(self.out_data.get())
        if self.out_threshold and out_avg > self.out_threshold:
            self.notify('out', self.out_threshold, out_avg)

    def notify(self, direction, threshold, value):
        import sys
        if len(self.cmd) > 50:
            cmd = self.cmd[:47] + '...'
        else:
            cmd = self.cmd

        print >> sys.stderr, "%s: %s exceeding '%s' bandwidth limit %10.2f: %10.2f kB/s (%3.2f %%)" % \
            (datetime.strftime(datetime.now(), '%F %T'), cmd, direction, threshold, value, value / threshold * 100)


        if self.notify_command:
            import shlex
            args = shlex.split(self.notify_command)

            import subprocess
            subprocess.Popen(args)


def avg(x): return float(sum(x)) / len(x)

