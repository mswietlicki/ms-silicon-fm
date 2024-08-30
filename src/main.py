from audio_player import AudioPlayer
from machine import Pin, PWM, Timer, ADC
from state import RatioState
from utime import sleep_ms
from config import Config
from sa828 import SA828
from button import Button
import gc

state = RatioState()
config = Config()

# #Pin(25, Pin.OUT, Pin.PULL_DOWN, value=1)
# Pin(29, Pin.IN, None)
# adc0 = ADC(29) # ADC0 pin is GP26
# print(f"VSYS: {adc0.read_u16() * ( 3.3 / 65535)}")

sa828 = SA828()
sa828.set_channels(config.channels)
sa828.set_squelch(config.squelch)
sa828.set_subaudio(config.filter)
sa828.select_channel(config.channel)
print("SA828 WRITE:", sa828.write_parameters())

audio_player = AudioPlayer(sa828.lock_speaker, sa828.free_speaker, config.volume)

def increment_channel(amount):
    config.channel = (config.channel + amount) % 16
    print("Channel", config.channel + 1)
    sa828.select_channel(config.channel)
    config.save()

def play_current_channel():
    audio_player.play(f"{config.channel+1}")

def play_hello():
    audio_player.play("hello", "channel", f"{config.channel+1}")

def set_volume_up(button):
    if config.volume < 3:
        config.volume = (config.volume + 1)
    audio_player.set_volume(config.volume)
    print("Volume", config.volume)
    config.save()
    audio_player.play("volume", config.volume)

def set_volume_down(button):
    if config.volume > 0:
        config.volume = (config.volume - 1)
    audio_player.set_volume(config.volume)
    print("Volume", config.volume)
    config.save()
    audio_player.play("volume", config.volume)

def set_channel_up(button):
    increment_channel(1)
    play_current_channel()
    print(free())

def set_channel_down(button):
    increment_channel(-1)
    play_current_channel()
    print(free())

def talk_on(button):
    sa828.talk_on()
    state.set_state(RatioState.TRANSMITTING)

def talk_off(button):
    sa828.talk_off()
    state.set_state(RatioState.IDLE)

def free(full=True):
  gc.collect()
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

btn_up = Button(2)
btn_up.on_short_click(set_channel_up)
btn_up.on_long_click(set_volume_up)
btn_down = Button(1)
btn_down.on_short_click(set_channel_down)
btn_down.on_long_click(set_volume_down)
btn_ptt = Button(3)
btn_ptt.on_down(talk_on)
btn_ptt.on_up(talk_off)

# Play the hello message
audio_player.play("hello", "channel", f"{config.channel+1}")
print(free())

while True:
    sleep_ms(100)