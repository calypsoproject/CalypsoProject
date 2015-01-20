from accelerometer import ADXL345
from gyroscope import SensorITG3200
from compass import hmc5883l


class Sensors:
    def __init__(self, i2c_common, accelerometer_addr=0x53, gyroscope_addr=0x68, compass_addr=0x1E):
        self.i2c_common = i2c_common
        self.accelerometer_addr = accelerometer_addr
        self.gyroscope_addr = gyroscope_addr
        self.compass_addr = compass_addr

    def init_sensors(self):
        try: self.accelerometer = ADXL345(self.i2c_common, address=self.accelerometer_addr)
        except: self.accelerometer = None
        try: self.gyroscope = SensorITG3200(self.i2c_common, address=self.gyroscope_addr)
        except: self.gyroscope = None
        try: self.compass = hmc5883l(self.i2c_common, address=self.compass_addr)
        except: self.compass = None

        self.initialized_sensors = [self.accelerometer, self.compass, self.gyroscope]

    def get_values(self):
        return {str(sensor): sensor.read() for sensor in self.initialized_sensors if sensor}