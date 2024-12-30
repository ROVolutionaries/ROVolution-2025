import smbus2
import threading

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

