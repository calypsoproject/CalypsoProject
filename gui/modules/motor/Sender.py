import socket
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
    prev_speeds = speeds

    def __init__(self, ip, port=8888, sender_check_interval=0.5):
        self.sender_check_interval = sender_check_interval
        self.ip = ip
        self.port = port
    
    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip, self.port))
        s.settimeout(1)

    def sender_thread(self):
        while 1:
            if self.speeds != self.prev_speeds:
                print self.speeds
            for motor in self.speeds:
                speed = self.speeds[motor]
                if int(speed) != int(self.prev_speeds[motor]):
                    try:
                        s.sendall('motor_handler.motor[\'%s\'].set_speed(%i)' % (motor, float(speed)))
                        while s.recv(1024) == 'false':
                            time.sleep(0.1)
                            s.sendall('motor_handler.motor[\'%s\'].set_speed(%i)' % (motor, float(speed)))
                            print 'repeating', speed
                    except Exception, e:
                        print e
                        try:
                            s.close()
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.connect((self.ip, self.port))
                        except:
                            pass
                self.prev_speeds = self.speeds
            time.sleep(self.sender_check_interval)