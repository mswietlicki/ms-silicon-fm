from machine import Pin
from neopixel import NeoPixel

class RatioState():
    IDLE = "idle"
    TRANSMITTING = "transmitting"
    RECEIVING = "receiving"
    ERROR = "error"

    def __init__(self):
        self.state = self.IDLE
        self.state_led = NeoPixel(Pin(16, Pin.OUT), 1)
        self.show()

    def set_state(self, state):
        self.state = state
        self.show()

    def get_state(self):
        return self.state
    
    def show(self):
        if self.state == RatioState.IDLE:
            self.state_led[0] = (10, 0, 0) # green  # type: ignore
        elif self.state == RatioState.TRANSMITTING:
            self.state_led[0] = (0, 20, 20)  # type: ignore
        elif self.state == RatioState.RECEIVING:
            self.state_led[0] = (0, 0, 50)  # type: ignore
        elif self.state == RatioState.ERROR:
            self.state_led[0] = (0, 50, 0)  # type: ignore
        else:
            self.state_led[0] = (0, 0, 0) # type: ignore
        self.state_led.write()