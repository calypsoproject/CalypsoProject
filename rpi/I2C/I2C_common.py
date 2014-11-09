import threading
import smbus


class I2CCommon():
    def __init__(self, rpi_revision):
        self.lock = threading.RLock()
        self.i2c = smbus.SMBus(rpi_revision)

    def write_byte_data(self, address, register, data):
        with self.lock:
            self.i2c.write_byte_data(address, register, data)

    def read_byte_data(self, address, register):
        with self.lock:
            return self.read_byte_data(address, register)