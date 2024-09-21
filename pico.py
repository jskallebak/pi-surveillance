from machine import Pin
from time import sleep

class Button:
    def __init__(self, name: string, button_pin: int, led_pin: int, output_pin: int):
        self.name = name
        
        self.led = Pin(led_pin, Pin.OUT)
        self.led_state = False
        self.led.value(self.led_state)
        
        self.button = Pin(button_pin, Pin.IN, Pin.PULL_UP)
        self.button_state_now = 1
        self.button_state_old = 1
        
        self.output = Pin(output_pin, Pin.OUT)
        self.output_state = False
        self.output.value(self.output_state)
        
    def check_press(self, debug: bool) -> None:
        self.button_state_now = self.button.value()
        if self.button_state_now == 0 and self.button_state_old == 1:
            self.led_state = not self.led_state
            self.led.value(self.led_state)
            
            self.output_state = not self.output_state
            self.output.value(self.output_state)
        if debug:
            print(self.name, self.led_state, self.button_state_now, self.output_state)
        self.button_state_old = self.button_state_now


but_yellow = Button('yellow', 14, 15, 0)
but_blue = Button('blue', 17, 16, 1)
but_red = Button('red', 11, 12, 2)
but_green = Button('green', 22, 20, 3)
debug = True

while True:
    but_yellow.check_press(debug)
    but_blue.check_press(debug)
    but_red.check_press(debug)
    but_green.check_press(debug)
    sleep(.1)
    