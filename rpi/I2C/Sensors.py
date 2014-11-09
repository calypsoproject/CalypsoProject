from accelerometer import adxl345
from gyroscope import SensorITG3200
from compass import hmc5883l


class Sensors:
    def __init__(self, i2c_common, accelerometer_addr=0x00, gyroscope_addr=0x00, compass_addr=0x00):
        self.accelerometer = adxl345(i2c_common, address=accelerometer_addr)
        self.gyroscope = SensorITG3200(i2c_common, address=gyroscope_addr)
        self.compass = hmc5883l(i2c_common, address=compass_addr)

        self.initialized_sensors = [self.accelerometer, self.compass, self.gyroscope]

    def get_values(self):
        return {str(sensor): sensor.read() for sensor in self.initialized_sensors}