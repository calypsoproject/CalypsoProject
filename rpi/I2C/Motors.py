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

    def __init__(self, motor_address, rpi_revision=1, acceleration=50, kp_idq=None, ki_idq=None):
        self.motor_address = motor_address
        self.acceleration = acceleration
        self.kp_idq = kp_idq
        self.ki_idq = ki_idq
        self.i2c = smbus.SMBus(rpi_revision)
        atexit.register(self.at_exit)

    def at_exit(self):
        print 'exiting'
        self.disable_system()

    def init_motor(self):
        if self.system_is_enabled:
            self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(self.acceleration)[0])
            self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(self.acceleration)[1])
            if self.kp_idq:
                self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.get_hi_lo_bytes(self.kp_idq)[0])
                self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.get_hi_lo_bytes(self.kp_idq)[1])
            if self.ki_idq:
                self.i2c.write_byte_data(self.motor_address, self.ki_idq_lo_reg, self.get_hi_lo_bytes(self.ki_idq)[0])
                self.i2c.write_byte_data(self.motor_address, self.ki_idq_hi_reg, self.get_hi_lo_bytes(self.ki_idq)[1])
        else:
            print 'enable system first'

    def get_motor_state(self):
        try:
            return self.i2c.read_byte_data(self.motor_address, self.enable_system_reg)
        except IOError, e:
            print e


    def enable_system(self):
        if self.get_motor_state() == 1:
            print 'already enabled'
        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 1)
        time.sleep(8)
        self.init_motor()
        self.system_is_enabled = True

    def disable_system(self):
        self.system_is_enabled = False
        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 0)

    def change_accel(self, accel):
        try:
            if self.system_is_enabled:
                self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(accel)[0])
                self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(accel)[1])
            else:
                print 'enable system first'
        except IOError, e:
            print e

    def change_speed(self, speed):
        try:
            if self.system_is_enabled:
                self.i2c.write_byte_data(self.motor_address, self.speed_reg, speed)
            else:
                print 'enable system first'
        except IOError, e:
            print e

    def change_direction(self, direction):
        try:
            if self.system_is_enabled:
                self.i2c.write_byte_data(self.motor_address, self.direction_reg, direction)
            else:
                print 'enable system first'
        except IOError, e:
            print e


    def get_speed(self, percent=False):
        try:
            if self.system_is_enabled:
                hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
                lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
                if percent:
                    return (hi * 255 + lo) * (100 / self.max_255_val)
                return hi * 255 + lo
            else:
                print 'enable system first'
        except IOError, e:
            print e

    def get_torque(self):
        try:
            if self.system_is_enabled:
                hi = self.i2c.read_byte_data(self.motor_address, self.torque_hi_r_reg)
                lo = self.i2c.read_byte_data(self.motor_address, self.torque_lo_r_reg)
                return hi * 255 + lo
            else:
                print 'enable system first'
        except IOError, e:
            print e

    def get_bus_voltage(self):
        try:
            if self.system_is_enabled:
                return self.i2c.read_byte_data(self.motor_address, self.bus_voltage_r_reg)
            else:
                print 'enable system first'
        except IOError, e:
            print e

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
    m.change_speed(10)
    while 1:
        print m.get_speed(), m.get_torque()
        time.sleep(0.5)