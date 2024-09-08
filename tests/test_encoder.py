# This file is placed in the Public Domain.
#
#
# pylint: disable=C,R,W1503


"no tests"


import unittest


from objx.encoder import dumps


class TestEncoder(unittest.TestCase):

    def test_emptystring(self):
        a = ""
        res = dumps(a)
        self.assertEqual(res, '""')

    def test_string(self):
        a = "b"
        res = dumps(a)
        self.assertEqual(res, '"b"')
