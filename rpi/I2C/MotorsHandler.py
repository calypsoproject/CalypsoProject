import threading
import time
from Motor import Motor
import RPi.GPIO as GPIO


class MotorsHandler():
    motor = {}
    initialized_motors = []
    reset_delay = 1  # sec
    resetting = False

    def __init__(self, i2c_common):
        self.i2c_common = i2c_common

    def reset_boards(self, from_thread=False):
        """ sends 3.3V to controllers
        """
        if not from_thread:
            if not self.resetting:
                self.resetting = True
                threading.Thread(target=self.reset_boards, args=[True])
            return
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(11, GPIO.OUT)
        GPIO.output(11, True)
        time.sleep(self.reset_delay)
        GPIO.output(11, False)

    def add_motor(self, motor_instance):
        self.initialized_motors.append(motor_instance)

    def new_motor(self, motor_address, motor_name, acceleration=2, kp_hi=None, kp_lo=None):
        new_motor = Motor(motor_address, self.i2c_common, motor_name, acceleration, kp_hi, kp_lo)
        self.motor[motor_name] = new_motor
        self.initialized_motors.append(new_motor)
        return new_motor

    def enable(self, block=False):
        for motor in self.initialized_motors:
            motor.enable_system()
        if block:
            time.sleep(Motor.enable_timeout)

    def disable(self):
        for motor in self.initialized_motors:
            motor.disable_system()

    def set_accel(self, acceleration):
        for motor in self.initialized_motors:
            motor.set_accel(acceleration)

    def set_speed(self, speed):
        for motor in self.initialized_motors:
            motor.set_speed(speed)

    def set_kp(self, kp):
        for motor in self.initialized_motors:
            motor.set_kp(kp)
        print 'kp:', kp

    def get_status(self):
        result = {}
        for motor in self.initialized_motors:
            result[str(motor)] = motor.get_values()
        return result