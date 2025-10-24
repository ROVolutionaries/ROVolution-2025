from machine import Pin, I2C, PWM
import time

# Initialize I2C on GPIO pins (SDA=Pin 0, SCL=Pin 1)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)

SLAVE_ADDRESS = 0x10

#variable for leak sensing
isLeak = False

#PWM microsecond values for forward, stop, reverse
F = 1900
S = 1500
R = 1100

# Define individual  pins on pico (change according to electrical diagram)
vMotor1 = 1
vMotor2 = 2
vMotor3 = 3
vMotor4 = 4
hMotor1 = 5
hMotor2 = 6
hMotor3 = 7
hMotor4 = 8
pH = machine.ADC(28)
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
def move_forward(thrust):
    forward(h3, thrust)
    forward(h4, thrust)
    reverse(h1, thrust)
    reverse(h2, thrust)

def back(thrust):
    reverse(h3, thrust)
    reverse(h4, thrust)
    forward(h1, thrust)
    forward(h2, thrust)

def right(thrust):
    forward(h1, thrust)
    forward(h3, thrust)
    reverse(h2, thrust)
    reverse(h4,thrust)

def left(thrust):
    forward(h2, thrust)
    forward(h4, thrust)
    reverse(h1, thrust)
    reverse(h3,thrust)

def forward_left(thrust):
    forward(h4, thrust)
    reverse(h1, thrust)

def forward_right(thrust):
    forward(h3, thrust)
    reverse(h2, thrust)

def back_left(thrust):
    forward(h1, thrust)
    reverse(h4, thrust)

def back_right(thrust):
    reverse(h3, thrust)
    forward(h2, thrust)

def up(thrust):
    reverse(v1, thrust)
    reverse(v2, thrust)
    reverse(v3, thrust)
    reverse(v4, thrust)

def down(thrust):
    forward(v1, thrust)
    forward(v2, thrust)
    forward(v3, thrust)
    forward(v4, thrust)

def roll_right(thrust):
    forward(v1, thrust)
    reverse(v2, thrust)
    forward(v3, thrust)
    reverse(v4, thrust)

def roll_left(thrust):
    reverse(v1, thrust)
    forward(v2, thrust)
    reverse(v3, thrust)
    forward(v4, thrust)

def pitch_forward(thrust):
    forward(v1, thrust)
    forward(v2, thrust)
    reverse(v3, thrust)
    reverse(v4, thrust)

def pitch_back(thrust):
    reverse(v1, thrust)
    reverse(v2, thrust)
    forward(v3, thrust)
    forward(v4, thrust)

def yaw_right(thrust):
    reverse(h3, thrust)
    forward(h4, thrust)
    forward(h1, thrust)
    reverse(h2, thrust)

def yaw_left(thrust):
    forward(h3, thrust)
    reverse(h4, thrust)
    reverse(h1, thrust)
    forward(h2, thrust)

def read_ph():
    raw_pH = pH.read_u16()
    #update later to include some operation to convert to reading between 0 and 14

def leak():
    global isLeak
    if leak.value() == 0:
        isLeak = 0
    elif leak.value() == 1:
        isLeak = 1

def read_commands():
    data = bytearray(2)  # ✅ Initialize before use
    i2c.readinto(data)  # ✅ Read data into bytearray

    signal = data[0]  # First byte is the signal
    thrust_gain = data[1]  # Second byte is the scaled thrust gain (0-100)
    thrust = thrust_gain / 100.0  # Convert back to 0.0-1.0 range

    return (signal, thrust)

def send_sensor_data():
    global isLeak

    data = bytearray(2)
    data[0] = isLeak
    data[1] = int(read_ph() * 100)
    i2c.writeto(SLAVE_ADDRESS, data)

while True:
    commands = read_commands()
    signal = commands[0]
    thrust = commands[1]
    if signal == 1:
        move_forward(thrust)
    elif signal == 2:
        back(thrust)
    elif signal == 3:
        right(thrust)
    elif signal == 4:
        left(thrust)
    elif signal == 5:
        forward_left(thrust)
    elif signal == 6:
        forward_right(thrust)
    elif signal == 7:
        back_left(thrust)
    elif signal == 8:
        back_right(thrust)
    elif signal == 9:
        up(thrust)
    elif signal == 10:
        down(thrust)
    elif signal == 11:
        roll_right(thrust)
    elif signal == 12:
        roll_left(thrust)
    elif signal == 13:
        pitch_forward(thrust)
    elif signal == 14:
        pitch_back(thrust)
    elif signal == 15:
        yaw_right(thrust)
    elif signal == 16:
        yaw_left(thrust)
        
    elif signal == 17:
        send_sensor_data()

    elif signal == 18():
        led = Pin("LED", Pin.OUT)
        led.on()

while True:
    time.sleep(0.5)
    devices = i2c.scan()
    if SLAVE_ADDRESS in devices:
        print("Slave device found!")
    else:
        print("Slave device not found!")

    





    
