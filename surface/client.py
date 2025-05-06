import socket
import time
import pygame
import struct
import threading

#Initialising UDP Client
msgFromClient = "Hello"
bytesToSend = msgFromClient.encode('utf-8')
serverAddress = ('169.254.37.82', 2222)
bufferSize = 1024

UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPClient.sendto(bytesToSend, serverAddress)
time.sleep(0.5)
UDPClient.sendto(bytesToSend, serverAddress)
print("Sent message to Pi: ", msgFromClient)
format = ""

header_map = {
        "float": 0x01,
        "int": 0x02,
        "boolean": 0x03
    }

camera_map = {
    "main": 0,
    "gripper": 1,
    "jelly": 2,
    "fish": 3
}

def switch_camera():
    #Camera switching code
    print()

precision_mode = False

#Range from 0-3, 0-4 for 5 cameras
currentCamera = 0


def sendControl(header, signal, data):
    if header == 0x01:
        format = "<Bif"
        if precision_mode == True:
            data = data/2 #HALF SCALE FACTOR OF THRUST IN PRECISION MODE

    elif header == 0x02:
        format = "<Bii"
    elif header == 0x03:
        format = "<Bi?"
    bytesToSend = struct.pack(format, header, signal, data)
    UDPClient.sendto(bytesToSend, serverAddress)


# Initialize pygame
pygame.init()
# Initialize the joystick
pygame.joystick.init()
clock = pygame.time.Clock()
# Check if a joystick is connected
if pygame.joystick.get_count() == 0:
    print("No joystick connected!")
    exit()
# Get the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"Joystick connected: {joystick.get_name()}")
DEAD_ZONE = 0.06

running = True
print("Number of hats:", joystick.get_numhats())
while True:
    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
            running = False
                # Joystick  events

        if event.type == pygame.JOYAXISMOTION:

            # Analog stick inputs
            left_stick_x = joystick.get_axis(0)  #Left stick horizontal
            left_stick_y = joystick.get_axis(1)  #Left stick vertical
            right_stick_x = joystick.get_axis(2)  #Right stick horizontal
            right_stick_y = joystick.get_axis(3)  #Right stick vertical

            sticks = [left_stick_x, left_stick_y, right_stick_x, right_stick_y]

            # Apply dead zone to each axis
            left_stick_x = 0 if abs(left_stick_x) < DEAD_ZONE else left_stick_x
            left_stick_y = 0 if abs(left_stick_y) < DEAD_ZONE else left_stick_y
            right_stick_x = 0 if abs(right_stick_x) < DEAD_ZONE else right_stick_x
            right_stick_y = 0 if abs(right_stick_y) < DEAD_ZONE else right_stick_y

            print("Left stick x: ", left_stick_x)
            print("Left stick y: ", left_stick_y)
            print("Right stick x: ", right_stick_x)
            print("Right stick y: ", right_stick_y)


            if left_stick_x > 0.0:
                sendControl(header_map['float'], 3, left_stick_x) #Lateral left
            else:

                sendControl(header_map['float'], 4, abs(left_stick_x)) #Lateral right
            
            if left_stick_y > 0.0:
                sendControl(header_map['float'], 1, left_stick_y) #Forward
            else:
                sendControl(header_map['float'], 2, abs(left_stick_y)) #Reverse

            if right_stick_x > 0.0:
                sendControl(header_map['float'], 15, right_stick_x) #Yaw right
            else:
                sendControl(header_map['float'], 16, abs(right_stick_x)) #Yaw left

            if right_stick_y > 0.0:
                sendControl(header_map['float'], 13, right_stick_y) #Pitch up
            else:
                sendControl(header_map['float'], 13, abs(right_stick_y)) #Pitch down
        
        # Button press events
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            print(f"Button {button} pressed")  # Add this line to identify buttons

            if button == 0:  
                sendControl(header_map['int'], 20, -1) #Grabber close
                print("X Pressed")
            elif button == 1:
                if currentCamera == camera_map["jelly"]:
                    sendControl(header_map['int'], 17, -1) #Jelly close
                elif currentCamera == camera_map["fish"]:
                    sendControl(header_map['int'], 18, -1) #Fish close
                    
                print("Circle Pressed")

            elif button == 2:  
                if currentCamera == camera_map["jelly"]:
                    sendControl(header_map['int'], 17, 1) #Jelly open
                elif currentCamera == camera_map["fish"]:
                    sendControl(header_map['int'], 18, 1) #Fish open

                print("Square Pressed")

            elif button == 3: 
                sendControl(header_map['int'], 20, -1) #Grabber open
                print("Triangle Pressed")

            elif button == 4:  
                sendControl(header_map['int'], 12, -1) #Roll left
                print("L1 Pressed")

            elif button == 5:  
                sendControl(header_map['int'], 11, 1) #Roll right
                print("R1 Pressed")

            elif button == 9:  
                l2_trigger = joystick.get_axis(4) 
                l2_scaled = (l2_trigger + 1) / 2

                sendControl(header_map['float'], 10, l2_scaled) #Descend 

                print("L2 Button Pressed")

            elif button == 10:  
                r2_trigger = joystick.get_axis(5) 
                r2_scaled = (r2_trigger + 1) / 2

                sendControl(header_map['float'], 9, r2_scaled) #Descend

                print("R2 Button Pressed")

            elif button == 15:  
                #Toggle precision mode
                if precision_mode == False:
                    precision_mode = True
                else:
                    precision_mode = False
                print("Middle Button Pressed")

        # D-pad inputs
        if event.type == pygame.JOYHATMOTION:
            dpad_x, dpad_y = event.value
            print(f"D-pad: ({dpad_x}, {dpad_y})")

            if dpad_y > 0:
                sendControl(header_map['int'], 19, 1) #Camera tilt up
            else: 
                sendControl(header_map['float'], 19, -1) #Camera tilt down

            if dpad_x > 0:
                switch_camera() #Konstantin update
            else: 
                switch_camera() #Konstantin update
            
            # D-pad up: (0, 1), down: (0, -1), left: (-1, 0), right: (1, 0)


            


