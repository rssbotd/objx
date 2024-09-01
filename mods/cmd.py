# This file is placed in the Public Domain.
# pylint: disable=C,I,R


"list of commands"


from objx.face import keys


from . import getmain


Commands = getmain("Commands")


def cmd(event):
    "list commands."
    event.reply(",".join(sorted(keys(Commands.cmds))))
