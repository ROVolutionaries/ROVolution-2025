#include "pico/stdlib.h"
#include "hardware/i2c.h"
#include <stdio.h>
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include <array>

#define I2C_ADDR 0x10

//PWM microsecond values for forward, stop, reverse
const uint16_t F = 1900;
const uint16_t S = 1500;
const uint16_t R = 1100;

// Thrusters
const uint8_t vMotor1 = 1;
const uint8_t vMotor2 = 2;
const uint8_t vMotor3 = 3;
const uint8_t vMotor4 = 4;
const uint8_t hMotor1 = 5;
const uint8_t hMotor2 = 6;
const uint8_t hMotor3 = 7;
const uint8_t hMotor4 = 8;

std::array<uint8_t, 8> motor_pins = {vMotor1, vMotor2, vMotor3, vMotor4, hMotor1, hMotor2, hMotor3, hMotor4};

// Sensors
const uint8_t pH_pin = 28;  // ADC input on GPIO 28
const uint8_t leak_pin = 16;

bool isLeak = false;

std::array<uint, 8> slice_num;
std::array<uint, 8> channel;

// Initialise all thrusters to pulse width 1500 microseconds
void initialize_motors() {
    uint8_t motors[] = {vMotor1, vMotor2, vMotor3, vMotor4, hMotor1, hMotor2, hMotor3, hMotor4};
    for (int i = 0; i < 8; i++) {
        gpio_set_function(motors[i], GPIO_FUNC_PWM);
        slice_num[i] = pwm_gpio_to_slice_num(motors[i]);
        channel[i] = pwm_gpio_to_channel(motors[i]);
        pwm_set_wrap(slice_num[i], 20000);
        pwm_set_chan_level(slice_num[i], channel[i], (S*20000)/20000);
        pwm_set_enabled(slice_num[i], true);
    }
    sleep_ms(1000);
}

void set_pwm_duty(uint8_t pin, uint16_t duty_ns) {
    uint16_t level = (duty_ns * 20000) / 20000;  // Convert microseconds to proportion of 20000
    pwm_set_chan_level(pwm_gpio_to_slice_num(pin), pwm_gpio_to_channel(pin), level);
}

// Basic motor functions
void forward(uint8_t motor, uint8_t thrust) {
    set_pwm_duty(motor, 1500 + thrust * 400);
}

void reverse(uint8_t motor, uint8_t thrust) {
    set_pwm_duty(motor, 1500 - thrust * 400);
}

void stop(uint8_t motor) {
    set_pwm_duty(motor, 1500);
}

// Vectored movement functions
void move_forward(uint8_t thrust) {
    forward(hMotor3, thrust);
    forward(hMotor4, thrust);
    reverse(hMotor1, thrust);
    reverse(hMotor2, thrust);
}

void back(uint8_t thrust) {
    reverse(hMotor3, thrust);
    reverse(hMotor4, thrust);
    forward(hMotor1, thrust);
    forward(hMotor2, thrust);
}

void right(uint8_t thrust) {
    forward(hMotor1, thrust);
    forward(hMotor3, thrust);
    reverse(hMotor2, thrust);
    reverse(hMotor4, thrust);
}

void left(uint8_t thrust) {
    forward(hMotor2, thrust);
    forward(hMotor4, thrust);
    reverse(hMotor1, thrust);
    reverse(hMotor3, thrust);
}

void forward_left(uint8_t thrust) {
    forward(hMotor4, thrust);
    reverse(hMotor1, thrust);
}

void forward_right(uint8_t thrust) {
    forward(hMotor3, thrust);
    reverse(hMotor2, thrust);
}

void back_left(uint8_t thrust) {
    forward(hMotor1, thrust);
    reverse(hMotor4, thrust);
}

void back_right(uint8_t thrust) {
    reverse(hMotor3, thrust);
    forward(hMotor2, thrust);
}

void up(uint8_t thrust) {
    reverse(vMotor1, thrust);
    reverse(vMotor2, thrust);
    reverse(vMotor3, thrust);
    reverse(vMotor4, thrust);
}

void down(uint8_t thrust) {
    forward(vMotor1, thrust);
    forward(vMotor2, thrust);
    forward(vMotor3, thrust);
    forward(vMotor4, thrust);
}

void roll_right(uint8_t thrust) {
    forward(vMotor1, thrust);
    reverse(vMotor2, thrust);
    forward(vMotor3, thrust);
    reverse(vMotor4, thrust);
}

void roll_left(uint8_t thrust) {
    reverse(vMotor1, thrust);
    forward(vMotor2, thrust);
    reverse(vMotor3, thrust);
    forward(vMotor4, thrust);
}

void pitch_forward(uint8_t thrust) {
    forward(vMotor1, thrust);
    forward(vMotor2, thrust);
    reverse(vMotor3, thrust);
    reverse(vMotor4, thrust);
}

void pitch_back(uint8_t thrust) {
    reverse(vMotor1, thrust);
    reverse(vMotor2, thrust);
    forward(vMotor3, thrust);
    forward(vMotor4, thrust);
}

void yaw_right(uint8_t thrust) {
    reverse(hMotor3, thrust);
    forward(hMotor4, thrust);
    forward(hMotor1, thrust);
    reverse(hMotor2, thrust);
}

void yaw_left(uint8_t thrust) {
    forward(hMotor3, thrust);
    reverse(hMotor4, thrust);
    reverse(hMotor1, thrust);
    forward(hMotor2, thrust);
}

uint16_t read_ph() {
    adc_select_input(2);  // Select ADC input 2 (GPIO 28)
    uint16_t raw_pH = adc_read();
    // Update later to include some operation to convert to reading between 0 and 14
    return raw_pH;
}

void check_leak() {
    isLeak = !gpio_get(leak_pin);  // Invert because 0 means leak detected
}

void send_sensor_data() {
    uint8_t data[2];
    data[0] = isLeak ? 1 : 0;
    data[1] = static_cast<uint8_t>(read_ph() * 100 / 65535);  // Scale 16-bit ADC value to 0-100 range

    i2c_write_raw_blocking(i2c0, data, 2);
}

std::pair<uint8_t, float> read_commands() {
    uint8_t data[2];
    int bytes_read = i2c_read_raw_blocking(i2c0, data, 2);
    
    if (bytes_read != 2) {
        // Handle error: didn't receive expected amount of data
        return std::make_pair(0, 0.0f);
    }

    uint8_t signal = data[0];  // First byte is the signal
    uint8_t thrust_gain = data[1];  // Second byte is the scaled thrust gain (0-100)
    float thrust = thrust_gain / 100.0f;  // Convert back to 0.0-1.0 range

    return std::make_pair(signal, thrust);
}

int main() {
    stdio_init_all();

    // i2c setup
    i2c_init(i2c0, 10000);
    i2c_set_slave_mode(i2c0, true, I2C_ADDR);
    gpio_set_function(2, GPIO_FUNC_I2C);
    gpio_set_function(3, GPIO_FUNC_I2C);
    gpio_pull_up(2);
    gpio_pull_up(3);

    // Initialize ADC for pH sensor
    adc_init();
    adc_gpio_init(pH_pin);

    // Initialize leak sensor pin
    gpio_init(leak_pin);
    gpio_set_dir(leak_pin, GPIO_IN);

    // Initialize LED
    const uint LED_PIN = PICO_DEFAULT_LED_PIN;
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    initialize_motors();

    while (true) {
        auto [signal, thrust] = read_commands();
        
        switch(signal) {
            case 0: gpio_put(LED_PIN, 1); break;
            case 1: move_forward(thrust); break;
            case 2: back(thrust); break;
            case 3: right(thrust); break;
            case 4: left(thrust); break;
            case 5: forward_left(thrust); break;
            case 6: forward_right(thrust); break;
            case 7: back_left(thrust); break;
            case 8: back_right(thrust); break;
            case 9: up(thrust); break;
            case 10: down(thrust); break;
            case 11: roll_right(thrust); break;
            case 12: roll_left(thrust); break;
            case 13: pitch_forward(thrust); break;
            case 14: pitch_back(thrust); break;
            case 15: yaw_right(thrust); break;
            case 16: yaw_left(thrust); break;
            case 17: send_sensor_data(); break;
            case 18: gpio_put(LED_PIN, 1); break; // Turn on LED
            default: break; // Do nothing for unrecognized signals
        }

        sleep_ms(10); // Small delay to prevent tight looping
    }

    return 0;
}
