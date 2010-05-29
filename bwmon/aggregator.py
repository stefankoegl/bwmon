from subprocess import Popen, PIPE
from datetime import datetime
import re
import collections


class Aggregator():

    def __init__(self, args):
        self.args = args

    def run(self):
        line_regex = re.compile('\s*(?P<in>\d+)\s*/\s*(?P<out>\d+)\s*--\s*(?P<proc>.*)')

        proc = Popen(self.args, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
        records = collections.defaultdict(list)

        for line in proc.stdout:

            record = self.get_record(line)

            if not record:
                continue

            records[process].append(record)

            if len(records[process]) > 1:
                prev_record = records[process][-2]
                bw = self.get_bandwidth(prev_record, record)
                # process bandwidth


    def get_record(line):
        match = line_regex.match(line)

        if not match:
            return None

        process = match.group('proc').strip()
        bytes_in = int(match.group('in'))
        bytes_out = int(match.group('out'))
        record = {'timestamp': datetime.now(), 'in': bytes_in, 'out': bytes_out}


    def get_bandwidth(rec1, rec2):
        """
        returns the mean incoming and outgoing bandwidth used between
        the two given records.

        rec1 represents the earlier, rec2 the later record
        """
        date_diff = rec2['timestamp'] - rec1['timestamp']
        in_diff = rec2['in'] - rec1['diff']
        out_diff = rec2['out'] - rec1['out']

        in_bw = in_diff / date_diff.seconds
        out_bw = out_diff / date_diff.seconds

        return (in_bw, out_bw)

