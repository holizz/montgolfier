class LineParser:
    def __init__(self, client):
        self.client = client
        self.connections = []

    def parse(self, cmd):
        c = cmd.split()
        if c[0] == '/connect':
            self._connect(*c[1:])

    def _connect(self, jid, password=None):
        if password == None:
            raise NotImplementedError

        conn = self.client(jid, password)

        if conn.connect():
            conn.process(threaded=True)

        self.connections.append(conn)
