from machine import Pin, PWM
from utime import sleep
from sa828 import SA828

channels = ['446.0063','446.0063', '446.0188', '446.0188', '446.0313', '446.0313', '412.7500', '412.7500', '413.7500', '413.7500', '414.7500', '414.7500', '415.7500', '415.7500', '416.7500', '416.7500', '417.7500', '417.7500', '418.7500', '418.7500', '419.7500', '419.7500', '420.7500', '420.7500', '421.7500', '421.7500', '422.7500', '422.7500', '423.7500', '423.7500', '424.7500', '424.7500']

sa828 = SA828()

sa828.set_channels(channels)
print("SAVE:", sa828.write_parameters())

pin14 = Pin(14, Pin.OPEN_DRAIN, None, value=1)
pin15 = Pin(15, Pin.OPEN_DRAIN, None, value=1)

# Read or write Speaker Enable flag

speakerPin = Pin(26, Pin.OPEN_DRAIN, None, value=1)
speakerEnable = Pin(27, Pin.IN, Pin.PULL_DOWN)

speakerPWN = PWM(speakerPin)
speakerPin.init(Pin.OPEN_DRAIN, value=1)

print("PLAY:")
speakerEnable.init(mode=Pin.OUT, value=1)
speakerPin.init(Pin.ALT, alt = Pin.ALT_PWM)
speakerPWN.init(duty_u16=1000, duty_ns=15252, freq=1000)
sleep(1)
print("STOP:")
speakerEnable.init(Pin.IN, Pin.PULL_DOWN)
speakerPWN.deinit()
speakerPin.init(Pin.OPEN_DRAIN, value=1)
