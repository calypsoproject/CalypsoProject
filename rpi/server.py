import socket

__author__ = 'prog'

class Server:
    def __init__(self, listen_port):
        self.send_queue = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), listen_port))
        self.socket.listen(1)

    def communication_thread(self):
        while 1:
            try:
                clientsocket, address = self.socket.accept()
                clientsocket.setblocking(False)
                self.recieved = clientsocket.makefile()
            except Exception, e:
                print 'Server, communication thread, mainloop:', e
