class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0
        self.previous_error = 0

    def update(self, setpoint, measured_value):
        error = measured_value - setpoint
        self.integral += error
        derivative = error - self.previous_error
        
        output = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
        self.previous_error = error
        
        return output

yaw_control = PID(1, 1, 1)
pitch_control = PID(1, 1, 1) 
roll_control = PID(1, 1, 1) 

def get_roll_PID(roll_input):
    roll_control.update(0, roll_input) #integrate with gyro code later

def get_pitch_PID(pitch_input):
    pitch_control.update(0, pitch_input) #integrate with gyro code later

def get_yaw_PID(yaw_input):
    yaw_control.update(0, yaw_input) #integrate with gyro code later

