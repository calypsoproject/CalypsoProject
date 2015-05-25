import Adafruit_BBIO.GPIO as GPIO
import threading
import smbus
import time


class I2CCommon(object):
    origin = 'Calypso/I2CCommon'
    resetting = False

    def __init__(self, port, logger):
        self.port = port
        if port == 2:
            self.pin = 'P9_17'
        elif port == 1:
            self.pin = 'P9_19'
        self.logger = logger
        self.lock = threading.RLock()
        self.i2c = smbus.SMBus(port)
        self.logger.info(self.origin+'/__init__', 'I2C common initialized')

    def write_byte_data(self, address, register, data):
        with self.lock:
            try:
                self.i2c.write_byte_data(address, register, abs(int(data)))
            except:
                self.reset()
                self.i2c.write_byte_data(address, register, abs(int(data)))

    def read_byte_data(self, address, register):
        with self.lock:
            try:
                val = self.i2c.read_byte_data(address, register)
            except:
                self.reset()
                val = self.i2c.read_byte_data(address, register)
            return val

    def read_word_data(self, address, register):
        with self.lock:
            try:
                val = self.i2c.read_word_data(address, register)
            except:
                val = self.i2c.read_word_data(address, register)
            return val

    def read_i2c_block_data(self, *args, **kwargs):
        with self.lock:
            try:
                val = self.i2c.read_i2c_block_data(*args, **kwargs)
            except:
                val = self.i2c.read_i2c_block_data(*args, **kwargs)
            return val

    def reset(self):
        self.resetting = True
        try:
            with self.lock:
                self.i2c.close()
                GPIO.setup(self.pin, GPIO.OUT)
                for i in range(20):
                    GPIO.output(self.pin, GPIO.LOW)
                    time.sleep(1/20000.0)
                    GPIO.output(self.pin, GPIO.HIGH)
                    time.sleep(1/1000.0)
                self.i2c = smbus.SMBus(self.port)
        except:
            pass
        self.resetting = False
#