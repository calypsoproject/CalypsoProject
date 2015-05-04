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
    sc = modules.SpeedCalculator(ip)
    sender = modules.SpeedSender(ip)

    while 1:
        time.sleep(0.1)
        incline_correction = -sc.calculate_incline()*max_speed
        roll_correction = sc.calculate_roll()*max_speed

        roll_correction = roll_correction + min_speed if roll_correction > 0 else roll_correction
        roll_correction = roll_correction - min_speed if roll_correction < 0 else roll_correction
        incline_correction = incline_correction + min_speed if incline_correction > 0 else incline_correction
        incline_correction = incline_correction - min_speed if incline_correction < 0 else incline_correction

        fl = incline_correction + roll_correction
        fr = incline_correction + roll_correction
        br = -incline_correction - roll_correction
        bl = -incline_correction - roll_correction
        max_val = max([abs(fl), abs(fr), abs(br), abs(bl)])
        if max_val > max_speed:
            k = float(max_speed) / max_val
            fl *= k
            fr *= k
            bl *= k
            br *= k

        speeds['fl'] = fl
        speeds['fr'] = fr
        speeds['br'] = br
        speeds['bl'] = -bl
        speeds['ml'] = sc.joystick.right_left
        speeds['mr'] = -sc.joystick.right_left

        if sc.joystick.throttle != 0:
            kf_forward = 1/sc.joystick.throttle
        else:
            kf_forward = 1
        speed_diff = max_speed - min_speed

        if sc.joystick.throttle != 0:
            speeds['mr'] = (sc.joystick.throttle + speeds['mr'] / kf_forward if speeds['mr'] < speeds['ml'] else sc.joystick.throttle)*speed_diff
            speeds['ml'] = (sc.joystick.throttle + speeds['ml'] / kf_forward if speeds['mr'] > speeds['ml'] else sc.joystick.throttle)*speed_diff
        else:
            speeds['mr'] *= max_speed
            speeds['ml'] *= max_speed

        for k in speeds.keys():
            speeds[k] = round(speeds[k])
        for i in ['mr', 'ml']:
            if speeds[i] != 0:
                if speeds[i] > 0:
                    speeds[i] += min_speed
                if speeds[i] < 0:
                    speeds[i] -= min_speed
        speeds['ml'] = -speeds['ml']
        #print speeds
        sender.speeds = speeds

calculate_corrections()
