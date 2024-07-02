from machine import UART, Pin
import time

class SA828:
    channels = []
    tx_subaudio = "000"
    rx_subaudio = "000"
    sq = "1"
    
    def __init__(self, uart_id=0, baudrate=9600, tx_pin=0, rx_pin=1):
        self.uart = UART(uart_id, baudrate=baudrate, bits=8, parity=None, stop=1, tx=Pin(tx_pin), rx=Pin(rx_pin))
        time.sleep(0.1)  # Allow some time for the UART to initialize
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
        time.sleep(0.05)  # Wait for the command to be processed by the SA828
        response = b""
        while True:
            if self.uart.any():
                chunk = self.uart.read()
                if chunk:
                    response += chunk
                    if response.endswith(b"\r\n"):
                        break
                time.sleep(0.01)  # Small delay to allow more data to arrive
            else:
                time.sleep(0.01)  # Small delay to wait for the next chunk of data
            
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
        
    def set_channels(self, channels):
        self.channels = channels