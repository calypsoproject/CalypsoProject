import pickle
import socket
import threading

__author__ = 'prog'

class Server:
    def __init__(self, command_handler, listen_port):
        """ command_handler ... is called with recieved command and client socket as parameters
            timeout ... how long it will wait for message before closing clientsocket
        """
        self.command_handler = command_handler
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])  # socket.gethostname() returns wrong value
        self.socket.bind((hostname, listen_port))
        self.socket.listen(1)
        threading.Thread(target=self.communication_thread).start()

    def communication_thread(self):
        """ waits for connection with client and spawns
            new thread for each connection
        """
        while 1:
            try:
                clientsocket, address = self.socket.accept()
                threading.Thread(target=self.clientsocket_thread, args=[clientsocket]).start()
            except Exception, e:
                print 'Server, communication thread:', e

    def clientsocket_thread(self, clientsocket):
        """ recieves commands, calls handler method and
            returns pickled result until connection is alive.
        """
        while 1:
            try:
                result = self.command_handler(clientsocket.recv(8192), clientsocket)
                clientsocket.sendall(pickle.dumps(result))
            except:
                clientsocket.close()
                break