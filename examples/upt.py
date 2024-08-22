# This file is placed in the Public Domain.


"show uptime"


import time


from objx.utility import laps


from .run import STARTTIME


def upt(event):
    "show uptime."
    event.reply(laps(time.time() - STARTTIME))
