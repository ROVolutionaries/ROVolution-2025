PICO_ADDRESS = 0x04

# Create an I2C bus object
bus = smbus.SMBus(1)  # For Raspberry Pi, use bus number 1

# Define the I2C address of the Pico
PICO_ADDRESS = 0000  # Change this to your Pico's I2C address

def send_pwm_value(pin, duty_cycle):
    # Send pin number and duty cycle to the Pico
    bus.write_i2c_block_data(PICO_ADDRESS, pin, [duty_cycle])
