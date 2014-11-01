import threading
import time
import smbus
from Motor import Motor
import RPi.GPIO as GPIO


class MotorsHandler():
    initialized_motors = []
    reset_delay = 1  # sec
    resetting = False

    def __init__(self, rpi_revision=1):
        self.i2c_common = I2CCommon(rpi_revision)

    def reset_boards(self, from_thread=False):
        """ sends 3.3V to controllers
        """
        if not from_thread:
            if self.resetting == False:
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

    def new_motor(self, motor_address, motor_name='motor', rpi_revision=1, acceleration=2):
        try:
            motor = Motor(motor_address, self.i2c_common, motor_name, rpi_revision, acceleration)
        except Exception, e:
            return e
        self.initialized_motors.append(motor)
        return motor

    def enable_all(self, block=False):
        for motor in self.initialized_motors:
            motor.enable_system()
        if block:
            time.sleep(Motor.enable_timeout)

    def disable_all(self):
        for motor in self.initialized_motors:
            motor.disable_system()

    def change_accel_all(self, acceleration):
        for motor in self.initialized_motors:
            motor.change_accel(acceleration)

    def change_speed_all(self, speed):
        for motor in self.initialized_motors:
            motor.change_speed(speed)

    def get_values_from_all_motors(self):
        result = {}
        for motor in self.initialized_motors:
            result[str(motor)] = motor.get_values()
        return result


class I2CCommon():
    def __init__(self, rpi_revision):
        self.lock = threading.RLock()
        self.i2c = smbus.SMBus(rpi_revision)

    def write_byte_data(self, address, register, data):
        with self.lock:
            try:
                self.i2c.write_byte_data(address, register, data)
            except Exception, e:
                return e

    def read_byte_data(self, address, register):
        with self.lock:
            try:
                return self.read_byte_data(address, register)
            except Exception, e:
                return e