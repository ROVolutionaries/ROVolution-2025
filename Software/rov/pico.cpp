#include "pico/stdlib.h"
#include <stdio.h>
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/uart.h"
#include <array>
#include "hardware/i2c.h"
#include "pico/binary_info.h"


#define UART_ID uart1
#define UART_TX_PIN 8
#define UART_RX_PIN 9


//UART handler data
static uint8_t byte_count = 0;
static uint8_t signal = 0;
static uint8_t thrust_gain = 0;
char data[2];


static const uint BAUDRATE = 115200; // 100 kHz
static int addr = 0x68;


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
const uint8_t vMotor4 = 10;
const uint8_t hMotor1 = 11;
const uint8_t hMotor2 = 6;
const uint8_t hMotor3 = 7;
const uint8_t hMotor4 = 0;

std::array<uint8_t, 8> motor_pins = {vMotor1, vMotor2, vMotor3, vMotor4, hMotor1, hMotor2, hMotor3, hMotor4};

// Sensors
const uint8_t pH_pin = 28;  // ADC input on GPIO 28
const uint8_t leak_pin = 16;

bool isLeak = false;

std::array<uint, 8> slice_num;
std::array<uint, 8> channel;

//IMU Values
int16_t acceleration[3], gyro[3], temp;


// Initialise all thrusters to pulse width 1500 microseconds
void initialize_motors() {
    uint8_t motors[] = {vMotor1, vMotor2, vMotor3, vMotor4, hMotor1, hMotor2, hMotor3, hMotor4};

    for (int i = 0; i < 8; i++) {
        gpio_set_function(motors[i], GPIO_FUNC_PWM);
        slice_num[i] = pwm_gpio_to_slice_num(motors[i]);
        channel[i] = pwm_gpio_to_channel(motors[i]);
        pwm_set_clkdiv_int_frac (slice_num[i],  9,9);
        pwm_set_wrap(slice_num[i], 65465);
        pwm_set_chan_level(slice_num[i], channel[i], 19639.5);
        pwm_set_enabled(slice_num[i], true);
    }
    sleep_ms(3000);
}

void set_pw(uint8_t pin, uint16_t duty_us) {
    uint16_t level =(uint16_t)(65465 * ((float)duty_us/5000));
    pwm_set_chan_level(pwm_gpio_to_slice_num(pin), pwm_gpio_to_channel(pin), level);
}

// Basic motor functions
void forward(uint8_t motor, uint8_t thrust) {
    set_pw(motor, 1500 + thrust * 400);
}

void reverse(uint8_t motor, uint8_t thrust) {
    set_pw(motor, 1500 + thrust * 400);
}

void stop(uint8_t motor) {
    set_pw(motor, 1500);
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

static void mpu6050_reset() {
    // Two byte reset. First byte register, second byte data
    // There are a load more options to set up the device in different ways that could be added here
    uint8_t buf[] = {0x6B, 0x80};
    i2c_write_blocking(i2c_default, addr, buf, 2, false);
    sleep_ms(100); // Allow device to reset and stabilize

    // Clear sleep mode (0x6B register, 0x00 value)
    buf[1] = 0x00;  // Clear sleep mode by writing 0x00 to the 0x6B register
    i2c_write_blocking(i2c_default, addr, buf, 2, false); 
    sleep_ms(10); // Allow stabilization after waking up
}

static void mpu6050_read_raw(int16_t accel[3], int16_t gyro[3], int16_t *temp) {
    // For this particular device, we send the device the register we want to read
    // first, then subsequently read from the device. The register is auto incrementing
    // so we don't need to keep sending the register we want, just the first.

    uint8_t buffer[6];

    // Start reading acceleration registers from register 0x3B for 6 bytes
    uint8_t val = 0x3B;
    i2c_write_blocking(i2c_default, addr, &val, 1, true); // true to keep master control of bus
    i2c_read_blocking(i2c_default, addr, buffer, 6, false);

    for (int i = 0; i < 3; i++) {
        accel[i] = (buffer[i * 2] << 8 | buffer[(i * 2) + 1]);
    }

    // Now gyro data from reg 0x43 for 6 bytes
    // The register is auto incrementing on each read
    val = 0x43;
    i2c_write_blocking(i2c_default, addr, &val, 1, true);
    i2c_read_blocking(i2c_default, addr, buffer, 6, false);  // False - finished with bus

    for (int i = 0; i < 3; i++) {
        gyro[i] = (buffer[i * 2] << 8 | buffer[(i * 2) + 1]);;
    }

    // Now temperature from reg 0x41 for 2 bytes
    // The register is auto incrementing on each read
    val = 0x41;
    i2c_write_blocking(i2c_default, addr, &val, 1, true);
    i2c_read_blocking(i2c_default, addr, buffer, 2, false);  // False - finished with bus

    *temp = buffer[0] << 8 | buffer[1];
}


void on_uart_rx() {
    gpio_put(LED_PIN, 0);
    while (uart_is_readable(UART_ID)){
        uint8_t ch = uart_getc(UART_ID);
        printf("Received byte: %d\n", ch);

        if (ch >= 0 && ch <= 17){
            //signal = int_from_uart(UART_ID);
            signal = ch;
            printf("Signal: %d\n", signal);
            //byte_count++;
        }
        if(ch >= 18 && ch <= 118){
            //thrust_gain = int_from_uart(UART_ID) - 18;
            thrust_gain = ch - 18;
            printf("Thrust: %d\n", thrust_gain);
            //byte_count = 0;
        }

        float thrust = thrust_gain / 100.0f;  // Convert back to 0.0-1.0 range

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
            case 17: printf("pH Raw Value: %d\n", read_ph()); break;
            default: break; // Do nothing for unrecognized signals
            //need to add sending sensor data functionality
        }
    }

    
}

void setup_uart() {
    uart_init(UART_ID, BAUDRATE);
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

void setup_i2c() {
    // This example will use I2C0 on the default SDA and SCL pins (4, 5 on a Pico)
    i2c_init(i2c_default, 400 * 1000);
    gpio_set_function(PICO_DEFAULT_I2C_SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(PICO_DEFAULT_I2C_SDA_PIN);
    gpio_pull_up(PICO_DEFAULT_I2C_SCL_PIN);
    // Make the I2C pins available to picotool
    bi_decl(bi_2pins_with_func(PICO_DEFAULT_I2C_SDA_PIN, PICO_DEFAULT_I2C_SCL_PIN, GPIO_FUNC_I2C));

    mpu6050_reset();

}

void print_IMU(){
    mpu6050_read_raw(acceleration, gyro, &temp);
    // These are the raw numbers from the chip, so will need tweaking to be really useful.
    // See the datasheet for more information
    printf("Acc. X = %d, Y = %d, Z = %d\n", acceleration[0], acceleration[1], acceleration[2]);
    printf("Gyro. X = %d, Y = %d, Z = %d\n", gyro[0], gyro[1], gyro[2]);
    // Temperature is simple so use the datasheet calculation to get deg C.
    // Note this is chip temperature.
    printf("Temp. = %f\n", (temp / 340.0) + 36.53);

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

    //initialize_motors();
    gpio_put(LED_PIN, 1);

    initialize_motors();
    
    set_pw(1, 1400);

    sleep_ms(5000);

    set_pw(1, 1500);

    gpio_put(LED_PIN, 0);

    setup_uart();
    setup_i2c();

    while(1){
        tight_loop_contents();
    }
    return 0;
}
