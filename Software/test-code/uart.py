''' Raspberry Pi Pico - Voltmeter
 Sends via uart
 Works with ADC pins 0 to 4
 pins 0 to 2 are gp26 to gp28
 pin 3 unused
 pin 4 is internal temp sensor
 See: www.penguintutor.com/projects/pico '''

import serial
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=5)
data_bytes = [49, 55, 65]
data = bytes(data_bytes)
ser.write(data.to_bytes(1, byteorder='little'))