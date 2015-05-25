from GUI import app
from I2C.I2C_common import I2CCommon
from server import Server
from I2C.Sensors import Sensors
from I2C.MotorsHandler import MotorsHandler
from PID.Position import Position
from PID.SpeedCalculator import SpeedCalculator
from PID.JoystickUpdater import JoystickUpdater
from logger import Logger

class Calypso:
    def __init__(self):
        self.logger = Logger()
        self.server = Server(calypso_instance=self,
                             listen_port=8888,
                             logger=self.logger)

        i2c_common = I2CCommon(1, self.logger)
        self.i2c = i2c_common

        ## motors initialization
        self.motor_handler = MotorsHandler(i2c_common, self.logger)
        self.forward_left_motor = self.motor_handler.new_motor(motor_address=0x05,
                                                               motor_name='bl')
        self.forward_right_motor = self.motor_handler.new_motor(motor_address=0x06,
                                                                motor_name='br')
        self.side_right_motor = self.motor_handler.new_motor(motor_address=0x10,
                                                             motor_name='ml')
        self.side_left_motor = self.motor_handler.new_motor(motor_address=0x08,
                                                            motor_name='mr')
        self.middle_right_motor = self.motor_handler.new_motor(motor_address=0x07,
                                                               motor_name='fl')
        self.middle_left_motor = self.motor_handler.new_motor(motor_address=0x09,
                                                              motor_name='fr')

        self.position = Position()
        self.joystick = JoystickUpdater()
        self.sensors = Sensors(I2CCommon(2, self.logger))
        self.sensors.init_sensors()
        self.sensors.update_position(self.position)
        self.speed_calculator = SpeedCalculator(self.position, self.joystick, self.motor_handler, self.logger)
        self.pid = self.speed_calculator.pid

    def get_gui(self):
        motor_speeds = self.motor_handler.get_speeds()
        position = {'yaw': self.position.yaw_smooth,
                    'roll': -self.position.roll_smooth,
                    'pitch': self.position.pitch_smooth}
        return {'motors': motor_speeds,
                'position': position,
                'log': self.logger.get_log()}

if __name__ == '__main__':
    calypso = Calypso()
    app.config['calypso'] = calypso
    app.run(calypso.server.hostname, 8000)
