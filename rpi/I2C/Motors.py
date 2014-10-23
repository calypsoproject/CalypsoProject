import smbus
import time
import atexit

__author__ = 'prog'

class Motors:
    system_is_enabled = False
    max_255_val = 65535

    enable_system_reg   = 0x01
    direction_reg       = 0x02
    speed_reg           = 0x03
    accel_hi_reg        = 0x04
    accel_lo_reg        = 0x05
    kp_idq_hi_reg       = 0x06
    kp_idq_lo_reg       = 0x07
    ki_idq_hi_reg       = 0x08
    ki_idq_lo_reg       = 0x09

    speed_est_hi_r_reg  = 0x11
    speed_est_lo_r_reg  = 0x12
    torque_hi_r_reg     = 0x13
    torque_lo_r_reg     = 0x14
    bus_voltage_r_reg   = 0x15


    motor_addresses = {
        'side_right': 0x09,
        'side_left': None,
        'mid_right': None,
        'mid_left': None,
        'main_right': None,
        'main_left': None
    }

    def __init__(self, motor_address, rpi_revision=1, acceleration=50, kp_idq=None, ki_idq=None):
        self.motor_address = motor_address
        self.acceleration = acceleration
        self.kp_idq = kp_idq
        self.ki_idq = ki_idq
        self.i2c = smbus.SMBus(rpi_revision)
        atexit.register(self.at_exit)

    def at_exit(self):
        self.disable_system()

    def init_motor(self):
        self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(self.acceleration)[0])
        self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(self.acceleration)[1])
        if self.kp_idq:
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.get_hi_lo_bytes(self.kp_idq)[0])
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.get_hi_lo_bytes(self.kp_idq)[1])
        if self.ki_idq:
            self.i2c.write_byte_data(self.motor_address, self.ki_idq_lo_reg, self.get_hi_lo_bytes(self.ki_idq)[0])
            self.i2c.write_byte_data(self.motor_address, self.ki_idq_hi_reg, self.get_hi_lo_bytes(self.ki_idq)[1])

    def get_motor_state(self):
        try:
            return self.i2c.read_byte_data(self.motor_addresses[motor], self.enable_system_reg)
        except IOError, e:
            print e


    def enable_system(self, motor=None):
        if motor:
            if self.get_motor_state(motor) == 1:
                print 'already enabled'
            self.i2c.write_byte_data(self.motor_addresses[motor], self.enable_system(), 1)
            time.sleep(8)
            return
        for key in self.motor_addresses.keys():
            if self.motor_addresses[key] is not None:
                if self.get_motor_state(key) == 1:
                    print 'already enabled'
                self.i2c.write_byte_data(self.motor_addresses[key], self.enable_system_reg, 1)
                time.sleep(8)
        self.init_motor()
        self.system_is_enabled = True

    def disable_system(self, motor=None):
        self.system_is_enabled = False
        if motor:
            self.i2c.write_byte_data(self.motor_addresses[motor], self.enable_system(), 0)
            return
        for key in self.motor_addresses.keys():
            if self.motor_addresses[key] is not None:
                self.i2c.write_byte_data(self.motor_addresses[key], self.enable_system_reg, 0)

    def change_accel(self, motor, accel):
        try:
            self.i2c.write_byte_data(self.motor_addresses[motor], self.accel_lo_reg, self.get_hi_lo_bytes(accel)[0])
            self.i2c.write_byte_data(self.motor_addresses[motor], self.accel_hi_reg, self.get_hi_lo_bytes(accel)[1])
        except IOError, e:
            print e

    def change_speed(self, motor, speed):
        try:
            self.i2c.write_byte_data(self.motor_addresses[motor], self.speed_reg, speed)
        except IOError, e:
            print e

    def change_direction(self, motor, direction):
        try:
            self.i2c.write_byte_data(self.motor_addresses[motor], self.direction_reg, direction)
        except IOError, e:
            print e


    def get_speed(self, motor, percent=False):
        try:
            hi = self.i2c.read_byte_data(self.motor_addresses[motor], self.speed_est_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_addresses[motor], self.speed_est_hi_r_reg)
            if percent:
                return (hi * 255 + lo) * (100 / self.max_255_val)
            return hi * 255 + lo
        except IOError, e:
            print e

    def get_torque(self, motor):
        try:
            hi = self.i2c.read_byte_data(self.motor_addresses[motor], self.torque_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_addresses[motor], self.torque_lo_r_reg)
            return hi * 255 + lo
        except IOError, e:
            print e

    def get_bus_voltage(self, motor):
        try:
            return self.i2c.read_byte_data(self.motor_addresses[motor], self.bus_voltage_r_reg)
        except IOError, e:
            print e

    def set_addresses(self, side_right, side_left, mid_right, mid_left, main_right, main_left):
        self.motor_addresses = {
            'side_right': side_right,
            'side_left': side_left,
            'mid_right': mid_right,
            'mid_left': mid_left,
            'main_right': main_right,
            'main_left': main_left
        }

    def get_hi_lo_bytes(self, val):
        acc = int(val * (self.max_255_val / 100))
        low = acc % 255
        high = (acc - low) / 255
        return [low, high]

if __name__ == '__main__':
    m = Motors(motor_address=0x09,
               rpi_revision=1,
               acceleration=40)
    m.enable_system()
    print 'enabled'
    m.change_speed(m.s, 40)
    raw_input()
    m.disable_system()