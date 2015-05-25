import atexit
import threading
import time
from PIDControl import PID_Controller
from Position import Position
from JoystickUpdater import JoystickUpdater as Joystick


class SpeedCalculator(object):
    # affects speed calculation
    responsiveness = 10
    origin = 'Calypso/SpeedCalculator'
    enabled = False

    # max angles
    def __init__(self, position, joystick_updater, motor_handler, logger, max_incline=45, max_roll=90, joystick_incline=True,
                 joystick_roll=False, kp=2, ki=0, kd=0, kpp=None, kip=None, kdp=None, mode=1, max_speed=50, min_speed=4, floating_speed=50,
                 interval=0.2):
        self.logger = logger
        self.interval = interval
        self.floating_speed = floating_speed
        self.max_speed = max_speed
        self.abs_max_speed = self.max_speed + self.floating_speed
        self.min_speed = min_speed
        self.max_speed_change = min([self.abs_max_speed - self.floating_speed, self.floating_speed - self.min_speed])
        self.mode = mode
        self.joystick_incline = joystick_incline
        self.joystick_roll = joystick_roll

        self.kdr = kd
        self.kir = ki
        self.kpr = kp
        self.kdp = kdp if kdp else kd
        self.kip = kip if kip else ki
        self.kpp = kpp if kpp else kp
        self.max_incline = max_incline
        self.max_roll = max_roll
        self.motor_handler = motor_handler

        self.joystick = joystick_updater

        self.position = position

        self.pid_roll = PID_Controller(self.kpr, self.kir, self.kdr)
        self.pid_incline = PID_Controller(self.kpp, self.kip, self.kdp)

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
        if self.joystick_incline:
            target = self.joystick.in_out * self.max_incline
        else:
            target = 0
        current = self.position.pitch_smooth
        correction = self.pid_incline.getCorrection(target, current, time.time() - self.incline_time)
        scaled_correction = self.incline_factor * correction
        scaled_correction = scaled_correction if 0 >= scaled_correction or scaled_correction <= 1 else 1
        scaled_correction = scaled_correction if 0 <= scaled_correction or scaled_correction >= -1 else -1
        self.roll_time = time.time()
        return scaled_correction

    def calculate_roll(self):
        if self.joystick_roll:
            target = self.joystick.in_out * self.max_roll
        else:
            target = 0
        current = self.position.roll_smooth
        correction = self.pid_roll.getCorrection(target, current, time.time() - self.roll_time)
        scaled_correction = self.roll_factor * correction
        scaled_correction = scaled_correction if 0 >= scaled_correction or scaled_correction <= 1 else 1
        scaled_correction = scaled_correction if 0 <= scaled_correction or scaled_correction >= -1 else -1
        self.roll_time = time.time()
        return scaled_correction

    def set(self, floating_speed=None, max_speed=None, min_speed=None, max_incline=None, max_roll=None):
        if floating_speed:
            self.floating_speed = floating_speed
        if max_speed:
            self.max_speed = max_speed
        if min_speed:
            self.min_speed = min_speed

        return 'ok'

    def calculate_corrections(self):
        speeds = {
            'fl': 0,
            'fr': 0,
            'bl': 0,
            'br': 0,
            'ml': 0,
            'mr': 0
        }
        speed_diff = 100 - self.min_speed
        while 1:
            time.sleep(self.interval)

            incline_correction = -self.calculate_incline() * self.max_speed
            roll_correction = self.calculate_roll() * self.max_speed
            if self.mode == 0:
                roll_correction = roll_correction + self.min_speed if roll_correction > 0 else roll_correction
                roll_correction = roll_correction - self.min_speed if roll_correction < 0 else roll_correction
                incline_correction = incline_correction + self.min_speed if incline_correction > 0 else incline_correction
                incline_correction = incline_correction - self.min_speed if incline_correction < 0 else incline_correction

            fl = incline_correction + roll_correction
            fr = incline_correction - roll_correction
            br = -incline_correction - roll_correction
            bl = -incline_correction + roll_correction

            max_val = max([abs(fl), abs(fr), abs(br), abs(bl)])
            if max_val > self.max_speed:
                k = float(self.max_speed) / max_val
                fl *= k
                fr *= k
                bl *= k
                br *= k

            if self.mode == 1:
                floating_speed = self.floating_speed + self.max_speed_change * self.joystick.elevation
                fl += floating_speed
                fr += floating_speed
                bl += floating_speed
                br += floating_speed

                min_val = min([fl, fr, br, bl])
                add = self.min_speed - min_val
                if min_val < self.min_speed:
                    fl += add
                    fr += add
                    bl += add
                    br += add

                max_val = max([abs(fl), abs(fr), abs(br), abs(bl)])
                if max_val > self.abs_max_speed:
                    k = float(self.abs_max_speed) / max_val
                    fl *= k
                    fr *= k
                    bl *= k
                    br *= k

            speeds['fl'] = -fl
            speeds['fr'] = -fr
            speeds['br'] = -br
            speeds['bl'] = -bl
            speeds['ml'] = self.joystick.right_left
            speeds['mr'] = -self.joystick.right_left

            if self.joystick.throttle != 0:
                kf_forward = 1 / self.joystick.throttle
            else:
                kf_forward = 1

            if self.joystick.throttle != 0:
                mr = (self.joystick.throttle + speeds['mr'] / kf_forward if speeds['mr'] < speeds[
                    'ml'] else self.joystick.throttle) * speed_diff
                speeds['ml'] = (self.joystick.throttle + speeds['ml'] / kf_forward if speeds['mr'] > speeds[
                    'ml'] else self.joystick.throttle) * speed_diff
                speeds['mr'] = mr
            else:
                speeds['mr'] *= 100
                speeds['ml'] *= 100

            for k in speeds.keys():
                speeds[k] = round(speeds[k])
            for i in ['mr', 'ml']:
                if speeds[i] != 0:
                    if speeds[i] > 0:
                        speeds[i] += self.min_speed
                    if speeds[i] < 0:
                        speeds[i] -= self.min_speed

            speeds['ml'] = -speeds['ml']

            for motor in speeds:
                self.motor_handler.motor[motor].set_speed(speeds[motor])
            self.logger.verbose(self.origin+'/calculate_corrections', speeds)
            print speeds

if __name__ == '__main__':
    sc = SpeedCalculator(Position(), Joystick(), None, None)