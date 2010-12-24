import unittest

from montgolfier.lineparser import LineParser


class FakeClient:
    def __init__(self, jid, password):
        pass

    def connect(self):
        pass


class LineParserTest(unittest.TestCase):
    def setUp(self):
        self.lp = LineParser(client=FakeClient)

    def testConnection(self):
        self.assertEqual(len(self.lp.connections), 0)
        self.lp.parse('/connect tom_tester@example.org password')
        self.assertEqual(len(self.lp.connections), 1)
