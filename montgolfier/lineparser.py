import re

import sleekxmpp


class LineGenerator:
    def __init__(self, line):
        self.line = line

    def __next__(self):
        m = re.match(r'^([\S]+)\s+(.*)$',
                self.line, re.DOTALL|re.MULTILINE)
        if not m:
            return self.line

        c, self.line = m.groups()
        return c


class LineParser:
    def __init__(self, client):
        self.client = client
        self.connections = []

    def parse(self, cmd):
        m = re.match(r'^/(\S+)\s+(.*)$', cmd, re.DOTALL|re.MULTILINE)

        if not m:
            self._msg(LineGenerator(cmd), noargs=True)
            return

        c, rem = m.groups()

        getattr(self, '_'+c)(LineGenerator(rem))

    def _connect(self, line):
        jid = next(line)
        password = next(line)

        conn = self.client(jid, password)

        if conn.connect():
            conn.process(threaded=True)

        self.connections.append(conn)
        self.connection_context = len(self.connections) - 1

    def _msg(self, line, noargs=False):
        # jid and -account
        if noargs:
            jid = self.message_context
        else:
            a = next(line)
            if a == '-account':
                self.set_connection(next(line))
                jid = next(line)
            else:
                jid = a

        self.message_context = jid
        body = line.line

        # Send it
        self.connections[self.connection_context].message(jid, body)

    def bare(self, jid):
        return sleekxmpp.xmlstream.JID(jid).bare

    def get_connection(self, jid):
        if re.match('^\d$', jid ):
            return int(jid)
        for j in (jid, self.bare(jid)):
            for i in range(len(self.connections)):
                connjid = self.connections[i].jid
                if connjid == j or self.bare(connjid) == j:
                    return i
        raise IndexError

    def set_connection(self, jid):
        self.connection_context = self.get_connection(jid)
