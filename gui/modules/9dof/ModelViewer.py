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
import sys
from OpenGL.GLU import *
from pygame.constants import *
import threading

# IMPORT OBJECT LOADER
from objloader import *

class ModelViewerThread(object):
    rx, ry, rz = (0, 0, 0)
    exit = False
    zoom = 0
    resizing = False
    def __init__(self, viewport=(800, 600)):
        self.viewport = viewport
        pygame.init()
        self.srf = pygame.display.set_mode(viewport, OPENGLBLIT | DOUBLEBUF | RESIZABLE)

        glLightfv(GL_LIGHT1, GL_POSITION,  (1.7, 0.5, -1.5, 1.5))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (2.0, 1.8, 1.8, 0.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.0, 0.9, 0.7, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (1.0, 0.8, 0.3, 1.0))
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 0.50])
        glMaterialfv(GL_FRONT, GL_SHININESS, [50.0])
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT1)
        glEnable(GL_DEPTH_TEST)

        # LOAD OBJECT AFTER PYGAME INIT
        self.obj = OBJ('go5-b-005.obj', swapyz=True)

        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = viewport
        gluPerspective(90.0, width/float(height), 1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glClearColor(0.01, 0.03, 0.1, 1.0)

    def update(self, parent=None):
        for e in pygame.event.get():
            if e.type == QUIT:
                if parent:
                    parent.exit = True
                pygame.display.quit()
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_ESCAPE:
                if parent:
                    parent.exit = True
                pygame.display.quit()
                sys.exit()
            elif e.type == KEYDOWN and e.key == K_SPACE:
                if parent:
                    parent.home()
                    print 'ok'

            elif e.type==VIDEORESIZE:
                self.viewport = e.dict['size']
                self.resizing = True
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # RENDER OBJECT
        glTranslate(0, 0., self.zoom)
        glRotate(self.ry, 1, 0, 0)
        glRotate(self.rx, 0, 1, 0)
        glRotate(self.rz, 0, 0, 1)
        glCallList(self.obj.gl_list)

        pygame.display.flip()

class ModelViewer(object):
    smooth = 20
    roll, pitch, yaw = 0, 0, 0
    rx = 0
    ry = 0
    rz = 0
    rx_offset = 0
    ry_offset = 0
    rz_offset = 0
    rx_static_offset = 0
    ry_static_offset = 30
    rz_static_offset = 90

    zoom = -2
    exit = False
    
    roll_history = [0 for i in range(smooth)]
    pitch_history = [0 for i in range(smooth)]
    yaw_history = [0 for i in range(smooth)]
    def __init__(self):
        atexit.register(self.at_exit)
        threading.Thread(target=self.run).start()
        threading.Thread(target=self.orientation_updater).start()

    def home(self):
        self.rx_offset = 360 - self.rx
        self.ry_offset = 360 - self.ry
        self.rz_offset = 360 - self.rz

    def run(self):
        mv = ModelViewerThread()
        while 1:
            mv.ry = self.ry + self.ry_offset + self.ry_static_offset
            mv.rx = self.rx + self.rx_offset + self.rx_static_offset
            mv.rz = self.rz + self.rz_offset + self.rz_static_offset
            mv.zoom = self.zoom
            mv.clock.tick(30)
            mv.update(self)
            if mv.resizing:
                while mv.resizing:
                    mv.resizing = False
                    for i in range(2):
                        mv.update()
                        mv.clock.tick(10)
                        size = mv.viewport
                        pygame.display.set_mode(size, OPENGL | DOUBLEBUF | RESIZABLE)
                        glViewport(0, 0, *size)
                        glMatrixMode(GL_PROJECTION)
                        glLoadIdentity()
                        width, height = size
                        gluPerspective(90.0, width/float(height), 1, 100.0)
                        glEnable(GL_DEPTH_TEST)
                        glMatrixMode(GL_MODELVIEW)
                        mv.ry = self.ry + self.ry_offset
                        mv.rx = self.rx + self.rx_offset
                        mv.rz = self.rz + self.rz_offset
                        mv.zoom = self.zoom
                        mv.clock.tick(30)
                        mv.update(self)
                print 'ended resizing'

    def update_data(self, accel, gyro, compass):
        ax, ay, az = accel['x'], accel['y'], accel['z']
        self.pitch = math.atan(ax/math.sqrt(ay**2 + az**2)) * 180/math.pi
        self.roll = math.atan(ay/math.sqrt(ax**2 + az**2)) * 180/math.pi
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

    def orientation_updater(self):
        while not self.exit:
            self.roll_history.pop(0)
            self.roll_history.append(self.roll)
            self.pitch_history.pop(0)
            self.pitch_history.append(self.pitch)
            self.yaw_history.pop(0)
            self.yaw_history.append(self.yaw)

            # if self.rx == 360:
            #     self.rx = 0
            # else:
            #     self.rx += 1

            self.ry = - sum(self.roll_history) / len(self.roll_history)
            self.rz = sum(self.pitch_history) / len(self.pitch_history)
            # self.rz = sum(self.yaw_history) / len(self.yaw_history)
            print self.rz, self.ry
            time.sleep(1/30.0)

    def at_exit(self):
        self.socket.close()


if __name__ == '__main__':
    mv = ModelViewer()
    mv.start_retrieving_data('192.168.0.104')
