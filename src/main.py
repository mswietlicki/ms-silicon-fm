from machine import Pin, PWM
from utime import sleep_ms, ticks_ms, ticks_diff, sleep_us
import ujson
from config import Config
from sa828 import SA828
from button import Button

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

def increment_channel(amount):
    config.channel = (config.channel + amount) % 16
    print("Channel", config.channel + 1)
    sa828.select_channel(config.channel)
    with open(Config.DEFAULT_PATH, "w") as f:
        f.write(ujson.dumps(config.__dict__))

def play_current_channel():
    pwm = sa828.lock_speaker()
    pwm.freq(48000)

    f = open(f"numbers/{config.channel+1}.raw","rb")
    buf = bytearray(4096)
    while True:
        read_length = f.readinto(buf)
        print(read_length)
        for sample in buf[:read_length]:
            pwm.duty_u16(sample<<8)
            sleep_us(110)
        if read_length < 4096:
            break
    f.close()

    pwm.deinit()
    sa828.free_speaker()

def on_btn_up_long_click(button):
    increment_channel(1)
    play_current_channel()

def on_btn_down_long_click(button):
    increment_channel(-1)
    play_current_channel()

# Initialize the buttons
button1 = Button(1)
button1.on_long_click(on_btn_up_long_click)
button2 = Button(2)
button2.on_long_click(on_btn_down_long_click)

play_current_channel()

while True:
    sleep_ms(100)