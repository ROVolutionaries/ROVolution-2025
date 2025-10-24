import socket
import time
import struct
import serial
import pigpio
import threading

'''
SIGNALS TO RECEIVE:

0 - ZERO EVERYTHING

#FLOAT DATA TYPE#
1 - Forward
2 - Reverse
3 - Lateral Right
4 - Lateral Left
5 - Forward Left
6 - Forward Right
7 - Back Left
8 - Back Right
9 - Ascend
10 - Descend
11 - Roll Right
12 - Roll Left
13 - Pitch Up
14 - Pitch Down
15 - Yaw Right
16 - Yaw Left

#INT DATA TYPE#
17 - Jelly open/close
18 - Fish open/close
19 - Tilt camera up/down
20 - Grabber open/close
21 - Switch camera previous/next

#BOOLEAN DATA TYPE#
22 - Toggle Precision Mode
23 - Toggle Stabilise Mode
24 - Reset attitude

25 - ZERO EVERYTHING
'''

# pigpio initialisation
pi = pigpio.pi() 
#pin definitions
jelly_servo = 13
fish_servo = 12 
tilt_servo = 19
linear_forward = 24
linear_back = 25
leak_sensor = 26
pi.set_mode(fish_servo, pigpio.OUTPUT)
pi.set_mode(jelly_servo, pigpio.OUTPUT)
pi.set_mode(tilt_servo, pigpio.OUTPUT)
pi.set_mode(linear_forward, pigpio.OUTPUT)
pi.set_mode(linear_back, pigpio.OUTPUT)
pi.set_mode(leak_sensor, pigpio.INPUT)

#data structures for pico communication
header_float = b'\x01'
header_int = b'\x02'
header_boolean = b'\x03'
format_float = "<if"
format_int = "<ii"
format_boolean = "<i?"
pico_signal = []

#data structures for surface communication
isLeak = False
gyro_pos = []

#Serial for reading and writing to Pico
try: 
    ser = serial.Serial('/dev/serial0', 115200, timeout=5)
except:
    print("No UART detected. Please wire UART and try again.")

# Create UDP socket
bufferSize = 1024
serverPort = 2222
sendPort = 5000
# STATIC ADDRESS: serverIP = '192.168.1.100'
serverIP = '169.254.37.82'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((serverIP, serverPort))
print('Server listening...')
# Create a new socket for sending data
send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
send_socket.bind((serverIP, sendPort))


print("Waiting for 'Hello' from client...")
while True:
    message, address = server_socket.recvfrom(bufferSize)
    print(f"Received raw message: {message}")
    try:
        if message.decode('utf-8') == "Hello":
            print("Handshake complete with:", address)
            break  # Only now start the threads
    except UnicodeDecodeError:
        # Not a valid Hello, maybe junk
        continue


def control():
    print("Started control loop.")
    while True:
        # Receiving blocking from client. Waits until a message is received.
        message, address = server_socket.recvfrom(bufferSize)

        header = message[0]  # first byte: header (int)
        print("Header: ", header)
        print("Signal: ", message[1])
        print("Data: ", message[2])


        # Now unpack based on header type
        
        if header == 1:  # float
            if len(message[1:]) != 8:
                print(f"Invalid message length: {len(message[1:])} bytes")
                continue
            signal, data = struct.unpack(format_float, message[1:])
            print(f"Received FLOAT: Signal: {signal}, Data: {data}")
        elif header == 2:  # int
            signal, data = struct.unpack(format_int, message[1:])
            print(f"Received INT: Signal: {signal}, Data: {data}")
        elif header == 3:  # boolean
            signal, data = struct.unpack(format_boolean, message[1:])
            print(f"Received BOOLEAN: Signal: {signal}, Data: {data}")
        else:
            print(f"Unknown header: {header}")
            continue

        # Now act on the signal as before
        if signal in range(1, 17):
            thrust = int(data * 100)
            print("Thrust: ", thrust)
            pico_signal = [signal, thrust]
            ser.write(bytes(pico_signal))
        elif signal == 17:
            print("Signal:", signal)
            print("Data:", data)
            pi.set_servo_pulsewidth(jelly_servo, data)
        elif signal == 18:
            print("Signal:", signal)
            print("Data:", data)
            pi.set_servo_pulsewidth(fish_servo, data)
        elif signal == 19:
            print("Signal:", signal)
            print("Data:", data)
            pi.set_servo_pulsewidth(tilt_servo, data)
        elif signal == 20:
            print("Signal:", signal)
            print("Data:", data)
            if data == 1:
                pi.write(linear_forward, 1)
            else:
                pi.write(linear_back, 1)
        elif signal == 21:
            print("Signal:", signal)
            print("Data:", data)
            # Camera switch code - KONSTANTIN
            print()

def telemetry():
    print("Started telemetry loop")
    global gyro_pos, isLeak, addr
    while True:
        if ser.in_waiting > 0:
            gyro_pos = ser.read(24)
            isLeak = pi.read(leak_sensor)
            send_socket.sendto(gyro_pos + isLeak, addr)
        time.sleep(0.1)


t1 = threading.Thread(target=control, args=[])
t2 = threading.Thread(target=telemetry, args=[])
t1.start()
t2.start()