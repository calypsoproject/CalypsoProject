import socket
import threading
import time
from Read import ReadJoystick


def get_prefix(val):
    if val > 0:
        return 1
    else:
        return -1

class Calculate:
    initialized = False
    def __init__(self, max_speed=50, min_speed=10):
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.joystick = ReadJoystick()
        threading.Thread(target=self.init_joystick).start()

    def init_joystick(self):
        while min(map(abs, self.joystick.axes[2:])) == 0: time.sleep(0.1)
        while max(map(abs, self.calculate(force=True).values())) != 0: time.sleep(0.1)
        self.initialized = True

    def calculate(self, mode=1, force=False):
        if not self.initialized and not force:
            return {
            'fl': 0,
            'fr': 0,
            'bl': 0,
            'br': 0,
            'ml': 0,
            'mr': 0
            }
        right_left = self.joystick.right_left
        in_out = self.joystick.in_out
        throttle = self.joystick.throttle
        elevation = self.joystick.elevation

        if mode == 0:
            fl_value = -right_left - in_out + elevation
            fr_value = right_left - in_out + elevation
            bl_value = -right_left + in_out + elevation
            br_value = right_left + in_out + elevation
            ml_value = 0
            mr_value = 0
        else:
            fl_value = -in_out + elevation
            fr_value = -in_out + elevation
            bl_value = in_out + elevation
            br_value = in_out + elevation
            ml_value = right_left
            mr_value = -right_left
            
            fl_value = fl_value if abs(fl_value) <= 1 else get_prefix(fl_value)*1
            fr_value = fr_value if abs(fr_value) <= 1 else get_prefix(fr_value)*1
            bl_value = bl_value if abs(bl_value) <= 1 else get_prefix(bl_value)*1
            br_value = br_value if abs(br_value) <= 1 else get_prefix(fr_value)*1

        values = {
            'fl': fl_value,
            'fr': fr_value,
            'bl': -bl_value,
            'br': br_value,
            'ml': ml_value,
            'mr': mr_value
        }

        if round(throttle, 3) == 0:
            max_val = max(map(abs, values.values()))
            if max_val > 1:
                kf = 1.0/max_val
            else:
                kf = 1
            values = {k: values[k]/kf for k in values.keys()}
        else:
            if throttle != 0:
                kf_forward = 1/throttle
            else:
                kf_forward = 1
            values['mr'] = throttle + values['mr'] / kf_forward if values['mr'] < values['ml'] else throttle
            values['ml'] = throttle + values['ml'] / kf_forward if values['mr'] > values['ml'] else throttle

        values['ml'] = -values['ml']
        values['mr'] = values['mr']
        kf = (self.max_speed - self.min_speed)
        values = {k: round(values[k] * kf) for k in values.keys()}
        for k in values.keys():
            if values[k] != 0:
                if values[k] > 0:
                    values[k] += self.min_speed
                else:
                    values[k] -= self.min_speed
        return values




    def test(self):
        while 1:
            speeds = self.calculate()
            print speeds
            time.sleep(0.5)

if __name__ == '__main__':
    host = '10.42.0.13'
    port = 8888
    c = Calculate()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.settimeout(1)
    prev = c.calculate()
    while 1:
        speeds = c.calculate()
        if speeds != prev:
            print speeds
        for motor in speeds:
            speed = speeds[motor]
            if int(speed) != int(prev[motor]):
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
                        s.connect((host, port))
                    except:
                        pass    
        prev = speeds
