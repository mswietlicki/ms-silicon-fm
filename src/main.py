from audio_player import AudioPlayer
from state import RatioState
from config import Config
from sa828 import SA828
from button import Button
from utime import sleep_ms
import gc

state = RatioState()
config = Config()

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

def increment_volume(amount: int):
    new_volume = (config.volume + amount)
    if new_volume > 0 and new_volume < 3:
        config.volume = new_volume
    audio_player.set_volume(config.volume)
    config.save()
    print("Volume", config.volume)
    audio_player.play("volume", f"{config.volume}")

def play_current_channel():
    audio_player.play(f"{config.channel+1}")

def play_hello():
    audio_player.play("hello", "channel", f"{config.channel+1}")

def set_volume_up(button):
    increment_volume(1)

def set_volume_down(button):
    increment_volume(-1)

def set_channel_up(button):
    increment_channel(1)
    play_current_channel()

def set_channel_down(button):
    increment_channel(-1)
    play_current_channel()

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

btn_up = Button(2) \
    .on_short_click(set_channel_up) \
    .on_long_click(set_volume_up)
btn_down = Button(1) \
    .on_short_click(set_channel_down) \
    .on_long_click(set_volume_down)
btn_ptt = Button(3) \
    .on_down(talk_on) \
    .on_up(talk_off)

audio_player.play("hello", "channel", f"{config.channel+1}")
print(free())
while True:
    sleep_ms(100)