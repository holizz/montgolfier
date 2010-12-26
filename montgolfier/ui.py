class UI:
    def __init__(self, client_class, lineparser_class):
        self.lp = lineparser_class(client_class, ui=self)
        self._quit = False

    def mainloop(self):
        while not self._quit:
            try:
                i = input('> ')
            except EOFError:
                pass
            else:
                self.lp.parse(i)

    def quit(self):
        self._quit = True

    def enqueue(self, level, connection, message_context, data):
        print((level,connection,message_context,data))
