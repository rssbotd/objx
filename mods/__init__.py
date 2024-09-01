# This file is placed in the Public Domain
# pylint: disable=C,I,R


"modules"


import sys


def getmain(name):
    mne = sys.modules.get("__main__", None)
    if mne:
        return getattr(mne, name, None)
