# This file is placed in the Public Domain.
#
#
# pylint: disable=C,R,W1503


"no tests"


import unittest


from objx import Object


class A(Object):

    def a(self):
        return 1


class TestRealOO(unittest.TestCase):

    def test_method(self):
        a = A()
        res = a.a()
        self.assertEqual(res, 1)

    def test_override(self):
        a = A()
        a.a = "b"
        self.assertEqual(a.a, "b")

    def test_overrideandcall(self):
        with self.assertRaises(Exception) as contrext:
            a = A()
            a.a = "b"
            a.a()
    