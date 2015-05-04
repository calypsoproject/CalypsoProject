class JoystickUpdater(object):
    def __init__(self):
        self.in_out = 0
        self.right_left = 0
        self.throttle = 0
        self.elevation = 0

    def update(self, in_out, right_left, throttle, elevation):
        self.in_out = in_out
        self.right_left = right_left
        self.throttle = throttle
        self.elevation = elevation