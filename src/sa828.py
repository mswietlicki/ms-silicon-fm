from machine import UART, Pin, PWM
import utime

class SA828:
    channels: list[str] = []
    tx_subaudio: str = "000"
    rx_subaudio: str = "000"
    sq: str = "2"

    # Control pins
    ptt_pin: Pin
    pwr_pin: Pin
    sleep_pin: Pin
    vox_pin: Pin
    spk_pin: Pin
    spk_en_pin: Pin
    channel_pins: list[Pin]
    
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=12, rx_pin=13, ptt_pin=11, pwr_pin=9, channel_pins=[5, 6, 8, 7], vox_pin=4, spk_pin=26, spk_en_pin=10, sleep_pin=29):
        print("Initializing SA828")

        self.ptt_pin = Pin(ptt_pin, Pin.OPEN_DRAIN, None, value=1)
        self.pwr_pin = Pin(pwr_pin, Pin.OPEN_DRAIN, None, value=0)
        self.sleep_pin = Pin(sleep_pin, Pin.OPEN_DRAIN, None, value=1)
        self.vox_pin = Pin(vox_pin, Pin.OPEN_DRAIN, None, value=1)
        self.spk_pin = Pin(spk_pin, Pin.OPEN_DRAIN, None, value=1)
        self.spk_en_pin = Pin(spk_en_pin, Pin.IN, Pin.PULL_DOWN)
        self.channel_pins = [Pin(pin, Pin.OPEN_DRAIN, None, value=1) for pin in channel_pins]

        self.uart = UART(uart_id, baudrate=baudrate, bits=8, parity=None, stop=1, tx=Pin(tx_pin), rx=Pin(rx_pin))
        utime.sleep(0.1)  # Allow some time for the UART to initialize
        print("FM:", self.read_module())
        parameters = self.read_parameters()
        if parameters.startswith("AA"):
            parameters = parameters[2:].split(',')
            self.channels = parameters[:32]
            self.tx_subaudio = parameters[32]
            self.rx_subaudio = parameters[33]
            self.sq = parameters[34]
            
            print("Channels:", self.channels)
            print("TX_SUBAUDIO:", self.tx_subaudio)
            print("RX_SUBAUDIO:", self.rx_subaudio)
            print("SQ:", self.sq)
        
    def send_command(self, command):
        self.uart.write(command)
        utime.sleep(0.05)  # Wait for the command to be processed by the SA828
        response = b""
        while True:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    response += chunk
                    if response.endswith(b"\r\n"):
                        break
                utime.sleep(0.01)  # Small delay to allow more data to arrive
            else:
                utime.sleep(0.01)  # Small delay to wait for the next chunk of data
            
        if response:
            return response.decode('utf-8')
        return "null"

    def read_module(self):
        command = "AAFAA"
        return self.send_command(command)

    def read_parameters(self):
        command = "AAFA1"
        return self.send_command(command)
    
    def write_dafault_parameters(self):
        command = "AAFA2"
        return self.send_command(command)
    
    def write_parameters(self):
        command = "AAFA3" + (",".join(self.channels)) + "," + self.tx_subaudio + "," + self.rx_subaudio + "," + self.sq
        return self.send_command(command)
    
    def set_channel(self, i, tx, rx):
        self.channels[i*2] = tx
        self.channels[i*2+1] = rx

    def talk_on(self):
        self.ptt_pin.value(0)

    def talk_off(self):
        self.ptt_pin.value(1)

    def set_channels(self, channels):
        self.channels = channels

    def set_squelch(self, sq: int):
        self.sq = f"{sq:01}"

    def set_subaudio(self, filter: int):
        self.tx_subaudio = f"{filter:03}"
        self.rx_subaudio = f"{filter:03}"

    def set_vox(self, enable):
        self.vox_pin.value(enable)
    
    def set_power(self, power):
        self.pwr_pin.value(power)

    def lock_speaker(self):
        self.spk_en_pin.init(mode=Pin.OUT, value=1)
        self.spk_pin.init(Pin.ALT, alt = Pin.ALT_PWM)
        return PWM(self.spk_pin)
    
    def free_speaker(self):
        self.spk_en_pin.init(Pin.IN, Pin.PULL_DOWN)
        self.spk_pin.init(Pin.OPEN_DRAIN, value=1)

    def select_channel(self, channel: int):
        for i, pin in enumerate(self.channel_pins):
            value = (~channel >> i) & 1
            pin.value(value)
