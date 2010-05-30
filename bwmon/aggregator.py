from subprocess import Popen, PIPE
from datetime import datetime
import re
import collections
import shlex

class Aggregator():

    def __init__(self, monitors):
        self.monitors = monitors
        self.line_regex = re.compile('\s*(?P<in>\d+)\s*/\s*(?P<out>\d+)\s*--\s*(?P<proc>.*)')

    def launch_monitors(self):

        outpipe = PIPE

        for m in self.monitors:
            args = shlex.split(m)
            proc = Popen(args, stdin=PIPE, stdout=outpipe, stderr=PIPE, bufsize=1)

            if outpipe == PIPE:
                outpipe = proc.stdout

        return outpipe


    def run(self):

        outpipe = self.launch_monitors()

        records = collections.defaultdict(list)

        for line in outpipe:
            record, process = self.get_record(line)

            if not record:
                continue

            records[process].append(record)

            if len(records[process]) <= 1:
                continue

            prev_record = records[process][-2]
            bw = self.get_bandwidth(prev_record, record)

            if not bw:
                continue

            print '%10d / %10d B/s -- %s' % (bw[0], bw[1], process)


    def get_record(self, line):
        """
        parses the given line (output of runmonitor.py) and returns a record
        which is a dictionary with the keys timestamp, in and out (both in
        bytes)
        """
        match = self.line_regex.match(line)

        if not match:
            return None, None

        process = match.group('proc').strip()
        bytes_in = int(match.group('in'))
        bytes_out = int(match.group('out'))
        record = {'timestamp': datetime.now(), 'in': bytes_in, 'out': bytes_out}
        return record, process


    def get_bandwidth(self, rec1, rec2):
        """
        returns the mean incoming and outgoing bandwidth used between
        the two given records.

        rec1 represents the earlier, rec2 the later record
        """
        date_diff = rec2['timestamp'] - rec1['timestamp']
        in_diff = rec2['in'] - rec1['in']
        out_diff = rec2['out'] - rec1['out']

        if not date_diff.seconds:
            return None

        in_bw = in_diff / date_diff.seconds
        out_bw = out_diff / date_diff.seconds

        return (in_bw, out_bw)

