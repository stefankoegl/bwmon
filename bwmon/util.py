# -*- coding: utf-8 -*-

import curses
import sys

def clear():
    curses.setupterm()
    sys.stdout.write(curses.tigetstr("clear"))
    sys.stdout.flush()

