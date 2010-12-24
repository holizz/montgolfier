import unittest

from montgolfier.lineparser import LineParser


class FakeClient:
    def __init__(self, jid, password):
        self.__dict__['jid'] = jid
        self.__dict__['password'] = password

    def connect(self):
        pass

    def message(self, jid, body):
        self.__dict__['target'] = jid
        self.__dict__['body'] = body


class LineParserTest(unittest.TestCase):
    def setUp(self):
        self.lp = LineParser(client=FakeClient)

    def _connect(self, jid='tom_tester@example.org', password='password'):
        self.lp.parse('/connect %s %s' % (jid, password))

    def c(self, i):
        return self.lp.connections[i].__dict__

    def testConnection(self):
        self.assertEqual(len(self.lp.connections), 0)
        self._connect()
        self.assertEqual(len(self.lp.connections), 1)
        self.assertEqual(self.c(0)['jid'], 'tom_tester@example.org')
        self.assertEqual(self.c(0)['password'], 'password')

        self._connect('a@b.c')
        self.assertEqual(len(self.lp.connections), 2)
        self.assertEqual(self.c(1)['jid'], 'a@b.c')
        self.assertEqual(self.c(1)['password'], 'password')

    def testMessage(self):
        self._connect()
        self.lp.parse('/msg tank@example.net hi there')
        self.assertEqual(self.c(0)['target'], 'tank@example.net')
        self.assertEqual(self.c(0)['body'], 'hi there')

        self._connect('a@b.c')
        self.lp.connection_context = 0
        self.lp.parse('/msg -account a@b.c target@example.org Message')
        self.assertEqual(self.c(1)['target'], 'target@example.org')

    def testMessageContext(self):
        """Both these messages should go to the same user:
        > /msg a@b.c Message 1
        > Message 2

        """
        self._connect()
        self.lp.parse('/msg unicorn@moon.org Message 1')
        self.lp.parse('Message 2')

        self.assertEqual(self.c(0)['target'], 'unicorn@moon.org')

        self.lp.parse('/msg a@b.c Message 1')

        self.assertEqual(self.c(0)['target'], 'a@b.c')

        self.lp.message_context = 'unicorn@moon.org'
        self.lp.parse('Message 3')

        self.assertEqual(self.c(0)['target'], 'unicorn@moon.org')

    def testConnectionContext(self):
        self._connect()
        self._connect()
        self.lp.parse('/msg j@r.i Message')
        self.assertEqual(self.c(1)['target'], 'j@r.i')

        self.lp.connection_context = 0
        self.lp.parse('/msg t@n.k Message')
        self.assertEqual(self.c(0)['target'], 't@n.k')
