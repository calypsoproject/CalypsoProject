import smbus
import threading
import time
import atexit

__author__ = 'prog'

class Motors:
    ## values if motor starts from 0 rpm
    jump_speed = 20
    jump_accel = 5
    jump_start_duration = 0.6
    start_kp_hi = 0x18
    start_kp_lo = 0x87

    ## I2C write registers
    enable_system_reg   = 0x01
    direction_reg       = 0x02
    speed_reg           = 0x03
    accel_hi_reg        = 0x04
    accel_lo_reg        = 0x05
    kp_idq_hi_reg       = 0x06
    kp_idq_lo_reg       = 0x07
    ki_idq_hi_reg       = 0x08
    ki_idq_lo_reg       = 0x09

    ## I2C read registers
    speed_est_hi_r_reg  = 0x11
    speed_est_lo_r_reg  = 0x12
    torque_hi_r_reg     = 0x13
    torque_lo_r_reg     = 0x14
    bus_voltage_r_reg   = 0x15

    ## other constants
    max_255_val = 65535
    normal_kp_hi = 0x02
    normal_kp_lo = 0x84
    minimal_speed = 10

    def __init__(self, motor_address, rpi_revision=1, acceleration=2):
        self.motor_address = motor_address
        self.acceleration = acceleration
        self.i2c = smbus.SMBus(rpi_revision)
        atexit.register(self.at_exit)
        self.system_is_enabled = self.get_motor_state()

    def at_exit(self):
        print 'exiting'
        self.disable_system()

    def init_motor(self):
        if not self.system_is_enabled:
            return False
        self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(self.acceleration)[0])
        self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(self.acceleration)[1])
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)

    def get_motor_state(self):
        try:
            return self.i2c.read_byte_data(self.motor_address, self.enable_system_reg)
        except IOError, e:
            print e


    def enable_system(self, block=False):
        if self.get_motor_state():
            self.disable_system()
            while self.get_motor_state():
                time.sleep(1)
                print self.get_motor_state()
            time.sleep(1)

        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 1)
        threading.Thread(target=self.system_enable_wait_thread).start()
        if block:
            time.sleep(8.5)

    def system_enable_wait_thread(self):
        time.sleep(8)
        self.system_is_enabled = True
        self.init_motor()

    def disable_system(self):
        if not self.get_motor_state():
            return False
        self.system_is_enabled = False
        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 0)

    def change_accel(self, accel, from_jump_start=False):
        if not self.system_is_enabled:
            return False

        try:
            self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(accel)[0])
            self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(accel)[1])
            if not from_jump_start:
                self.acceleration = accel
        except IOError, e:
            print e

    def change_speed(self, speed):
        if not self.system_is_enabled or speed < 0 or speed > 100:
            return False
        if speed < 10:
            speed = 0
        try:
            current_speed = self.get_speed()
            if current_speed < 10 < speed:
                threading.Thread(target=self.jump_start, args=[speed]).start()
            else:
                self.i2c.write_byte_data(self.motor_address, self.speed_reg, speed)
        except IOError, e:
            print e

    def jump_start(self, final_speed):
        print 'jump_start'
        self.change_accel(self.jump_accel, from_jump_start=True)
        self.system_is_enabled = False
        self.i2c.write_byte_data(self.motor_address, self.speed_reg, self.jump_speed)

        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.start_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.start_kp_hi)

        time.sleep(self.jump_start_duration)

        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)

        self.system_is_enabled = True
        self.change_accel(self.acceleration)
        self.i2c.write_byte_data(self.motor_address, self.speed_reg, final_speed)

    def change_direction(self, direction):
        if not self.system_is_enabled:
            return False

        try:
            self.change_speed(0)
            while self.get_speed() > 10:
                time.sleep(0.1)
            self.i2c.write_byte_data(self.motor_address, self.direction_reg, direction)
        except IOError, e:
            print e


    def get_speed(self):
        if not self.system_is_enabled:
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_lo_r_reg)
            return hi * 255 + lo
        except IOError, e:
            print e

    def get_torque(self):
        if not self.system_is_enabled:
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.torque_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.torque_lo_r_reg)
            return hi * 255 + lo
        except IOError, e:
            print e

    def get_bus_voltage(self):
        if not self.system_is_enabled:
            return False

        try:
            return self.i2c.read_byte_data(self.motor_address, self.bus_voltage_r_reg)
        except IOError, e:
            print e

    def get_direction(self):
        if not self.system_is_enabled:
            return False

        try:
            return self.i2c.read_byte_data(self.motor_address, self.direction_reg)
        except IOError, e:
            print e


    def get_hi_lo_bytes(self, val):
        acc = int(val * (self.max_255_val / 100))
        low = acc % 255
        high = (acc - low) / 255
        return [low, high]

    def print_reg_values(self, delay=1):
        while 1:
            print self.get_torque(), self.get_speed(), self.get_bus_voltage(), self.get_motor_state()
            time.sleep(delay)

if __name__ == '__main__':
    m = Motors(motor_address=0x07,
               rpi_revision=1)
    m.enable_system(block=True)
    m.change_speed(15)
    raw_input('asdf')
    m.disable_system()