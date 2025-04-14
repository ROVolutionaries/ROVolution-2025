#include "pico/stdlib.h"
#include <stdio.h>
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/uart.h"
#include <array>

#define UART_ID uart1

#define UART_TX_PIN 4
#define UART_RX_PIN 5

//UART handler data
static uint8_t byte_count = 0;
static uint8_t signal = 0;
static uint8_t thrust_gain = 0;
char data[2];


static const uint BAUDRATE = 115200; // 100 kHz

//PWM microsecond values for forward, stop, reverse
const uint16_t F = 1900;
const uint16_t S = 1500;
const uint16_t R = 1100;

// LED PIN
const uint LED_PIN = PICO_DEFAULT_LED_PIN;

float thrust;

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

bool check_leak() {
    isLeak = !gpio_get(leak_pin);  // Invert because 0 means leak detected
    return isLeak;
}
int int_from_uart(uart_inst_t *uart) {
    int result = 0;
    char c;
    while (1) {
        c = uart_getc(uart);
        if (c >= '0' && c <= '9') {
            result = result * 10 + (c - '0');
        } else {
            // Non-digit character received, assume end of number
            break;
        }
    }
    return result;
}

void on_uart_rx() {
    while (uart_is_readable(UART_ID)){
        if (byte_count == 0){
            signal = int_from_uart(UART_ID);
            printf("Received character: %d\n", signal);

            byte_count++;
        }
        else{
            thrust_gain = int_from_uart(UART_ID);
            byte_count = 0;
        }

        float thrust = thrust_gain / 100.0f;  // Convert back to 0.0-1.0 range

        gpio_put(LED_PIN, 0);
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
            case 17: gpio_put(LED_PIN, 0); break; // Turn on LED
            default: break; // Do nothing for unrecognized signals
            //need to add sending sensor data functionality
        }
    }

    
}

void setup_uart() {
    uart_init(UART_ID, 2400);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_baudrate(UART_ID, BAUDRATE);
    uart_set_fifo_enabled(UART_ID, false);

    int UART_IRQ = UART_ID == uart0 ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(UART_IRQ, on_uart_rx); //UART 0 or 1?
    irq_set_enabled(UART_IRQ, true);
    uart_set_irq_enables(UART_ID, true, false);

}

int main() {
    stdio_init_all();

    // Initialize ADC for pH sensor
    adc_init();
    adc_gpio_init(pH_pin);

    // Initialize leak sensor pin
    gpio_init(leak_pin);
    gpio_set_dir(leak_pin, GPIO_IN);

    // Initialize LED
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    initialize_motors();
    gpio_put(LED_PIN, 1);

    setup_uart();

    while(1){
        tight_loop_contents();
    }

    return 0;
}

