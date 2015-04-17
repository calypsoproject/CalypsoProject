import pygame
import threading


class ReadJoystick:
    selected_joystick = 0
    joystick_count = None
    joystick_names = None
    axes = None
    buttons = None
    hats = None
    def __init__(self, button_pressed_callback=None):
        self.button_pressed_callback = button_pressed_callback
        pygame.init()
        self.clock = pygame.time.Clock()
        pygame.joystick.init()
        threading.Thread(target=self.main_loop).start()

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
            self.clock.tick(20)