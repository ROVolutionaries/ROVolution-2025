from machine import Pin, I2C, PWM
import time

# Initialize I2C on GPIO pins (SDA=Pin 0, SCL=Pin 1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

# Define the I2C address of the Pi
buffer = bytearray(32)

#variable for leak sensing
isLeak = False

#PWM microsecond values for forward, stop, reverse
F = 1900
S = 1500
R = 1100
thrust = 1 #percentage of thrust power used from 0.0 to 1.0

# Define individual  pins on pico (change according to electrical diagram)
vMotor1 = 1
vMotor2 = 2
vMotor3 = 3
vMotor4 = 4
hMotor1 = 5
hMotor2 = 6
hMotor3 = 7
hMotor4 = 8
pH = machine.ADC(34)
servo1 = 9
servo2 = 10
FOC = 11
laser1 = 12
laser2 = 13
linear = 14
servo3 = 15 #camtilt
leak = Pin(16, Pin.IN)


#create PWM objects
v1 = PWM(Pin(vMotor1))
v2 = PWM(Pin(vMotor2))
v3 = PWM(Pin(vMotor3))
v4 = PWM(Pin(vMotor4))
h1 = PWM(Pin(hMotor1))
h2 = PWM(Pin(hMotor2))
h3 = PWM(Pin(hMotor3))
h4 = PWM(Pin(hMotor4))

motors = [v1, v2, v3, v4, h1, h2, h3, h4]

def initialize_motors():
    for motor in motors:
        motor.duty_ns(S)
    time.sleep(1)

#basic motor functions
def forward(motor, thrust):
    motor.duty_ns(1500 + thrust * 400)

def reverse(motor, thrust):
    motor.duty_ns(1500 - thrust * 400)

def stop(motor):
    motor.duty_ns(1500)

#vectored movement functions
def move_forward():
    forward(h3, thrust)
    forward(h4, thrust)
    reverse(h1, thrust)
    reverse(h2, thrust)

def back():
    reverse(h3, thrust)
    reverse(h4, thrust)
    forward(h1, thrust)
    forward(h2, thrust)

def right():
    forward(h1, thrust)
    forward(h3, thrust)
    reverse(h2, thrust)
    reverse(h4,thrust)

def left():
    forward(h2, thrust)
    forward(h4, thrust)
    reverse(h1, thrust)
    reverse(h3,thrust)

def forward_left():
    forward(h4, thrust)
    reverse(h1, thrust)

def forward_right():
    forward(h3, thrust)
    reverse(h2, thrust)

def back_left():
    forward(h1, thrust)
    reverse(h4, thrust)

def back_right():
    reverse(h3, thrust)
    forward(h2, thrust)

def read_ph():
    raw_pH = pH.read_u16()
    #update later to include some operation to convert to reading between 0 and 14

def leak():
    if leak.value() == 0:
        global isLeak = 0
    elif leak.value() == 1:
        isLeak = 1

def read_commands():
    i2c.readinto(data)
    data = int.from_bytes(data)
    signal = data[0]  # First byte is the signal
    thrust_gain = data[1]  # Second byte is the scaled thrust gain (0-100)
    thrust = thrust_gain / 100.0  # Convert back to 0.0-1.0 range

    return (signal, thrust)

def send_sensor_data():
    data = bytearray(2)
    data[0] = isLeak
    data[1] = int(read_ph * 100)
    i2c.write(data)





    