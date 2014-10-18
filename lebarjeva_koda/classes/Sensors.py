
from hmc5883l import hmc5883l
from adxl345 import ADXL345
from itg3200 import SensorITG3200
from Adafruit_BMP085 import BMP085
from Adafruit_I2C import Adafruit_I2C
import subprocess
import time
import threading


class dof9:
    def __init__(self, declination=(0, 0), gauss=4.7):
        self.compass = hmc5883l(gauss=gauss, declination=declination)
        self.accelerometer = ADXL345()
        self.gyroscope = SensorITG3200(1, 0x68)
        self.gyroscope.default_init()

    def get_compass(self):
        return self.compass.degrees(self.compass.heading())  # (degrees, minutes)

    def get_accelerometer(self):
        return self.accelerometer.getAxes(True)    # {'x':n, 'y':n, 'z':n}

    def get_gyroscope(self):
        #time.sleep(0.1)
        gx, gy, gz = self.gyroscope.read_data()
        return {'x': gx, 'y': gy, 'z': gz}    # {'x':n, 'y':n, 'z':n}

class Sensors():
    def __init__(self):
        self.bmp = BMP085(0x77)
        self.temp_sensors = ['28-000004d420c6', '28-000004d48494', '28-000004d4f30e']
        self.dof = dof9()
        self.temps = []
        self.retstr = "0|0"
        self.temp_thread = threading.Thread(target=self.read_temp_thread)
        self.temp_thread.start()
        self.thr = threading.Thread(target=self.main_thread)
        self.thr.start()

    def read_temp(self, device_file):
        device_file = '/sys/bus/w1/devices/'+device_file+'/w1_slave'
        temp_c = 0
        try:
            catdata = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = catdata.communicate()
            out_decode = out.decode('utf-8')
            lines = out_decode.split('\n')
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
            return temp_c
        except:
            pass

    def read_temp_all(self):
        return [str(self.read_temp(j)) for j in self.temp_sensors]

    def read_pressure(self):
        try:
            return self.bmp.readPressure()
        except:
            return 0

    def read_temp_thread(self):
        while 1:
            self.temps = self.read_temp_all()
            time.sleep(3)

    def main_thread(self):
        while 1:
            vals = [",".join(self.temps), str(self.read_pressure()),
                    ",".join(map(str, self.dof.get_gyroscope().values())),
                    ",".join(map(str, self.dof.get_accelerometer().values())),
                    ",".join(map(str, self.dof.get_compass()))]
            self.retstr = "|".join(vals)
            time.sleep(0.1)
