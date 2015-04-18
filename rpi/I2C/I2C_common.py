import threading
import smbus
import time


class I2CCommon():
    def __init__(self, rpi_revision):
        self.lock = threading.RLock()
        self.i2c = smbus.SMBus(rpi_revision)

    def write_byte_data(self, address, register, data):
        with self.lock:
            try:
                self.i2c.write_byte_data(address, register, abs(int(data)))
            except:
                print 'i2c error'

    def read_byte_data(self, address, register):
        with self.lock:
            try:
                val = self.i2c.read_byte_data(address, register)
                return val
            except:
                print 'i2c error'

    def read_word_data(self, address, register):
        with self.lock:
            try:
                val = self.i2c.read_word_data(address, register)
                return val
            except:
                print 'i2c error'

    def read_i2c_block_data(self, *args, **kwargs):
        with self.lock:
            try:
                val = self.i2c.read_i2c_block_data(*args, **kwargs)
                return val
            except:
                print 'i2c error'