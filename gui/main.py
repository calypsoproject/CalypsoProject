import time
import modules

ip = '10.42.0.13'

max_speed = 50
min_speed = 10



speeds = {
    'fl': 0,
    'fr': 0,
    'bl': 0,
    'br': 0,
    'ml': 0,
    'mr': 0
}
def calculate_corrections():
    p = modules.Position()
    p.start_retrieving_data(ip)
    while 1:
        print p.get_angles()
        time.sleep(0.1)
    sc = modules.SpeedCalculator(ip)
    while 1:
        print sc.calculate_incline()
        print sc.calculate_roll()

    sender = modules.SpeedSender(ip)

    while 1:
        time.sleep(0.5)
        incline_correction = sc.calculate_incline()*max_speed
        roll_correction = sc.calculate_roll()*max_speed
        incline_correction = incline_correction + min_speed if incline_correction != 0 else 0
        roll_correction = roll_correction + min_speed if roll_correction != 0 else 0

        print 'incline:', incline_correction, 'roll:', roll_correction
        fl = incline_correction + roll_correction
        fr = incline_correction + roll_correction
        br = -incline_correction - roll_correction
        bl = -incline_correction - roll_correction
        print incline_correction, roll_correction, raw_input()
        speeds['fl'] = fl if abs(fl) < max_speed else max_speed
        speeds['fr'] = fr if fr < max_speed else max_speed
        speeds['br'] = br if br < max_speed else max_speed
        speeds['bl'] = bl if bl < max_speed else max_speed
        speeds['ml'] = sc.joystick.right_left
        speeds['mr'] = -sc.joystick.right_left

        if sc.joystick.throttle != 0:
            kf_forward = 1/sc.joystick.throttle
        else:
            kf_forward = 1
        speed_diff = max_speed - min_speed
        speeds['mr'] = (sc.joystick.throttle + speeds['mr'] / kf_forward if speeds['mr'] < speeds['ml'] else sc.joystick.throttle)*speed_diff
        speeds['ml'] = (sc.joystick.throttle + speeds['ml'] / kf_forward if speeds['mr'] > speeds['ml'] else sc.joystick.throttle)*speed_diff
        for k in speeds.keys():
            speeds[k] = round(speeds[k])
        for i in ['mr', 'ml']:
            if speeds[i] != 0:
                if speeds[i] > 0:
                    speeds[i] += min_speed
                if speeds[i] < 0:
                    speeds[i] -= min_speed

        print speeds

calculate_corrections()
