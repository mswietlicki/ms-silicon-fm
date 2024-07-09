from machine import Pin, PWM
from utime import sleep, sleep_ms
from sa828 import SA828

channels = []
for i in range(16):
    frequency = 446.00625 + (i * 0.0125)
    channels.append(f"{frequency:.4f}")
    channels.append(f"{frequency:.4f}")
print("CHANNELS:", channels)

squelch = "4"
filter = "000"

sa828 = SA828()
sa828.set_channels(channels)
sa828.set_squelch(squelch)
sa828.set_subaudio(filter)
print("SAVE:", sa828.write_parameters())


pin14 = Pin(14, Pin.OPEN_DRAIN, None, value=1)
pin15 = Pin(15, Pin.OPEN_DRAIN, None, value=1)


print("PLAY:")
speaker_pin = sa828.lock_speaker()
speakerPWN = PWM(speaker_pin)
speakerPWN.init(duty_u16=1000, duty_ns=15252, freq=1000)

sleep_ms(500)

print("STOP:")
speakerPWN.deinit()
sa828.unlock_speaker()
