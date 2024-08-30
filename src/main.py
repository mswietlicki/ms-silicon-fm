from machine import Pin, PWM, Timer
from neopixel import NeoPixel
from utime import sleep_ms, ticks_ms, ticks_diff, sleep_us
import ujson
from config import Config
from sa828 import SA828
from button import Button
import gc

class RatioState():
    Idle = "idle"
    Transmitting = "transmitting"
    Receiving = "receiving"
    Error = "error"

state = RatioState.Idle
state_led = NeoPixel(Pin(16, Pin.OUT), 1)

def show_state():
    if state == RatioState.Idle:
        state_led[0] = (10, 0, 0) # green
    elif state == RatioState.Transmitting:
        state_led[0] = (0, 20, 20)
    elif state == RatioState.Receiving:
        state_led[0] = (0, 0, 50)
    elif state == RatioState.Error:
        state_led[0] = (0, 50, 0)
    else:
        state_led[0] = (0, 0, 0)
    state_led.write()

show_state()

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
sa828.select_channel(config.channel)
print("SAVE:", sa828.write_parameters())


def increment_channel(amount):
    config.channel = (config.channel + amount) % 16
    print("Channel", config.channel + 1)
    sa828.select_channel(config.channel)
    with open(Config.DEFAULT_PATH, "w") as f:
        f.write(ujson.dumps(config.__dict__))

audio_timer = Timer()
audio_buffer = bytes()
audio_position = 0
audio_pwm: PWM
audio_queue = []

def play_audio_callback(timer):
    global audio_buffer, audio_position, audio_queue

    if audio_position >= len(audio_buffer):
        timer.deinit()
        audio_buffer = bytes()
        audio_position = 0
        if(len(audio_queue) > 0):
            play_audio(*audio_queue)
        else:
            #audio_pwm.deinit()
            sa828.free_speaker()
        return

    sample = audio_buffer[audio_position]
    audio_position += 1
    audio_pwm.duty_u16((sample << 8) | sample)

def play_audio(*filenames: str):
    global audio_timer, audio_buffer, audio_position, audio_pwm, audio_queue

    if(filenames == None or len(filenames) == 0):
        return
    
    audio_queue = list(filenames)

    f = open(f"audio/{audio_queue.pop(0)}.raw","rb")
    audio_buffer = f.read() #bytearray(buffer_size)
    read_length = len(audio_buffer) #f.readinto(buf)
    f.close()

    print(read_length)
    audio_pwm = sa828.lock_speaker()
    audio_pwm.freq(96000)
    audio_position = 0
    audio_timer.init(freq=8000, mode=Timer.PERIODIC, callback=play_audio_callback)

def play_current_channel():
    play_audio(f"{config.channel+1}")

def play_hello():
    play_audio("hello", "channel", f"{config.channel+1}")

def on_btn_up_long_click(button):
    increment_channel(1)
    play_current_channel()
    print(free())

def on_btn_down_long_click(button):
    increment_channel(-1)
    play_current_channel()
    print(free())

def free(full=True):
  gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

# Set the speaker volume
pin14 = Pin(14, Pin.OPEN_DRAIN, None, value=0)
pin15 = Pin(15, Pin.OPEN_DRAIN, None, value=0)

btn_up = Button(2)
btn_up.on_long_click(on_btn_up_long_click)
btn_down = Button(1)
btn_down.on_long_click(on_btn_down_long_click)
btn_ptt = Button(3)
btn_ptt.on_down(lambda button: sa828.talk_on())
btn_ptt.on_up(lambda button: sa828.talk_off())

play_hello()
print(free())

while True:
    sleep_ms(100)
    show_state()


    