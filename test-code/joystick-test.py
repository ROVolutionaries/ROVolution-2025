import pygame

# Initialize pygame
pygame.init()

# Initialize the joystick
pygame.joystick.init()

# Check if a joystick is connected
if pygame.joystick.get_count() == 0:
    print("No joystick connected!")
    exit()

# Get the first joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

print(f"Joystick connected: {joystick.get_name()}")

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
            
            print(f"Left Stick: ({left_stick_x}, {left_stick_y})")
            print(f"Right Stick: ({right_stick_x}, {right_stick_y})")
        
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
            elif button == 6:  # L2 (Digital button, not trigger)
                print("L2 Button Pressed")
            elif button == 7:  # R2 (Digital button, not trigger)
                print("R2 Button Pressed")
            elif button == 8:  # Middle button
                print("Middle Button Pressed")
        
        # D-pad inputs
        if event.type == pygame.JOYHATMOTION:
            dpad_x, dpad_y = joystick.get_hat(0)
            print(f"D-pad: ({dpad_x}, {dpad_y})")
            # D-pad up: (0, 1), down: (0, -1), left: (-1, 0), right: (1, 0)
    
    # Optional: L2/R2 triggers (analog) are axes 4 and 5 on many controllers
    l2_trigger = joystick.get_axis(4)
    r2_trigger = joystick.get_axis(5)
    print(f"L2 Trigger: {l2_trigger}, R2 Trigger: {r2_trigger}")

    # Limit loop execution speed
    pygame.time.wait(10)

# Quit pygame
pygame.quit()
