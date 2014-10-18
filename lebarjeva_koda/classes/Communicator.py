__author__ = 'delavnica'

import smbus
import time
import threading
import os

class Communicator(object):

    def __init__(self, bus_addr=1):
        self.address = bus_addr
        self.bus = smbus.SMBus(bus_addr)
        self.lock = threading.RLock()
    def write_byte_data(self, main_address, dir_address, value):
        with self.lock:
            self.bus.write_byte_data(main_address, dir_address, value)