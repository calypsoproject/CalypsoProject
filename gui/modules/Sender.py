import socket
import threading
import time

__author__ = 'prog'

class Sender(object):
    # order: in_out, right_left, throttle, elevation
    joystick = [0, 0, 0, 0]
    prev_joystick = list([0, 0, 0, 0])
    def __init__(self, ip, port=8888, sender_check_interval=0.1):
        self.ip = ip
        self.port = port

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))
        self.s.settimeout(1)

    def send(self):
        self.connect()
        if self.joystick != self.prev_joystick:
            print self.joystick
            self.s.sendall('joystick.update(%s, %s, %s, %s)' % (self.joystick[0],
                                                                self.joystick[1],
                                                                self.joystick[2],
                                                                self.joystick[3]))
            self.s.recv(1024)
        self.prev_joystick = list(self.joystick)