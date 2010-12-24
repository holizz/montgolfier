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

    def _msg(self, *args):
        args = list(args)

        # -account
        if args[0] == '-account':
            args.pop(0)
            self.set_connection(args.pop(0))

        # jid, body
        jid = args.pop(0)
        body = ' '.join(args)
        if jid:
            self.message_context = jid
        else:
            jid = self.message_context

        # Send it
        self.connections[self.connection_context].message(jid, body)

    def get_connection(self, jid):
        for i in range(len(self.connections)):
            if self.connections[i].jid == jid:
                return i
        raise IndexError

    def set_connection(self, jid):
        self.connection_context = self.get_connection(jid)
