__author__ = 'delavnica'

import socket
import threading
import select
import time
from msvcrt import getch
import serial


out_file = open("log" + str(time.time()) + ".txt", "w")


class ArduinoListener(threading.Thread):
    def __init__(self, serial_port, baud_rate=38400, timeout=1, lock=None):
        super(ArduinoListener, self).__init__()
        self.serial_comm = serial.Serial(serial_port, baudrate=baud_rate, timeout=timeout)
        self.serial_comm.close()
        self.serial_comm.open()
        if lock is None:
            self.lock = threading.Lock()
        else:
            self.data = lock
        self.data = []
        print("init")
        out_file.write("init\n")

    def run(self):
        out_file.write("runnning\n")
        print("running")
        self.listen()

    def listen(self):
        while 1:
            try:
                line = self.serial_comm.readline().strip().split("|")
                speed1, dir1, speed2, dir2 = map(int, line)
            except:
                out_file.write("except\n")
                print("except")
                speed1, dir1, speed2, dir2 = 0, 1, 0, 1
            speed1 = int(speed1 / 1024.0 * 100)
            speed2 = int(speed2 / 1024.0 * 100)
            if not 0 <= speed1 <= 100:
                speed1 = 0
            if not 0 <= speed2 <= 100:
                speed2 = 0
            dir1 = int(dir1 / 500 + 1)
            dir2 = int(dir2 / 500 + 1)

            with self.lock:
                self.data = (speed1, dir1, speed2, dir2)


    def getData(self):
        return self.data


arduinoListener = ArduinoListener(5)
arduinoListener.start()
while 1:
    time.sleep(0.2)
    print(arduinoListener.getData())
    break

SEND_LEN = 1024
RECV_LEN = 1024

HOST = ''
PORT = 4444

data1 = False
a = 0
b = 0
en = False


def readburek():
    global data1, a, b, en
    #lock = threading.Lock()
    sp = 0
    pressed_left = False
    pressed_up = False
    pressed_right = False
    pressed_down = False
    la = 0
    lb = 0
    while 1:
        key = getch()
        #data1 = raw_input()
        if key == "w" and en:
            if sp < 100:
                sp += 1
            a, b = sp, sp
        elif key == "s" and en:
            if sp > -100:
                sp -= 1
            a, b = sp, sp
        if key == "a" and en:
            a = sp
            b = int(sp / 2)
        elif key == "d" and en:
            a = int(sp / 2)
            b = sp
        elif key == "k":
            a, b, sp = 0, 0, 0
        elif key == "u":
            en = (not en)
            print "enabled", en
            if not en:
                a, b, sp = 0, 0, 0
        if la != a or lb != b:
            data1 = True
            print "a = " + str(a) + " b = " + str(b)
            lb = b
            la = a


def keyHandler(event):
    foo = event.keysym
    print foo


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

read_list = [server_socket]

sendstr = ""
thr = threading.Thread(target=readburek)
thr.daemon = True
##thr.start()
try:
    while 1:
        readable, writable, errored = select.select(read_list, [], [])
        for s in readable:
            if s is server_socket:
                client_socket, address = server_socket.accept()
                read_list.append(client_socket)
                print "Connection from ", address
            else:
                sf = s.makefile()
                data = sf.readline().strip()
                data1 = 1
                if data:
                    if data1:
                        sendstr = str(int(en)) + "|" + str(a) + "|" + str(b)
                        sendstr = "|".join(map(str, arduinoListener.getData()))
                        s.send(sendstr + "\n")
                        print "sending: " + sendstr
                        data1 = 1
                    else:
                        s.send(str(int(en)) + "|n\n")
                    print "recieved: " + data

                    out_file.write(str(time.time()) + "##")
                    out_file.write("sending:" + sendstr + "##")
                    out_file.write("receieved:" + data + "\n")
                    out_file.flush()
                else:
                    s.close()
                    read_list.remove(s)
                    print "connection closed"
except KeyboardInterrupt:
    out_file.close()