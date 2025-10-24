import pygame
import math 

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

DEAD_ZONE = 0.05

# Main loop
running = True
while running:
    for event in pygame.event.get():
        # Quit event
        if event.type == pygame.QUIT:
            running = False
        
        # Joystick motion events
        if event.type == pygame.JOYAXISMOTION:
            # Analog stick inputs
            left_stick_x = joystick.get_axis(0)  #Left stick horizontal
            left_stick_y = joystick.get_axis(1)  #Left stick vertical
            right_stick_x = joystick.get_axis(2)  #Right stick horizontal
            right_stick_y = joystick.get_axis(3)  #Right stick vertical
            
            sticks = {
                "Left": (left_stick_x, left_stick_y),
                "Right": (right_stick_x, right_stick_y),
            }

            directions = [
                (337.5, 22.5, "Right"),
                (22.5, 67.5, "Back-Right"),
                (67.5, 112.5, "Back"),
                (112.5, 157.5, "Back-Left"),
                (157.5, 202.5, "Left"),
                (202.5, 247.5, "Forward-Left"),
                (247.5, 292.5, "Forward"),
                (292.5, 337.5, "Forward-Right"),
            ]

            for stick_name, (x, y) in sticks.items():
                # Apply dead zone
                x = 0 if abs(x) < DEAD_ZONE else x
                y = 0 if abs(y) < DEAD_ZONE else y

            print(left_stick_x)

            #Calculate magnitude and normalise
            magnitude = math.sqrt(x**2 + y**2)
            if magnitude > 1:
                magnitude = 1

            #Calculate the angle in degrees
            angle = math.degrees(math.atan2(y, x))
            if angle < 0:
                angle += 360

            #Determine direction
            direction = "Unknown"
            for start, end, dir_name in directions:
                if start <= angle or angle < end:
                    direction = dir_name
                    break

            print(f"{stick_name} Stick - Direction: {direction}, Magnitude: {magnitude:.2f}, Angle: {angle:.2f}°")
                     
        # Button press events
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            if button == 0:  
                print("X Pressed")
            elif button == 1:  
                print("Circle Pressed")
            elif button == 2:  
                print("Square Pressed")
            elif button == 3: 
                print("Triangle Pressed")
            elif button == 4:  
                print("L1 Pressed")
            elif button == 5:  
                print("R1 Pressed")
            elif button == 9:  
                print("L2 Button Pressed")
            elif button == 10:  
                print("R2 Button Pressed")
            elif button == 15:  
                print("Middle Button Pressed")
        
        # D-pad inputs
        if event.type == pygame.JOYHATMOTION:
            dpad_x, dpad_y = joystick.get_hat(0)
            print(f"D-pad: ({dpad_x}, {dpad_y})")
            # D-pad up: (0, 1), down: (0, -1), left: (-1, 0), right: (1, 0)

        # Optional: L2/R2 triggers (analog) are axes 4 and 5 on many controllers
        
        l2_trigger = joystick.get_axis(4)
        r2_trigger = joystick.get_axis(5)
        if l2_trigger != 0 or r2_trigger != 0:
            print(f"L2 Trigger: {l2_trigger}, R2 Trigger: {r2_trigger}")

    
    # Limit loop execution speed
    clock.tick(60)

# Quit pygame
pygame.quit()
