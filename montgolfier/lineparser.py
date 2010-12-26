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
    ERROR = 3
    MESSAGE_RECEIVED = 4

    def __init__(self, client_class, ui):
        self.client_class = client_class
        self.ui = ui
        self.connections = []
        self.connection_context = None
        self.message_context = None

    ##
    ## Parser
    ##

    def parse(self, cmd):
        m = re.match(r'^/(\S+)(\s+(.*))?$', cmd, re.DOTALL|re.MULTILINE)

        if not m:
            self._msg(LineGenerator(cmd), noargs=True)
            return

        c = m.groups()[0]
        rem = m.groups()[2]

        if hasattr(self, '_'+c):
            getattr(self, '_'+c)(LineGenerator(rem))
        else:
            self.ui.enqueue(level=LineParser.ERROR,
                    connection=self.connection_context,
                    message_context=self.message_context,
                    data='No such command: "%s"'%c)

    ##
    ## Bits and bobs
    ##

    def bare(self, jid):
        return sleekxmpp.xmlstream.JID(jid).bare

    def get_connection(self, jid):
        if re.match('^\d$', jid ):
            return int(jid)
        for j in (jid, self.bare(jid)):
            for i in range(len(self.connections)):
                connjid = self.connections[i].boundjid.bare
                if connjid == j or self.bare(connjid) == j:
                    return i
        raise IndexError

    def set_connection(self, jid):
        self.connection_context = self.get_connection(jid)

    ##
    ## Callbacks
    ##

    def connected(self, conn):
        self.connections.append(conn)
        self.connection_context = len(self.connections) - 1

        self.ui.enqueue(level=LineParser.INFO,
                connection=self.get_connection(conn.boundjid.bare),
                message_context=None,
                data='Connected!')

    def message_received(self, conn, jid, body):
        self.ui.enqueue(level=LineParser.MESSAGE_RECEIVED,
                connection=self.get_connection(conn.boundjid.bare),
                message_context=jid,
                data=body)

    def quit(self):
        #TODO: disconnect gracefully
        self.ui.quit()

    ##
    ## Commands
    ##

    def _connect(self, line):
        jid = next(line)
        password = next(line)

        conn = self.client_class(self, jid, password)
        conn.connect()

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
        self.connections[self.connection_context].send_message(jid, body, mtype='chat')
        self.ui.enqueue(level=LineParser.MESSAGE_SENT,
                connection=self.connection_context,
                message_context=jid,
                data=body)

    def _accounts(self, line):
        if self.connections:
            data = 'Accounts:\n'
            for i in range(len(self.connections)):
                data += '%d: %s' % (i, self.connections[i].boundjid.bare)
        else:
            data = 'No accounts connected'

        self.ui.enqueue(level=LineParser.INFO,
                connection=None,
                message_context=None,
                data=data)

    def _quit(self, line):
        self.quit()
