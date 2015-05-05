import atexit
import json
import socket
import threading
import urllib

__author__ = 'prog'

class Server:
    def __init__(self, calypso_instance, listen_port):
        """ command_handler ... is called with recieved command and client socket as parameters
            timeout ... how long it will wait for message before closing clientsocket
        """
        self.calypso_instance = calypso_instance
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = ([(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1])  # socket.gethostname() returns wrong value
        self.socket.bind((self.hostname, listen_port))
        self.socket.listen(1)
        atexit.register(self.at_exit)
        t = threading.Thread(target=self.communication_thread)
        t.daemon = True
        t.start()

    def at_exit(self):
        self.socket.close()

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
                result = self.exec_command(urllib.unquote(clientsocket.recv(8192)))
                clientsocket.sendall(result)
            except:
                clientsocket.close()
                break

    def exec_command(self, command):
        try:
            result = None
            exec 'result = self.calypso_instance.' + command
            return json.dumps(result)
        except Exception, e:
            return str(e)