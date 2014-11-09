from GUI import app
from I2C.I2C_common import I2CCommon
from server import Server
from I2C.Sensors import Sensors
from I2C.MotorsHandler import MotorsHandler

class Calypso:
    def __init__(self):
        self.server = Server(self.command_from_server,
                             listen_port=8888)

        i2c_common = I2CCommon(rpi_revision=1)

        ## motors initialization
        self.motor_handler = MotorsHandler(i2c_common)
        self.forward_left_motor = self.motor_handler.new_motor(motor_address=0x01,
                                                               motor_name='forward left')
        self.forward_right_motor = self.motor_handler.new_motor(motor_address=0x02,
                                                                motor_name='forward right')
        self.side_right_motor = self.motor_handler.new_motor(motor_address=0x03,
                                                             motor_name='side right')
        self.side_left_motor = self.motor_handler.new_motor(motor_address=0x04,
                                                            motor_name='side left')
        self.middle_right_motor = self.motor_handler.new_motor(motor_address=0x05,
                                                               motor_name='middle right')
        self.middle_left_motor = self.motor_handler.new_motor(motor_address=0x06,
                                                              motor_name='middle left')

        self.sensors = Sensors(i2c_common)

    def command_from_server(self, command, clientsocket):
        """ executes command, recieved from server and returns result
        """
        try:
            result = None
            exec command
            return result
        except Exception, e:
            return e

if __name__ == '__main__':
    calypso = Calypso()
    app.config['calypso'] = calypso
    app.run(calypso.server.hostname, 80)