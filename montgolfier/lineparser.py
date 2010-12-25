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
    INFO = 1
    MESSAGE_SENT = 2

    def __init__(self, client_class, output):
        self.client_class = client_class
        self.output = output
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

        conn = self.client_class(jid, password)

        if conn.connect():
            conn.process(threaded=True)

            self.connections.append(conn)
            self.connection_context = len(self.connections) - 1

            self.output.enqueue(level=LineParser.INFO,
                    connection=self.connection_context,
                    message_context=None,
                    data='Connected!')

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
        self.output.enqueue(level=LineParser.MESSAGE_SENT,
                connection=self.connection_context,
                message_context=jid,
                data=body)

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
