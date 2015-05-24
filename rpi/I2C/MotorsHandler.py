import Adafruit_BBIO.GPIO as GPIO
import time
from Motor import Motor


class MotorsHandler():
    motor = {}
    initialized_motors = []
    reset_delay = 1  # sec
    resetting = False

    def __init__(self, i2c_common, logger):
        self.logger = logger
        self.i2c_common = i2c_common
        self.reset_boards()

    def reset_boards(self):
        """ sends 3.3V to controllers
        """
        GPIO.setup("P8_8", GPIO.OUT)
        GPIO.output("P8_8", GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output("P8_8", GPIO.LOW)

    def add_motor(self, motor_instance):
        self.initialized_motors.append(motor_instance)

    def new_motor(self, motor_address, motor_name, acceleration=2, kp_hi=None, kp_lo=None):
        new_motor = Motor(motor_address, self.i2c_common, motor_name, acceleration, self.logger, kp_hi, kp_lo)
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

    def get_status(self):
        result = {}
        for motor in self.initialized_motors:
            result[str(motor)] = motor.get_values()
        return result

    def get_speeds(self):
        return {i: self.motor[i].last_speed for i in self.motor}
