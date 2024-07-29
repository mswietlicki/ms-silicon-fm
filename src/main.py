from machine import Pin, PWM
from utime import sleep_ms, ticks_ms
import ujson
from config import Config
from sa828 import SA828

try:
    with open(Config.DEFAULT_PATH, "r") as f:
        config = Config(ujson.load(f))
except OSError:
    # Create a default configuration
    config: Config = Config()
    config.channels = []
    for i in range(16):
        frequency = 446.00625 + (i * 0.0125)
        config.channels.append(f"{frequency:.4f}")
        config.channels.append(f"{frequency:.4f}")
    config.channel = 0
    config.squelch = 4
    config.filter = 0
    config.volume = 3
    # Save the default configuration
    with open(Config.DEFAULT_PATH, "w") as f:
        f.write(ujson.dumps(config.__dict__))
print("Loaded config:", config.__dict__)

# Initialize the SA828 module
sa828 = SA828()
sa828.set_channels(config.channels)
sa828.set_squelch(config.squelch)
sa828.set_subaudio(config.filter)
print("SAVE:", sa828.write_parameters())

# Set the speaker volume
pin14 = Pin(14, Pin.OPEN_DRAIN, None, value=1)
pin15 = Pin(15, Pin.OPEN_DRAIN, None, value=1)

def button1_pressed(change):
    button1.irq(handler=None)
    print("Button 1 pressed")

    config.channel = (config.channel - 1) % 16
    print("Channel", config.channel)
    sa828.select_channel(config.channel)
    with open(Config.DEFAULT_PATH, "w") as f:
        f.write(ujson.dumps(config.__dict__))
    
    sleep_ms(20)
    button1.irq(trigger=Pin.IRQ_FALLING, handler=button1_pressed)

def button2_pressed(change):
    print("Button 2 pressed")
    config.channel = (config.channel + 1) % 16
    print("Channel", config.channel)
    sa828.select_channel(config.channel)
    with open(Config.DEFAULT_PATH, "w") as f:
        f.write(ujson.dumps(config.__dict__))

button1 = Pin(28, Pin.IN, Pin.PULL_UP)
button1.irq(trigger=Pin.IRQ_FALLING, handler=button1_pressed)
button2 = Pin(29, Pin.IN, Pin.PULL_UP)
button2.irq(trigger=Pin.IRQ_FALLING, handler=button2_pressed)
# Test the speaker
print("PLAY:")
speaker_pin = sa828.lock_speaker()
speakerPWN = PWM(speaker_pin)
speakerPWN.init(duty_u16=1000, duty_ns=15252, freq=1000)

sleep_ms(500)

print("STOP:")
speakerPWN.deinit()
sa828.unlock_speaker()

# loop forever  
while True:
    sleep_ms(100)