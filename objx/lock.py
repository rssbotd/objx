# This file is placed in the Public Domain.


"locking"


import _thread


lock       = _thread.allocate_lock()


def __dir__():
    return (
        'lock',
    )
