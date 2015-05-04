import math


class Position(object):
    smooth = 20
    roll, pitch, yaw = 0, 0, 0
    rx = 0
    ry = 0
    rz = 0
    rx_offset = 0
    ry_offset = 0
    rz_offset = 0
    rx_static_offset = 0
    ry_static_offset = -5
    rz_static_offset = 0

    zoom = -2

    roll_history = [0 for i in range(smooth)]
    pitch_history = [0 for i in range(smooth)]
    yaw_history = [0 for i in range(smooth)]
    yaw_smooth = 0
    roll_smooth = 0
    pitch_smooth = 0

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
        self.yaw_smooth = sum(self.yaw_history) / len(self.yaw_history)+self.ry_offset+self.ry_static_offset
        self.pitch_smooth = -sum(self.roll_history) / len(self.roll_history)+self.rx_offset+self.rx_static_offset
        self.roll_smooth = sum(self.pitch_history) / len(self.pitch_history)+self.ry_offset+self.ry_static_offset

    def get_angles(self):
        return {'x': -sum(self.roll_history) / len(self.roll_history)+self.rx_offset+self.rx_static_offset,
                'y': sum(self.pitch_history) / len(self.pitch_history)+self.ry_offset+self.ry_static_offset}


