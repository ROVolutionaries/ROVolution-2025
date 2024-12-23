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
            left_stick_x = joystick.get_axis(0)  # Left stick horizontal
            left_stick_y = joystick.get_axis(1)  # Left stick vertical
            right_stick_x = joystick.get_axis(2)  # Right stick horizontal
            right_stick_y = joystick.get_axis(3)  # Right stick vertical

            # Apply dead zone
            left_stick_x = 0 if abs(left_stick_x) < DEAD_ZONE else left_stick_x
            left_stick_y = 0 if abs(left_stick_y) < DEAD_ZONE else left_stick_y
            right_stick_x = 0 if abs(right_stick_x) < DEAD_ZONE else right_stick_x
            right_stick_y = 0 if abs(right_stick_y) < DEAD_ZONE else right_stick_y

            magnitude = math.sqrt(left_stick_x**2 + left_stick_y**2)

            # Ensure the magnitude is within [0, 1]
            if magnitude > 1:
                magnitude = 1
            
            # Calculate the angle in radians
            angle = math.atan2(left_stick_y, left_stick_x)

            angle_degrees = math.degrees(angle)
            if angle_degrees < 0:
                angle_degrees += 360  #

            if 337.5 <= angle_degrees or angle_degrees < 22.5:
                direction = "Right"
            elif 22.5 <= angle_degrees < 67.5:
                direction = "Back-Right"
            elif 67.5 <= angle_degrees < 112.5:
                direction = "Back"
            elif 112.5 <= angle_degrees < 157.5:
                direction = "Back-Left"
            elif 157.5 <= angle_degrees < 202.5:
                direction = "Left"
            elif 202.5 <= angle_degrees < 247.5:
                direction = "Forward-Left"
            elif 247.5 <= angle_degrees < 292.5:
                direction = "Forward"
            elif 292.5 <= angle_degrees < 337.5:
                direction = "Forward-Right"

            print(f"Direction: {direction}, Magnitude: {magnitude}, Angle {angle_degrees}")

            #if abs(left_stick_x)  != 0 or (left_stick_y) != 0 or abs(right_stick_x) != 0 or abs(right_stick_y) != 0:
            #    print(f"Left Stick: ({left_stick_x}, {left_stick_y})" + f", Right Stick: ({right_stick_x}, {right_stick_y})")
                     
        # Button press events
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            if button == 0:  # Cross (Shape buttons mapping may vary)
                print("Cross Pressed")
            elif button == 1:  # Circle
                print("Circle Pressed")
            elif button == 2:  # Square
                print("Square Pressed")
            elif button == 3:  # Triangle
                print("Triangle Pressed")
            elif button == 4:  # L1
                print("L1 Pressed")
            elif button == 5:  # R1
                print("R1 Pressed")
            elif button == 9:  # L2 (Digital button, not trigger)
                print("L2 Button Pressed")
            elif button == 10:  # R2 (Digital button, not trigger)
                print("R2 Button Pressed")
            elif button == 15:  # Middle button
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
