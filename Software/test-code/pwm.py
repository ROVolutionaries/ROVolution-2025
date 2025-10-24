import pigpio
import time

servo = 13 

pi = pwm = pigpio.pi() 
pwm.set_mode(13, pigpio.OUTPUT)
for i in range(500, 2500, 5):
    pwm.set_servo_pulsewidth(servo, i)
