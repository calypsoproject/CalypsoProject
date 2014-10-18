__author__ = 'muzik.bot.nu'

import os
import sys
import math
import socket
import time
import threading



from classes.Motor import Motor
from classes.Communicator import Communicator
from classes.Sensors import Sensors

RECV_LEN = 1024
SEND_LEN = 1024
HOST = "192.168.137.1"
PORT = 4444




class ConnectSocket():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.connect()
    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.s = self.socket.makefile()
    def sendData(self, data):
        self.socket.send(data+"\n")
    def getData(self):
        return self.s.readline().strip()
    def close(self):
        self.socket.close()


communicator = Communicator(0)

right_motor = Motor(0x0f, communicator, "Left motor")
left_motor = Motor(0x0e, communicator, "Right motor")
sensors = Sensors()


def socketing():
    s = ConnectSocket(HOST, PORT)
    while 1:
        s.sendData(str(right_motor.get_speed())+"|"+str(left_motor.get_speed())+"|"+sensors.retstr)
        response = s.getData().split("|")


        speed1, dir1, speed2, dir2 = map(int, response)
        right_motor.set_speed(speed1, dir1)
        left_motor.set_speed(speed2, dir2)
        print(left_motor.last_speed, left_motor.final_speed, left_motor.last_accl)
        time.sleep(0.1)
    left_motor.stop()
    right_motor.stop()

def socketing1():
    s = ConnectSocket(HOST, PORT)
    while 1:
        s.sendData(sensors.retstr)
        response = s.getData().split("|")
        speed1, dir1, speed2, dir2 = map(int, response)
        time.sleep(0.1)

try:
    socketing()
except KeyboardInterrupt:
    os.system("sudo killall python")
