// pins.h — ESP32 pin assignments for Heart Sleeve sketches
// Programmed via Arduino IDE with the ESP32 board package.
//
// Key differences from Arduino Mega:
//   - ADC is 12-bit (0–4095) instead of 10-bit (0–1023)
//   - PWM uses the LEDC peripheral (ledcWrite) instead of analogWrite
//   - Not all pins support ADC or PWM — check your specific ESP32 variant
//   - Avoid GPIO 6–11 (connected to internal flash)

#ifndef PINS_H
#define PINS_H

// --- Solenoid Valves (active HIGH = open) ---
#define VALVE_APEX_CIRC     23
#define VALVE_MID_CIRC      22
#define VALVE_BASE_CIRC     21
#define VALVE_APEX_HEL      19
#define VALVE_MID_HEL       18
#define VALVE_BASE_HEL       5

#define NUM_VALVES 6
const uint8_t VALVE_PINS[NUM_VALVES] = {
    VALVE_APEX_CIRC, VALVE_MID_CIRC, VALVE_BASE_CIRC,
    VALVE_APEX_HEL,  VALVE_MID_HEL,  VALVE_BASE_HEL
};

// --- Pump (LEDC PWM) ---
#define PUMP_PWM_PIN        16
#define PUMP_LEDC_CHANNEL    0
#define PUMP_LEDC_FREQ_HZ  5000
#define PUMP_LEDC_BITS       8    // 8-bit duty: 0–255

// --- Pressure Sensors ---
// ESP32 ADC1 channels only (ADC2 conflicts with Wi-Fi)
#define PRESSURE_SENSOR_1   34   // ADC1_CH6 — input only, no pull
#define PRESSURE_SENSOR_2   35   // ADC1_CH7 — input only, no pull

// --- Trigger / ECG ---
#define ECG_TRIGGER_PIN     32   // ADC1_CH4

// --- ADC config ---
#define ADC_RESOLUTION      4095   // 12-bit
#define SENSOR_SUPPLY_V     3.3f   // ESP32 runs at 3.3 V
#define SENSOR_SCALE        60.6f  // kPa per volt — PLACEHOLDER (recalculate for 3.3 V supply)
#define SENSOR_OFFSET       0.0f   // kPa offset   — PLACEHOLDER

#endif // PINS_H
