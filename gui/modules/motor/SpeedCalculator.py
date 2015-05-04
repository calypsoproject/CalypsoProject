import time
from ..joystick.Read import ReadJoystick
from ..PID.PIDControl import PID_Controller
from ..dof9.Position import Position


class SpeedCalculator(object):
    # affects speed calculation
    responsiveness = 10

    # max angles
    def __init__(self, ip, max_incline=45, max_roll=90, joystick_incline=True, joystick_roll=False, kp=1.5, ki=0, kd=0.3, mode=0):
        self.mode = mode
        self.joystick_incline = joystick_incline
        self.joystick_roll = joystick_roll
        self.kd = kd
        self.ki = ki
        self.kp = kp
        self.max_incline = max_incline
        self.max_roll = max_roll

        self.joystick = ReadJoystick()
        self.joystick.initialize()

        self.position = Position()
        self.position.start_retrieving_data(ip)

        self.pid = PID_Controller(self.kp, self.ki, self.kd)
        self.incline_time = time.time()
        self.roll_time = time.time()

        self.incline_factor = 1.0 / self.max_incline
        self.roll_factor = 1.0 / self.max_roll

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
