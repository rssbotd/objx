# This file is placed in the Public Domain.


"list of commands"


from objx.face import keys


def cmd(event):
    "list commands."
    from .run import Commands
    print(Commands)
    event.reply(",".join(sorted(keys(Commands.cmds))))
