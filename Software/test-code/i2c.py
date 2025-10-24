import pigpio

pi = pigpio.pi()
handle = pi.i2c_open(1, SLAVE_ADDRESS)  # Bus 1, Slave mode

while True:
    (count, data) = pi.i2c_read_device(handle, 16)  # Read up to 16 bytes
    if count > 0:
        print("Received:", data)
