# This file is placed in the Public Domain.
# pylint: disable=C0413,R0903,R0912,W0105,W0201,W0611,W0718


"runtime"


import os
import sys
import time


from objx.default import Default
from objx.object  import Object
from objx.persist import Persist


STARTTIME = time.time()


rpr = object.__repr__


class Config(Default):

    "configuration"


Cfg         = Config()
Cfg.name    = Object.__module__.rsplit(".", maxsplit=1)[-2]
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr


class Event(Default):

    "Result"

    def __init__(self):
        Default.__init__(self)
        self.result  = []
        self.txt     = ""

    def reply(self, txt):
        "add text to the result"
        self.result.append(txt)


class Commands:

    "Commands"

    cmds = Object()

    @staticmethod
    def add(func):
        "add command."
        setattr(Commands.cmds, func.__name__, func)


def command(evt):
    "check for and run a command."
    parse(evt)
    func = getattr(Commands.cmds, evt.cmd, None)
    if func:
        func(evt)


def parse(obj, txt=None):
    "parse a string for a command."
    args = []
    _nr = -1
    obj.otxt = txt or obj.otxt or obj.txt
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            if not obj.gets:
                obj.gets = Default()
            if key in obj.gets:
                val = getattr(obj.gets, key)
                value = val + "," + value
            setattr(obj.gets, key, value)
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            if key == "mod":
                obj.hasmods = True
                if obj.mod:
                    obj.mod += f",{value}"
                else:
                    obj.mod = value
                continue
            if not obj.gets:
                obj.gets = Default()
            setattr(obj.sets, key, value)
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""
