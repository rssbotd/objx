# This file is placed in the Public Domain.
# pylint: disable=C0413,R0903,R0912,W0105,W0201,W0718


"runtime"


import inspect
import io
import os
import queue
import sys
import threading
import time
import traceback


from objx.default import Default
from objx.object  import Object, fmt, keys
from objx.persist import Persist, find, long, skel, sync, types
from objx.utility import fntime, laps, named, spl, skip


STARTTIME = time.time()


rpr = object.__repr__


class Config(Default):

    "configuration"


Cfg         = Config()
Cfg.name    = Object.__module__.rsplit(".", maxsplit=1)[-2]
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr


class Logging:

    "Logging"

    filter = []
    out    = None


def debug(txt):
    "print to console."
    for skp in Logging.filter:
        if skp in txt:
            return
    if Logging.out:
        Logging.out(txt)


class Errors:

    "Errors"

    errors = []

    @staticmethod
    def format(exc):
        "format an exception"
        res = ""
        stream = io.StringIO(
                             traceback.print_exception(
                                                       type(exc),
                                                       exc,
                                                       exc.__traceback__
                                                      )
                            )
        for line in stream.readlines():
            res += line + "\n"
        return res


def errors():
    "show exceptions"
    for exc in Errors.errors:
        print(Errors.format(exc))


def later(exc):
    "add an exception"
    excp = exc.with_traceback(exc.__traceback__)
    Errors.errors.append(excp)


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


    @staticmethod
    def scan(mod) -> None:
        "scan module for commands."
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)


def command(evt):
    "check for and run a command."
    parse(evt)
    func = getattr(Commands.cmds, evt.cmd, None)
    if func:
        try:
            func(evt)
        except Exception as ex:
            later(ex)


class Thread(threading.Thread):

    "Thread"

    def __init__(self, func, thrname, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, thrname, (), {}, daemon=daemon)
        self._result   = None
        self.name      = thrname or (func and named(func)) or named(self).split(".")[-1]
        self.out       = None
        self.queue     = queue.Queue()
        self.sleep     = None
        self.starttime = time.time()
        if func:
            self.queue.put_nowait((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def size(self):
        "return qsize"
        return self.queue.qsize()

    def join(self, timeout=1.0):
        "join this thread."
        super().join(timeout)
        return self._result

    def run(self):
        "run this thread's payload."
        func, args = self.queue.get()
        try:
            self._result = func(*args)
        except Exception as ex:
            later(ex)
            for arg in args:
                if isinstance(arg, Event):
                    arg.ready()


class Timer(Object):

    "Timer"

    def __init__(self, sleep, func, *args, thrname=None):
        self.args  = args
        self.func  = func
        self.sleep = sleep
        self.name  = thrname or named(func)
        self.state = {}
        self.timer = None

    def run(self):
        "run the payload in a thread."
        self.state["latest"] = time.time()
        launch(self.func, *self.args)

    def start(self):
        "start timer."
        timer = threading.Timer(self.sleep, self.run)
        timer.name   = self.name
        timer.daemon = True
        timer.sleep  = self.sleep
        timer.state  = self.state
        timer.func   = self.func
        timer.state["starttime"] = time.time()
        timer.state["latest"]    = time.time()
        timer.start()
        self.timer   = timer

    def stop(self):
        "stop timer."
        if self.timer:
            self.timer.cancel()


class Repeater(Timer):

    "Repeater"

    def run(self):
        launch(self.start)
        super().run()


class Fleet(Object):

    "Fleet"

    bots = []

    @staticmethod
    def all():
        "return all objects."
        return Fleet.bots

    @staticmethod
    def announce(txt):
        "announce on all bots."
        for bot in Fleet.bots:
            if "announce" in dir(bot):
                bot.announce(txt)

    @staticmethod
    def get(orig):
        "return bot."
        res = None
        for bot in Fleet.bots:
            if rpr(bot) == orig:
                res = bot
                break
        return res

    @staticmethod
    def register(obj):
        "add bot."
        Fleet.bots.append(obj)


class Reactor:

    "Reactor"

    def __init__(self):
        self.cbs      = Object()
        self.queue    = queue.Queue()
        self.stopped  = threading.Event()

    def callback(self, evt):
        "call callback based on event type."
        evt.orig = repr(self)
        func = getattr(self.cbs, evt.type, None)
        if not func:
            evt.ready()
            return
        if "target" in dir(func) and func.target not in str(func).lower():
            evt.ready()
            return
        evt._thr = launch(func, self, evt)

    def loop(self):
        "proces events until interrupted."
        while not self.stopped.is_set():
            try:
                evt = self.poll()
                self.callback(evt)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        "function to return event."
        return self.queue.get()

    def put(self, evt):
        "put event into the queue."
        self.queue.put_nowait(evt)

    def register(self, typ, cbs):
        "register callback for a type."
        setattr(self.cbs, typ, cbs)

    def start(self):
        "start the event loop."
        launch(self.loop)

    def stop(self):
        "stop the event loop."
        self.stopped.set()


class Client(Reactor):

    "Client"

    cache = Object()
    out = None

    def __init__(self, outer=None):
        Reactor.__init__(self)
        self.register("command", command)
        self.out = outer

    def say(self, _channel, txt):
        "echo on verbose."
        self.raw(txt)

    def raw(self, txt):
        "print to screen."
        if self.out:
            txt = txt.encode('utf-8', 'replace').decode()
            self.out(txt)

    def show(self, evt):
        "show results into a channel."
        for txt in evt.result:
            self.say(evt.channel, txt)


def launch(func, *args, **kwargs):
    "launch a thread."
    nme = kwargs.get("name", named(func))
    thread = Thread(func, nme, *args, **kwargs)
    thread.start()
    return thread


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


def scan(modstr, *pkgs, disable=""):
    "scan modules for commands and classes"
    mds = []
    for modname in spl(modstr):
        if skip(modname, disable):
            continue
        for pkg in pkgs:
            module = getattr(pkg, modname, None)
            if not module:
                continue
            Commands.scan(module)
            Persist.scan(module)
    return mds


if __name__ == "__main__":
    import examples.all
    Cfg.mod = ",".join(dir(examples.all))
    scan(Cfg.mod, examples)
    result = Event()
    result.txt = " ".join(sys.argv[1:])
    command(result)
    for text in result.result:
        print(text)
    errors()
