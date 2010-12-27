import logging

from montgolfier.lineparser import LineParser
from montgolfier.client import Client
from montgolfier.ui import UI


class LogHandler(logging.Handler):
    def __init__(self, ui):
        logging.Handler.__init__(self)
        self.ui = ui

    def emit(self, msg):
        self.ui.enqueue(level=LineParser.ERROR,
                connection=self.ui.lp.connection_context,
                message_context=self.ui.lp.message_context,
                data=msg)


def run():
    ui = UI(client_class=Client, lineparser_class=LineParser)
    logging.getLogger().addHandler(LogHandler(ui))
    logging.getLogger().setLevel(logging.DEBUG)
    ui.mainloop()
