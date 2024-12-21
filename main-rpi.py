import smbus2
import socket

PICO_ADDRESS = 0x04

# Create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to an address and port
server_socket.bind(('0.0.0.0', 5000))

# Enable the server to accept connections
server_socket.listen()
print(f"Server listening on {host}:{port}")

# Accept connection from client
client_socket, addr = server_socket.accept()
print(f"Got connection from {addr}")

# Create an I2C bus object
bus = smbus.SMBus(1)  # For Raspberry Pi, use bus number 1

# Define the I2C address of the Pico
PICO_ADDRESS = 0000  # Change this to your Pico's I2C address

def send_pwm_value(pin, duty_cycle):
    # Send pin number and duty cycle to the Pico
    bus.write_i2c_block_data(PICO_ADDRESS, pin, [duty_cycle])


# Define motor control parameters (adjust based on your ESC) 
REVERSE = 1100 
FORWARD = 1900 
OFF = 1500 

def send_combined_data(signal, thrust_gain):
    """Send both function signal and thrust gain."""
    try:
        # Pack the data: 1 byte for signal, 4 bytes for float thrust_gain
        data = bytearray(2)
        data[0] = signal
        data[1] = thrust_gain
        bus.write_i2c_block_data(PICO_ADDRESS, 0, data)
    except Exception as e:
        print(f"Error sending data: {e}")

