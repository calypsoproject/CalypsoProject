# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import atexit
import math
import json
import socket
import time
import threading

class Position(object):
    smooth = 20
    roll, pitch, yaw = 0, 0, 0
    rx = 0
    ry = 0
    rz = 0
    rx_offset = 0
    ry_offset = 0
    rz_offset = 0
    rx_static_offset = 90
    ry_static_offset = 30
    rz_static_offset = 0

    zoom = -2
    exit = False
    
    roll_history = [0 for i in range(smooth)]
    pitch_history = [0 for i in range(smooth)]
    yaw_history = [0 for i in range(smooth)]

    def __init__(self):
        atexit.register(self.at_exit)

    def calibrate(self):
        self.rx_offset = 360 - self.rx
        self.ry_offset = 360 - self.ry
        self.rz_offset = 360 - self.rz

    def update_data(self, accel, gyro, compass):
        ax, ay, az = accel['x'], accel['y'], accel['z']
        self.pitch = math.atan(ax/math.sqrt(ay**2 + az**2)) * 180/math.pi
        self.roll = math.atan(ay/math.sqrt(ax**2 + az**2)) * 180/math.pi
        self.roll_history.pop(0)
        self.roll_history.append(self.roll)
        self.pitch_history.pop(0)
        self.pitch_history.append(self.pitch)
        self.yaw_history.pop(0)
        self.yaw_history.append(self.yaw)
        self.yaw = compass[0] + 60 / (compass[1] + 1)

    def start_retrieving_data(self, host, port=8888, interval=1/35.0, thread=False):
        if not thread:
            threading.Thread(target=self.start_retrieving_data, args=[host, port, interval, True]).start()
            return
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(1)
        while not self.exit:
            try:
                self.socket.sendall('sensors.get_values()')
                response = json.loads(self.socket.recv(1024))
                self.update_data(response['accelerometer'], response['gyroscope'], response['compass'])
            except Exception, e:
                print e
                try:
                    self.socket.close()
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((host, port))
                except:
                    pass
                time.sleep(0.1)

    def get_angles(self):
        return {'x': -sum(self.roll_history) / len(self.roll_history)+self.rx_offset+self.rx_static_offset,
                'y': sum(self.pitch_history) / len(self.pitch_history)+self.ry_offset+self.ry_static_offset}

    def at_exit(self):
        self.socket.close()


if __name__ == '__main__':
    mv = ModelViewer()
    mv.start_retrieving_data('192.168.0.107')
