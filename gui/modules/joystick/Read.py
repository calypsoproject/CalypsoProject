import pygame
import threading
import time

class ReadJoystick:
    selected_joystick = 0
    joystick_count = None
    joystick_names = None
    axes = None
    buttons = None
    hats = None
    right_left = 1
    in_out = 1
    throttle = 1
    elevation = 1
    def __init__(self, button_pressed_callback=None):
        self.button_pressed_callback = button_pressed_callback
        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        threading.Thread(target=self.main_loop).start()

    def initialize(self):
        while min(map(abs, self.axes[2:])) == 0: time.sleep(0.1)
        while round(max([abs(self.throttle), abs(self.elevation), abs(self.right_left), abs(self.in_out)]), 2) != 0: time.sleep(0.1)
        print 'joystick is initialized'

    def main_loop(self):
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION JOYBUTTONUP
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.button_pressed_callback:
                        self.button_pressed_callback(event)


            self.joystick_count = pygame.joystick.get_count()

            names = []
            for i in range(self.joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                names.append(joystick.get_name())
            self.joystick_names = names

            joystick = pygame.joystick.Joystick(self.selected_joystick)
            joystick.init()

            num_axes = joystick.get_numaxes()
            axes = []
            for i in range(num_axes):
                axes.append(joystick.get_axis(i))
            self.axes = axes

            num_buttons = joystick.get_numbuttons()
            buttons = []
            for i in range(num_buttons):
                buttons.append(joystick.get_button(i))
            self.buttons = buttons

            num_hats = joystick.get_numhats()
            hats = []
            for i in range(num_hats):
                hats.append(joystick.get_hat(i))
            self.hats = hats
            self.right_left = round(self.axes[0], 2)
            self.in_out = round(self.axes[1], 2)
            self.throttle = round(-(self.axes[2] - 1) / 2.0, 2)
            self.elevation = round(self.axes[4], 2)
            self.clock.tick(20)