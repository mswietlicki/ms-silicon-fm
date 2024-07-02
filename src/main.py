from machine import UART, Pin
import time
from sa828 import SA828

channels = ['446.0063','446.0063', '446.0188', '446.0188', '446.0313', '446.0313', '412.7500', '412.7500', '413.7500', '413.7500', '414.7500', '414.7500', '415.7500', '415.7500', '416.7500', '416.7500', '417.7500', '417.7500', '418.7500', '418.7500', '419.7500', '419.7500', '420.7500', '420.7500', '421.7500', '421.7500', '422.7500', '422.7500', '423.7500', '423.7500', '424.7500', '424.7500']

sa828 = SA828()

sa828.set_channels(channels)
print("SAVE: ", sa828.write_parameters())