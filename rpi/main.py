import threading
import time
from GUI import app
from I2C.I2C_common import I2CCommon
from server import Server
from I2C.Sensors import Sensors
from I2C.MotorsHandler import MotorsHandler

class Calypso:
    def __init__(self):
        self.server = Server(calypso_instance=self,
                             listen_port=8888)

        i2c_common = I2CCommon(rpi_revision=1)

        ## motors initialization
        self.motor_handler = MotorsHandler(i2c_common)
        self.forward_left_motor = self.motor_handler.new_motor(motor_address=0x05,
                                                               motor_name='ml')
        self.forward_right_motor = self.motor_handler.new_motor(motor_address=0x06,
                                                                motor_name='fr')
        self.side_right_motor = self.motor_handler.new_motor(motor_address=0x07,
                                                             motor_name='fl')
        self.side_left_motor = self.motor_handler.new_motor(motor_address=0x08,
                                                            motor_name='bl')
        self.middle_right_motor = self.motor_handler.new_motor(motor_address=0x09,
                                                               motor_name='br')
        self.middle_left_motor = self.motor_handler.new_motor(motor_address=0x10,
                                                              motor_name='mr')

        self.sensors = Sensors(i2c_common)

    def a(self):
        while 1:
            print self.forward_left_motor.get_motor_state()

if __name__ == '__main__':
    calypso = Calypso()
    app.config['calypso'] = calypso
    app.run(calypso.server.hostname, 80)