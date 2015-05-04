import socket
import threading
import time

__author__ = 'prog'

class SpeedSender(object):
    speeds = {
        'fl': 0,
        'fr': 0,
        'bl': 0,
        'br': 0,
        'ml': 0,
        'mr': 0
    }
    prev_speeds = dict(speeds)

    def __init__(self, ip, port=8888, sender_check_interval=0.1):
        self.sender_check_interval = sender_check_interval
        self.ip = ip
        self.port = port
        threading.Thread(target=self.sender_thread).start()

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip, self.port))
        self.s.settimeout(1)

    def sender_thread(self):
        self.connect()
        while 1:
            if self.speeds != self.prev_speeds:
                print self.speeds
            for motor in self.speeds:
                speed = self.speeds[motor]
                if int(speed) != int(self.prev_speeds[motor]):
                    try:
                        self.s.sendall('motor_handler.motor[\'%s\'].set_speed(%i)' % (motor, float(speed)))
                        while self.s.recv(1024) == 'false':
                            time.sleep(0.1)
                            self.s.sendall('motor_handler.motor[\'%s\'].set_speed(%i)' % (motor, float(speed)))
                            print 'repeating', speed
                    except Exception, e:
                        print e
                        try:
                            self.connect()
                        except:
                            pass
            self.prev_speeds = dict(self.speeds)
            time.sleep(self.sender_check_interval)