#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
from optparse import OptionParser

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    import bwmon

    parser = OptionParser()
    parser.add_option('--include', dest='include_filter', type='string', action='append', help='include only processes that match the given regex')
    parser.add_option('--exclude', dest='exclude_filter', type='string', action='append', help='exclude processes that match the given regex')

    (options, args) = parser.parse_args()

    monitor = bwmon.Monitor()
    monitor.set_filter(options.include_filter, options.exclude_filter)
    monitor.loop()

