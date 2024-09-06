# This file is placed in the Public Domain.
# pylint: disable=R0902,R0903


"default"


from objx import Object


class Default(Object):

    "Default"
    def __init__(self):
        Object.__init__(self)

    def __getattr__(self, key):
        return self.__dict__.get(key, "")


def __dir__():
    return (
        'Default',
    )
