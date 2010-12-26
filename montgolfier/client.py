import sleekxmpp


class Client(sleekxmpp.ClientXMPP):
    """A layer of abstraction over SleekXMPP

    """

    def __init__(self, lp, jid, password):
        self.lp = lp
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("message", self.message)

    def connect(self):
        if sleekxmpp.ClientXMPP.connect(self):
            self.process(threaded=True)

    def session_start(self, event):
        self.lp.connected(self)

        self.get_roster()
        self.send_presence()

    def message(self, msg):
        self.lp.message_received(self, msg['from'].bare, msg['body'])
