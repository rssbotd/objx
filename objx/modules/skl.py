# This file is placed in the Public Domain.
# pylint: disable=W0613


"create service file."


import getpass


from ..disk  import skel
from ..utils import privileges


def skl(event):
    "create service file (pipx)."
    privileges(getpass.getuser())
    skel()
