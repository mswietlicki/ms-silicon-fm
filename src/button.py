from machine import Pin
import time
import micropython

class Button():
    def __init__(self, pin_number, long_click_duration_ms=500):
        self.pin_number = pin_number
        self.long_click_duration_ms = long_click_duration_ms
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self._on_down_handler = None
        self._on_up_handler = None
        self._on_short_click_handler = None
        self._on_long_click_handler = None
        self._down_time = 0
        self.value = 0
        
        self.pin.irq(handler=self._button_down, trigger=Pin.IRQ_FALLING)

    def on_down(self, handler):
        self._on_down_handler = handler
    
    def on_up(self, handler):
        self._on_up_handler = handler

    def on_short_click(self, handler):
        self._on_short_click_handler = handler

    def on_long_click(self, handler):
        self._on_long_click_handler = handler


    def _button_down(self, pin):
        if(pin.value() == 1):
            return
        pin.irq(handler=None)
        self.value = pin.value()
        self._down_time = time.ticks_ms()
        print("BTN DOWN", self.pin_number)
        if self._on_down_handler is not None:
            self._on_down_handler(self)
            #micropython.schedule(self._on_down_handler,self)
        
        pin.irq(handler=self._button_up, trigger=Pin.IRQ_RISING)
        
    def _button_up(self, pin):
        if(pin.value() == 0):
            return
        pin.irq(handler=None)
        self.value = pin.value()
        print("BTN UP", self.pin_number)
        if self._on_up_handler is not None:
            self._on_up_handler(self)
            #micropython.schedule(self._on_up_handler,self)

        if time.ticks_diff(time.ticks_ms(), self._down_time) > self.long_click_duration_ms:
            print("BTN LONG CLICK", self.pin_number)
            if self._on_long_click_handler is not None:
                self._on_long_click_handler(self)
                #micropython.schedule(self._on_long_click_handler,self)
        else:
            print("BTN SHORT CLICK", self.pin_number)
            if self._on_short_click_handler is not None:
                self._on_short_click_handler(self)
                #micropython.schedule(self._on_short_click_handler,self)

        pin.irq(handler=self._button_down, trigger=Pin.IRQ_FALLING)


