import socket
from server import Server
from I2C.Motors import Motors
__author__ = 'prog'

class Calypso:
    def __init__(self):
        # self.server = Server(listen_port=8888)
        self.i2c =