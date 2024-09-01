# This file is placed in the Public Domain.
# pylint: disable=W0401,W0611,W0622,W0614
# ruff: noqa: F401,F403


"""objects


OBJX contains all the python3 code to program objects in a functional
way. It provides a base Object class that has only dunder methods, all
methods are factored out into functions with the objects as the first
argument. It is called Object Programming (OP), OOP without the
oriented.

OBJX  allows for easy json save//load to/from disk of objects. It
provides a "clean namespace" Object class so the namespace is not
cluttered with method names. This makes storing and reading to/from
json possible.

    >>> from objx.face import Object, dumps, loads
    >>> o = Object()
    >>> o.a = "b"
    >>> txt = dumps(o)
    >>> txt
    '{"a": "b"}'
    >>> obj = loads(txt)
    >>> obj 
    <objx.object.Object object at 0x7fe0d3aa6d90>
    >>> obj.a
    'b'

OBJX is Public Domain."""


__author__ ="Bart Thate <rssbotd@gmail.com>"
