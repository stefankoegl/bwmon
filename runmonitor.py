#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys

sys.path.insert(0, os.path.dirname(__file__) or '.')

if __name__ == '__main__':
    import bwmon

    monitor = bwmon.Monitor()
    monitor.loop()

