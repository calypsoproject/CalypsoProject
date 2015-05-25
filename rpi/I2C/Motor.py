import threading
import time
import atexit
import sys

__author__ = 'prog'


class Motor:
    ## values if motor starts from 0 rpm
    jump_speed = 20
    jump_accel = 10
    jump_start_duration = 0.2
    start_kp_hi = 0x0B
    start_kp_lo = 0xD7

    ## I2C write registers
    enable_system_reg = 0x01
    direction_reg = 0x02
    speed_reg = 0x03
    accel_hi_reg = 0x04
    accel_lo_reg = 0x05
    kp_idq_hi_reg = 0x06
    kp_idq_lo_reg = 0x07
    ki_idq_hi_reg = 0x08
    ki_idq_lo_reg = 0x09

    ## I2C read registers
    speed_est_hi_r_reg = 0x11
    speed_est_lo_r_reg = 0x12
    torque_hi_r_reg = 0x13
    torque_lo_r_reg = 0x14
    bus_voltage_r_reg = 0x15

    ## other constants
    max_255_val = 65535
    normal_kp_hi = 0x02
    normal_kp_lo = 0xB4
    normal_ki_hi = 0x09
    normal_ki_lo = 0x41
    minimal_speed = 4
    enable_timeout = 8
    lock_all_operations = False
    speed = 0
    last_speed = 0
    current_direction = 0

    def __init__(self, motor_address, i2c_common, motor_name, acceleration, logger, kp_hi=None, kp_lo=None,
                 jump_start_enabled=True):
        self.logger = logger
        self.origin = 'Calypso/Motor/'+motor_name
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
        self.disable_system()
        self.logger.info(self.origin+'/at_exit', 'exiting')
        sys.stdout.flush()

    def init_motor(self):
        if not self.get_motor_state():
            return False
        try:
            self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(self.acceleration)[0])
            self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(self.acceleration)[1])
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)
            self.i2c.write_byte_data(self.motor_address, self.ki_idq_lo_reg, self.normal_ki_lo)
            self.i2c.write_byte_data(self.motor_address, self.ki_idq_hi_reg, self.normal_ki_hi)
            self.set_direction(self.current_direction)
        except Exception, e:
            print self.motor_name, 'init_motor', e

    def get_motor_state(self):
        if self.lock_all_operations or self.i2c.resetting:
            return None
        try:
            return self.i2c.read_byte_data(self.motor_address, self.enable_system_reg)
        except IOError:
            print 'motor %s is disconnected' % self.motor_name
            return False
        except Exception, e:
            print self.motor_name, 'get_motor_state', e
            return None

    def enable_system(self, block=False):
        state = self.get_motor_state()
        if state:
            self.disable_system()
            while self.get_motor_state():
                time.sleep(1)
            time.sleep(1)
        elif state is None:
            return False
        try:
            self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 1)
        except Exception, e:
            print self.motor_name, 'enable_system', e
            return
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
        try:
            self.i2c.write_byte_data(self.motor_address, self.enable_system_reg, 0)
        except Exception, e:
            print self.motor_name, 'disable_system', e

    def set_accel(self, accel, from_jump_start=False):
        """ accel ... 0 - 100 (float / int)
        """
        if not self.get_motor_state():
            return False

        try:
            self.i2c.write_byte_data(self.motor_address, self.accel_lo_reg, self.get_hi_lo_bytes(accel)[0])
            self.i2c.write_byte_data(self.motor_address, self.accel_hi_reg, self.get_hi_lo_bytes(accel)[1])
        except Exception, e:
            print self.motor_name, 'set_accel', e

        if not from_jump_start:
            self.acceleration = accel

    def set_speed(self, speed):
        """ speed ... 0 - 100 (float / int)
        """
        if not self.get_motor_state() or speed < -100 or speed > 100:
            return False

        if speed < 0 and self.current_direction == 0:
            self.current_direction = 1
            self.set_direction(1, end_speed=speed)
            return

        elif speed > 0 and self.current_direction == 1:
            self.current_direction = 0
            self.set_direction(0, end_speed=speed)
            return

        if abs(speed) < self.minimal_speed:
            speed = 0
        current_speed = self.get_speed(percent=True)
        if current_speed < self.minimal_speed and speed and self.jump_start_enabled:
            threading.Thread(target=self.jump_start, args=[speed]).start()
        else:
            try:
                self.i2c.write_byte_data(self.motor_address, self.speed_reg, speed)
            except Exception, e:
                print self.motor_name, 'set_speed', e
            self.last_speed = speed if self.current_direction == 1 else speed * -1
            self.logger.info(self.origin+'/set_speed', 'reached '+str(speed))

    def jump_start(self, final_speed, repeat=0):
        self.set_accel(self.jump_accel, from_jump_start=True)

        self.lock_all_operations = True
        try:
            self.i2c.write_byte_data(self.motor_address, self.speed_reg, self.jump_speed)

            self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.start_kp_lo)
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.start_kp_hi)

            time.sleep(self.jump_start_duration)

            self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)

            self.i2c.write_byte_data(self.motor_address, self.speed_reg, final_speed)
            self.lock_all_operations = False

            self.set_accel(self.acceleration)

            time.sleep(0.1)
            hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_lo_r_reg)
        except Exception, e:
            print self.motor_name, 'jump_start', e
            while 1:
                try:
                    self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.normal_kp_lo)
                    self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.normal_kp_hi)

                    self.i2c.write_byte_data(self.motor_address, self.speed_reg, final_speed)
                    self.lock_all_operations = False

                    self.set_accel(self.acceleration)
                    break
                except Exception, e:
                    print self.motor_name, 'jump_start > disabling from exception', e
            return

        try:
            speed = hi * 255 + lo
        except:
            speed = 0
        if speed == 0 and repeat < 5:
            repeat += 1
            self.jump_start(final_speed, repeat)
            return
        elif speed == 0:
            self.logger.info(self.origin+'/jump_start', 'failed to start')
        else:
            self.logger.verbose(self.origin+'/jump_start', 'reached '+str(speed))

    def set_direction(self, direction, end_speed=None):
        """ direction ... 1 / 0 (int)
        """
        if not self.get_motor_state():
            return False

        current_speed = self.get_speed(percent=True)
        self.set_speed(0)
        while self.get_speed(): pass
        try:
            self.i2c.write_byte_data(self.motor_address, self.direction_reg, direction)
        except Exception, e:
            print self.motor_name, 'set_direction', e
            return
        if end_speed is not None:
            current_speed = end_speed
        self.set_speed(current_speed)

    def get_speed(self, percent=False, percent_estimated=False):
        """ returns value in rpm or in percent
        """
        if not self.get_motor_state():
            return False

        try:
            if percent:
                return self.i2c.read_byte_data(self.motor_address, self.speed_reg)

            hi = self.i2c.read_byte_data(self.motor_address, self.speed_est_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.speed_est_lo_r_reg)
        except Exception, e:
            print self.motor_name, 'get_speed', e
            return 0

        if percent_estimated:
            return self.get_percent_from_bytes(hi, lo)

        return hi * 255 + lo

    def get_torque(self):
        if not self.get_motor_state():
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.torque_hi_r_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.torque_lo_r_reg)
        except Exception, e:
            print self.motor_name, 'get_torque', e
            return 0

        return hi * 255 + lo

    def get_bus_voltage(self):
        if not self.get_motor_state():
            return False

        try:
            return self.i2c.read_byte_data(self.motor_address, self.bus_voltage_r_reg)
        except Exception, e:
            print self.motor_name, 'get_bus_voltage', e
            return 0

    def get_direction(self):
        if not self.get_motor_state():
            return False

        try:
            return self.i2c.read_byte_data(self.motor_address, self.direction_reg)
        except Exception, e:
            print self.motor_name, 'get_direction', e
            return self.current_direction

    def get_accel(self, percent=True):
        if not self.get_motor_state():
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.accel_hi_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.accel_lo_reg)
        except Exception, e:
            print self.motor_name, 'get_accel', e
            return self.acceleration

        if percent:
            return self.get_percent_from_bytes(hi, lo)
        else:
            return hi * 255 + lo

    def get_kp(self):
        if not self.get_motor_state():
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.kp_idq_hi_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.kp_idq_lo_reg)
        except Exception, e:
            print self.motor_name, 'get_kp', e
            return self.normal_kp_hi * 255 + self.normal_kp_lo
        return hi * 255 + lo

    def set_kp(self, kp):
        """ accel ... 0 - 100 (float / int)
        """
        if not self.get_motor_state():
            return False

        try:
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_lo_reg, self.get_hi_lo_bytes(kp)[0])
            self.i2c.write_byte_data(self.motor_address, self.kp_idq_hi_reg, self.get_hi_lo_bytes(kp)[1])
        except Exception, e:
            print self.motor_name, 'set_kp', e

    def get_ki(self):
        if not self.get_motor_state():
            return False

        try:
            hi = self.i2c.read_byte_data(self.motor_address, self.ki_idq_hi_reg)
            lo = self.i2c.read_byte_data(self.motor_address, self.ki_idq_lo_reg)
        except Exception, e:
            print self.motor_name, 'get_ki', e
            return self.normal_ki_hi * 255 + self.normal_ki_lo
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
