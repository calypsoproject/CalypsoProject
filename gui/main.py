import time
import modules

ip = '10.42.0.13'

joystick = modules.ReadJoystick()
joystick.initialize()
sender = modules.Sender(ip)
while 1:
    # order: in_out, right_left, throttle, elevation
    sender.joystick = [joystick.in_out,
                       joystick.right_left,
                       joystick.throttle,
                       joystick.elevation]
    sender.send()
    time.sleep(0.1)