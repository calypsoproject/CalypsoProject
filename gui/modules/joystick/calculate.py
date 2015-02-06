import time
from read import ReadJoystick

class Calculate:
    def __init__(self):
        self.joystick = ReadJoystick()
        self.calculate()

    def calculate(self):
        while 1:
            print self.joystick.buttons, self.joystick.axes, self.joystick.hats
            time.sleep(0.2)

if __name__ == '__main__':
    Calculate()