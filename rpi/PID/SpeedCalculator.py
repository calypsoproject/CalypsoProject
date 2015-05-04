import atexit
import threading
import time
from PIDControl import PID_Controller


class SpeedCalculator(object):
    # affects speed calculation
    responsiveness = 10

    exit = False

    # max angles
    def __init__(self, position, joystick_updater, motor_handler, max_incline=45, max_roll=90, joystick_incline=True, joystick_roll=False, kp=1, ki=0, kd=0.3, mode=0, max_speed=20, min_speed=10, floating_speed=30):
        self.floating_speed = floating_speed
        self.max_speed = max_speed
        self.min_speed = min_speed
        self.mode = mode
        self.joystick_incline = joystick_incline
        self.joystick_roll = joystick_roll
        self.kd = kd
        self.ki = ki
        self.kp = kp
        self.max_incline = max_incline
        self.max_roll = max_roll
        self.motor_handler = motor_handler

        self.joystick = joystick_updater

        self.position = position

        self.pid = PID_Controller(self.kp, self.ki, self.kd)
        self.incline_time = time.time()
        self.roll_time = time.time()

        self.incline_factor = 1.0 / self.max_incline
        self.roll_factor = 1.0 / self.max_roll
        atexit.register(self.at_exit)
        t = threading.Thread(target=self.calculate_corrections)
        t.daemon = True
        t.start()

    def at_exit(self):
        self.exit = True

    def calculate_incline(self):
        if self.mode == 0:
            target = self.joystick.in_out * self.max_incline
        else:
            target = 0
        current = self.position.pitch_smooth
        correction = self.pid.getCorrection(target, current, time.time() - self.incline_time)
        scaled_correction = self.incline_factor * correction
        scaled_correction = scaled_correction if 0 >= scaled_correction or scaled_correction <= 1 else 1
        scaled_correction = scaled_correction if 0 <= scaled_correction or scaled_correction >= -1 else -1
        self.roll_time = time.time()
        return scaled_correction

    def calculate_roll(self):
        if self.mode == 1:
            target = self.joystick.in_out * self.max_roll
        else:
            target = 0
        current = self.position.roll_smooth
        correction = self.pid.getCorrection(target, current, time.time() - self.roll_time)
        scaled_correction = self.roll_factor * correction
        scaled_correction = scaled_correction if 0 >= scaled_correction or scaled_correction <= 1 else 1
        scaled_correction = scaled_correction if 0 <= scaled_correction or scaled_correction >= -1 else -1
        self.roll_time = time.time()
        return scaled_correction
    
    def calculate_corrections(self):
        speeds = {
            'fl': 0,
            'fr': 0,
            'bl': 0,
            'br': 0,
            'ml': 0,
            'mr': 0
        }
        while not self.exit:
            time.sleep(0.2)
            incline_correction = -self.calculate_incline()*self.max_speed
            roll_correction = self.calculate_roll()*self.max_speed

            fl = incline_correction + roll_correction
            fr = incline_correction + roll_correction
            br = -incline_correction - roll_correction
            bl = -incline_correction - roll_correction

            max_val = max([abs(fl), abs(fr), abs(br), abs(bl)])
            k = float(self.max_speed) / max_val
            if max_val > self.max_speed:
                fl *= k
                fr *= k
                bl *= k
                br *= k

            speeds['fl'] = self.floating_speed+fl
            speeds['fr'] = self.floating_speed+fr
            speeds['br'] = self.floating_speed+br
            speeds['bl'] = -(self.floating_speed+bl)
            speeds['ml'] = self.joystick.right_left
            speeds['mr'] = -self.joystick.right_left

            if self.joystick.throttle != 0:
                kf_forward = 1/self.joystick.throttle
            else:
                kf_forward = 1
            speed_diff = self.max_speed - self.min_speed

            if self.joystick.throttle != 0:
                speeds['mr'] = (self.joystick.throttle + speeds['mr'] / kf_forward if speeds['mr'] < speeds['ml'] else self.joystick.throttle)*speed_diff
                speeds['ml'] = (self.joystick.throttle + speeds['ml'] / kf_forward if speeds['mr'] > speeds['ml'] else self.joystick.throttle)*speed_diff
            else:
                speeds['mr'] *= self.max_speed
                speeds['ml'] *= self.max_speed

            for k in speeds.keys():
                speeds[k] = round(speeds[k])
            for i in ['mr', 'ml']:
                if speeds[i] != 0:
                    if speeds[i] > 0:
                        speeds[i] += self.min_speed
                    if speeds[i] < 0:
                        speeds[i] -= self.min_speed
            speeds['ml'] = -speeds['ml']
            # for motor in speeds:
            #     self.motor_handler.motor[motor].set_speed(speeds[motor])
            print speeds
