class UI:
    def __init__(self, client_class, lineparser_class):
        self.lp = lineparser_class(client_class, output=self)

    def mainloop(self):
        while True:
            i = input('> ')
            self.lp.parse(i)

    def enqueue(self, level, connection, message_context, data):
        print((level,connection,message_context,data))
