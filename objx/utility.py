# This file is placed in the Public Domain.
# pylint: disable=R0911


"utilities"


import pathlib


def cdir(pth):
    "create directory."
    path = pathlib.Path(pth)
    path.parent.mkdir(parents=True, exist_ok=True)


def __dir__():
    return (
        "cdir",
    )
