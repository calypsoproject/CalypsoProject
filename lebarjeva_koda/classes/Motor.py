__author__ = 'delavnica'

import threading
import math
import time


class Motor(object):
    minimal_speed = 10

    def __init__(self, main_addr, communicator, motor_name):

        self.enable_event = threading.Event()

        self.jumping_lock_event = threading.Event()
        self.jumping_lock_event.clear()


        self.speed_lock_event = threading.Event()
        self.speed_lock_event.set()
        self.speed_lock_interrupt_handler = False

        self.stop_lock_event = threading.Event()
        self.stop_lock_event.set()

        self.last_speed = 0
        self.changed_time = time.time()
        self.last_accl = 1

        self.motor_name = motor_name


        self.final_speed = 0

        self.curr_dir = 1

        self.rotor_accl = 512
        self.rotor_accl = 512
        self.max_rpm = 10000

        self.bus = communicator

        self.main_addr = main_addr
        self.speed_addr =0x03
        self.dir_addr = 0x02
        self.enable_addr = 0x01
        self.motor_accl_hi_addr = 0x04
        self.motor_accl_lo_addr = 0x05
        self.KP_idq_hi_addr = 0x06
        self.KP_idq_lo_addr = 0x07
        self.KI_idq_hi_addr = 0x08
        self.KI_idq_lo_addr = 0x09

        self.bus.write_byte_data(self.main_addr, self.dir_addr, 0x01)
        threading.Thread(target=self._enable_motor).start()

    def _enable_motor(self, timeout=7):
        self.bus.write_byte_data(self.main_addr, self.enable_addr, 0x01)
        time.sleep(timeout)
        self.enable_event.set()
        print("Motor available")

    def jump_start(self, speed=20):
        if not self.jumping_lock_event.isSet():
            t = threading.Thread(target=self._jump_start, args=(speed,))
            t.start()
            self.jumping_lock_event.set()

    def _jump_start(self, speed=10):
        self.stop_lock_event.wait()
        print("jumping")
        self.bus.write_byte_data(self.main_addr, self.speed_addr, 0x32)
        time.sleep(1)
        self.bus.write_byte_data(self.main_addr, self.KP_idq_hi_addr, 0x17)
        self.bus.write_byte_data(self.main_addr, self.KP_idq_lo_addr, 0x87)
        self.bus.write_byte_data(self.main_addr, self.speed_addr, 0x32)
        self.changed_time = time.time()
        self.last_speed = 1
        self.last_accl = 1
        time.sleep(0.6)

        self.bus.write_byte_data(self.main_addr, self.KP_idq_hi_addr, 0x02)
        self.bus.write_byte_data(self.main_addr, self.KP_idq_lo_addr, 0x84)
        self.bus.write_byte_data(self.main_addr, self.speed_addr, speed)
        self.final_speed = speed
        self.jumping_lock_event.clear()
        print("jumped")

    def _stop(self):
        self.last_speed = self.get_speed()
        self.changed_time = time.time()
        waiterThread = threading.Thread(target=self.__lock_waiter, args=(self.stop_lock_event, float(self.last_speed) * self.max_rpm / 100.0 / float(self.rotor_accl) + 0.6,))
        print("last speed", self.last_speed, self.get_speed())
        print("waiting for", float(self.get_speed()) * self.max_rpm / 100 / float(self.rotor_accl) + 0.6)
        self.stop_lock_event.clear()
        self.bus.write_byte_data(self.main_addr, self.speed_addr, 0x00)
        waiterThread.start()
        self.last_accl = -1
        self.final_speed = 0

    def stop(self):
        self.set_speed(0)

    def get_speed(self):  # Calculates achieved speed or set it to max set speed
        current_speed = self.last_speed + self.last_accl*self.rotor_accl*(time.time() - self.changed_time)/100
        #if "eft" in self.motor_name:
            #print("Last speed in calculations",self.last_speed);
            #print(self.motor_name, "delta v", self.last_accl*self.rotor_accl*(time.time() - self.changed_time)/100 , "in time:", time.time()-self.changed_time)
        if (current_speed - self.final_speed)*self.last_accl >= 0:
            self.changed_time = time.time()
            self.last_speed = self.final_speed
            return self.last_speed
        else:
            #print("not yet")
            return current_speed

    def __lock_waiter(self, lock_event, timeout, sleep_time=0.05): ## done
        print("stopping")
        start_time = time.time()
        end_time = start_time + timeout
        interrupt_handler_lock = threading.Lock()
        while time.time() < end_time :
            if time.time() + sleep_time >= end_time:
                time.sleep(end_time - time.time())
                break
            else:
                with interrupt_handler_lock:
                    temp_interrupt_handler = self.speed_lock_interrupt_handler
                if temp_interrupt_handler:  # speed changed during exec
                    lock_event.set()
                    return
                else:
                    time.sleep(sleep_time)
        lock_event.set()
        print("Stopped")

    def set_speed(self, speed=10, direction=1):
        self.enable_event.wait()
        self.get_speed()
        if not self.stop_lock_event.isSet():
            return
        if speed < 5:
            if self.last_speed:
                print(self.motor_name, "low speed, stopping")
                self._stop()
            return
        if direction not in (1, 2):
            raise TypeError("Direction not right, {0}".format(direction))
        elif not 0 <= speed <= 100:
            raise TypeError("Speed not right, {0}".format(speed))
        if speed < self.minimal_speed:
            speed = self.minimal_speed
        if self.last_speed == speed and direction == self.curr_dir:
            return
        self.final_speed = speed
        if self.final_speed < self.last_speed:
            self.last_accl = -1
        else:
            self.last_accl = 1
        print self.motor_name, self.last_speed, self.final_speed, self.last_accl
        if direction == self.curr_dir:
            if not self.last_speed:
                self.jump_start(speed)
            else:
                self.bus.write_byte_data(self.main_addr, self.speed_addr, speed)
        else:
            threading.Thread(target=self._reverse, args=(speed, direction,)).start()

    def _reverse(self, speed, direction):
        print("reversing")
        self._stop()
        self.stop_lock_event.wait()
        self.bus.write_byte_data(self.main_addr, self.dir_addr, direction)
        self.curr_dir = direction
        self.jump_start(speed)

    def __str__(self):
        return self.motor_name

    def __repr__(self):
        return self.motor_name
