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
    """Aggregator that merges output from multiple monitors

    This class is used to aggregate the output of several monitors
    (ip_conntrack-based or pipe-based) into one output.
    """

    def __init__(self):
        """Create a new Aggregator object

        The aggregator is initialized with a default update frequency
        of "once per second".
        """
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
        """Add a new monitor to the aggregated result

        The monitor can be a bwmon.pipe.PipeMonitor object or
        a bwmon.monitor.Monitor object (i.e. a system-wide,
        ip_conntrack based monitor).

        @param monitor: A pipe.PipeMonitor or monitor.Monitor object
        """
        self.monitors.append(monitor)


    def add_notification(self, regex, in_threshold, out_threshold, interval, command):
        """FIXME

        @param regex: TODO
        @param in_threshold: TODO
        @param out_threshold: TODO
        @param interval: TODO
        @param command: TODO
        """
        self.notification_configs.append( (re.compile(regex), in_threshold, out_threshold, interval, command) )


    def set_app_config(self, app, regex_list):
        """FIXME

        @param app: TODO
        @param regex_list: TODO
        """
        self.app_configs[app] = regex_list


    def run(self):
        """Run the aggregator

        This runs the aggregator in an endless loop, printing
        the current usage periodically and sends out pre-set
        notifications.
        """
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
        """Determine the app name given a command

        Returns the name of the application that is assigned
        to a given command (command line) as given by the config.

        Fallback 1: The basename of the command (auto-grouping).

        Fallback 2: The command itself.
        """
        for app, regex in self.app_configs.iteritems():
            if any([re.search(x, cmd) for x in regex]):
                return app

        if self.auto_group:
            cmds = shlex.split(cmd)
            return os.path.basename(cmds[0])

        return cmd

    def group(self):
        """Group command-based usage by application

        This takes the current measurements (command line-based)
        and calculates per-app statistics using the rules to
        combine the app.
        """
        self.apps = {}
        entries = sorted(self.entries.get_usage())
        for bytes_in, bytes_out, cmd in entries:
            cmd = self.get_app(cmd)
            (b_in, b_out) = self.apps[cmd] if cmd in self.apps else (0, 0)
            self.apps[cmd] = (b_in + bytes_in, b_out + bytes_out)

    def notify(self):
        """Compare current usage against SLA; send notifications

        Compare the app-based usage values and check if there
        are any SLA violations. If there are any violations, call
        any notifiation callback as specified in the config.
        """
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
        """Print the current bandwidth usage to the console

        The output is (by default) grouped by apps. The columns
        in the output: BYTES_IN, BYTES_OUT, APP NAME
        """
        util.clear()

        for (cmd, (bytes_in, bytes_out)) in self.apps.iteritems():
            if bytes_in > 1024. or bytes_out > 1024.:
                if len(cmd) > 60:
                    cmd = cmd[:57] + '...'
                print '%10.2f KiB / %10.2f KiB -- %s' % (bytes_in/1024., bytes_out/1024., cmd)
                sys.stdout.flush()


    def close(self):
        """Close the aggregator and its monitors
        """
        for mon in self.monitors:
            mon.close()




class NotificationHandler(object):
    """Handler object for checking SLA thresholds and sending notifications
    """

    def __init__(self, cmd, in_threshold, out_threshold, interval, notify_command):
        """Creates a new NotificationHandler object

        @param cmd: TODO
        @param in_threshold: TODO
        @param out_threshold: TODO
        @param interval: TODO
        @param notify_command: TODO
        """
        self.cmd = cmd
        self.in_threshold = in_threshold
        self.out_threshold = out_threshold
        self.in_data = util.RingBuffer(interval)
        self.out_data = util.RingBuffer(interval)
        self.notify_command = notify_command

    def report_data(self, in_value, out_value):
        """TODO

        @param in_value: TODO
        @param out_value: TODO
        """
        self.in_data.append(in_value)
        self.out_data.append(out_value)


    def check_notify(self):
        """TODO
        """
        in_avg = avg(self.in_data.get())
        if self.in_threshold and in_avg > self.in_threshold:
            self.notify('in', self.in_threshold, in_avg)

        out_avg= avg(self.out_data.get())
        if self.out_threshold and out_avg > self.out_threshold:
            self.notify('out', self.out_threshold, out_avg)

    def notify(self, direction, threshold, value):
        """TODO

        @param direction: TODO
        @param threshold: TODO
        @param value: TODO
        """
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

