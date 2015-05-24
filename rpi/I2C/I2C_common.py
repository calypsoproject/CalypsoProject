import threading
import smbus
import time


class I2CCommon():
    origin = 'main.py[Calypso]/I2CCommon'

    def __init__(self, rpi_revision, logger):
        self.logger = logger
        self.lock = threading.RLock()
        self.i2c = smbus.SMBus(rpi_revision)
        self.logger.info(self.origin+'/__init__', 'I2C common initialized')

    def write_byte_data(self, address, register, data):
        with self.lock:
            self.i2c.write_byte_data(address, register, abs(int(data)))

    def read_byte_data(self, address, register):
        with self.lock:
            val = self.i2c.read_byte_data(address, register)
            return val

    def read_word_data(self, address, register):
        with self.lock:
            val = self.i2c.read_word_data(address, register)
            return val

    def read_i2c_block_data(self, *args, **kwargs):
        with self.lock:
            val = self.i2c.read_i2c_block_data(*args, **kwargs)
            return val
