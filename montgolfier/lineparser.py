class LineParser:
    def __init__(self, client):
        self.client = client
        self.connections = []

    def parse(self, cmd):
        c = cmd.split()
        if c[0] == '/connect':
            self._connect(*c[1:])
        elif c[0] == '/msg':
            self._msg(*c[1:])
        else:
            self._msg(None, cmd)

    def _connect(self, jid, password=None):
        if password == None:
            raise NotImplementedError

        conn = self.client(jid, password)

        if conn.connect():
            conn.process(threaded=True)

        self.connections.append(conn)
        self.connection_context = len(self.connections) - 1

    def _msg(self, jid, *body):
        if jid:
            self.message_context = jid
        else:
            jid = self.message_context

        body = ' '.join(body)
        self.connections[self.connection_context].message(jid, body)
