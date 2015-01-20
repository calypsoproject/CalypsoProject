import threading
import time
import atexit

__author__ = 'prog'

class Motor:
    ## values if motor starts from 0 rpm
    jump_speed = 10
    jump_accel = 10
    jump_start_duration = 1
    start_kp_hi = 0x0B
    start_kp_lo = 0xC3

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
    normal_kp_lo = 0xB4
    normal_ki_hi = 0x0E
    normal_ki_lo = 0x64
    minimal_speed = 10
    enable_timeout = 8
    lock_all_operations = False
    speed = 0

    def __init__(self, motor_address, i2c_common, motor_name, acceleration, kp_hi=None, kp_lo=None, jump_start_enabled=True):
        self.jump_start_enabled = jump_start_enabled
        if kp_hi and kp_lo:
            self.normal_kp_hi = kp_hi
            self.normal_kp_lo = kp_lo
        self.motor_address = motor_address
        self.acceleration = acceleration
        self.i2c = i2c_common
        atexit.register(self.at_exit)
        self.motor_name = motor_name

    def at_exit(self):
        print 'exiting:', self.motor_name
        self.disable_system()

    def init_motor(self):
        if not self.get_motor_state():
            return False
        self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(self.acceleration)[0])
        self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(self.acceleration)[1])
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)
        self.i2c.write_byte_data(self.motor_address, self.ki_idq_lo_reg, self.normal_ki_lo)
        self.i2c.write_byte_data(self.motor_address, self.ki_idq_hi_reg, self.normal_ki_hi)

    def get_motor_state(self):
        if self.lock_all_operations:
            print 'all operations are locked!'
            return None
        try:
            return self.i2c.read_byte_data(self.motor_address, self.enable_system_reg)
        except Exception, e:
            print e
            return None


    def enable_system(self, block=False):
        state = self.get_motor_state()
        if state:
            self.disable_system()
            while self.get_motor_state():
                time.sleep(1)
                print self.get_motor_state()
            time.sleep(1)
        elif state is None:
            return False
        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 1)
        threading.Thread(target=self.system_enable_wait_thread).start()
        if block:
            time.sleep(self.enable_timeout)

    def system_enable_wait_thread(self):
        self.lock_all_operations = True
        time.sleep(self.enable_timeout - 0.1)
        self.lock_all_operations = False
        self.init_motor()

    def disable_system(self):
        if not self.get_motor_state():
            return False
        self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 0)

    def set_accel(self, accel, from_jump_start=False):
        """ accel ... 0 - 100 (float / int)
        """
        if not self.get_motor_state():
            return False

        self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(accel)[0])
        self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(accel)[1])
        if not from_jump_start:
            self.acceleration = accel

    def set_speed(self, speed):
        """ speed ... 0 - 100 (float / int)
        """
        if not self.get_motor_state() or speed < 0 or speed > 100:
            return False
        if speed < self.minimal_speed:
            speed = 0
        current_speed = self.get_speed()
        if current_speed < self.minimal_speed and speed and self.jump_start_enabled:
            threading.Thread(target=self.jump_start, args=[speed]).start()
        else:
            self.i2c.write_byte_data(self.motor_address, self.speed_reg, speed)

    def jump_start(self, final_speed, repeat=True):
        print 'jump_start'
        self.set_accel(self.jump_accel, from_jump_start=True)

        self.lock_all_operations = True
        self.i2c.write_byte_data(self.motor_address, self.speed_reg, self.jump_speed)

        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.start_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.start_kp_hi)

        start = time.time()
        speed = 0
        while time.time() - start < self.jump_start_duration and speed == 0:
            hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_lo_r_reg)
            speed = hi * 255 + lo
            time.sleep(0.05)

        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)

        self.i2c.write_byte_data(self.motor_address, self.speed_reg, final_speed)
        self.lock_all_operations = False

        self.set_accel(self.acceleration)

        if speed == 0 and repeat:
            time.sleep(0.5)
            print 'jump_start failed. repeating...'
            self.jump_start(speed, repeat=False)

    def set_direction(self, direction):
        """ direction ... 1 / 0 (int)
        """
        if not self.get_motor_state():
            return False

        current_speed = self.get_speed(percent=True)
        self.set_speed(0)
        while self.get_speed():
            time.sleep(0.1)
        time.sleep(0.1)
        print current_speed, self.get_speed(percent=True), self.get_speed(percent_estimated=True)
        self.i2c.write_byte_data(self.motor_address, self.direction_reg, direction)
        self.set_speed(current_speed)


    def get_speed(self, percent=False, percent_estimated=False):
        """ returns value in rpm or in percent
        """
        if not self.get_motor_state():
            return False

        if percent:
            return self.i2c.read_byte_data(self.motor_address, self.speed_reg)

        hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
        lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_lo_r_reg)

        if percent_estimated:
            return self.get_percent_from_bytes(hi, lo)

        return hi * 255 + lo

    def get_torque(self):
        if not self.get_motor_state():
            return False

        hi = self.i2c.read_byte_data(self.motor_address, self.torque_hi_r_reg)
        lo = self.i2c.read_byte_data(self.motor_address, self.torque_lo_r_reg)
        return hi * 255 + lo

    def get_bus_voltage(self):
        if not self.get_motor_state():
            return False

        return self.i2c.read_byte_data(self.motor_address, self.bus_voltage_r_reg)

    def get_direction(self):
        if not self.get_motor_state():
            return False

        return self.i2c.read_byte_data(self.motor_address, self.direction_reg)

    def get_accel(self, percent=True):
        if not self.get_motor_state():
            return False

        hi = self.i2c.read_byte_data(self.motor_address, self.accel_hi_reg)
        lo = self.i2c.read_byte_data(self.motor_address, self.accel_lo_reg)
        if percent:
            return self.get_percent_from_bytes(hi, lo)
        else:
            return hi * 255 + lo

    def get_kp(self):
        if not self.get_motor_state():
            return False

        hi = self.i2c.read_byte_data(self.motor_address, self.kp_idq_hi_reg)
        lo = self.i2c.read_byte_data(self.motor_address, self.kp_idq_lo_reg)
        return hi * 255 + lo

    def set_kp(self, kp):
        """ accel ... 0 - 100 (float / int)
        """
        if not self.get_motor_state():
            return False

        self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.get_hi_lo_bytes(kp)[0])
        self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.get_hi_lo_bytes(kp)[1])

    def get_ki(self):
        if not self.get_motor_state():
            return False

        hi = self.i2c.read_byte_data(self.motor_address, self.ki_idq_hi_reg)
        lo = self.i2c.read_byte_data(self.motor_address, self.ki_idq_lo_reg)
        return hi * 255 + lo

    def get_hi_lo_bytes(self, val):
        acc = int(val * (self.max_255_val / 100.0))
        low = acc % 255
        high = (acc - low) / 255
        return [low, high]

    def get_percent_from_bytes(self, high, low, n_digits=5):
        val = high * 255 + low
        return round(val / (self.max_255_val / 100.0), n_digits)

    def get_values(self):
        return {'speed': self.get_speed(),
                'torque': self.get_torque(),
                'accel': self.get_accel(),
                'kp': self.get_kp(),
                'ki': self.get_ki(),
                'enabled': self.get_motor_state(),
                'locked': self.lock_all_operations,
                'voltage': self.get_bus_voltage(),
                'direction': self.get_direction()}

    def __str__(self):
        return self.motor_name
