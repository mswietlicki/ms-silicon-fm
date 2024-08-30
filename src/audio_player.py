from machine import Pin, PWM, Timer

class AudioPlayer:
    
    audio_timer: Timer
    audio_buffer: bytes
    audio_position: int
    audio_pwm: PWM
    audio_queue: list[str]
    audio_volume: int
    
    def __init__(self, lock_speaker, free_speaker, volume: int):
        self.audio_timer = Timer()
        self.audio_buffer = bytes()
        self.audio_position = 0
        self.audio_pwm: PWM
        self.audio_queue = []
        self.lock_speaker = lock_speaker
        self.free_speaker = free_speaker

        self.set_volume(volume)

    def play(self, *filenames: str):
        if(filenames == None or len(filenames) == 0):
            return
        
        self.audio_queue = list(filenames)
        filename = self.audio_queue.pop(0)
        with open(f"audio/{filename}.raw", "rb") as f:
            self.audio_buffer = f.read()

        self.audio_pwm = self.lock_speaker()
        self.audio_pwm.freq(96000)
        self.audio_position = 0
        self.audio_timer.init(freq=8000, mode=Timer.PERIODIC, callback=self.play_audio_callback)

    def play_audio_callback(self, timer):
        if self.audio_position >= len(self.audio_buffer):
            self.audio_timer.deinit()
            self.audio_buffer = bytes()
            self.audio_position = 0
            if(len(self.audio_queue) > 0):
                self.play(*self.audio_queue)
            else:
                self.free_speaker()
            return

        sample = self.audio_buffer[self.audio_position]
        self.audio_position += 1
        self.audio_pwm.duty_u16((sample << 8) | sample)

    def stop(self):
        self.audio_timer.deinit()
        self.audio_buffer = bytes()
        self.audio_position = 0
        if(self.free_speaker):
            self.free_speaker()
        return
    
    def set_volume(self, volume: int):
        self.audio_volume = volume % 4
        self.volume_pin1 = Pin(14, Pin.OPEN_DRAIN, None, value=self.audio_volume & 1)
        self.volume_pin2 = Pin(15, Pin.OPEN_DRAIN, None, value=self.audio_volume & 2)
        return