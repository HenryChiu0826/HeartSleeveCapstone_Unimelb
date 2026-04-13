// pins.h — shared pin assignments for all Heart Sleeve sketches
// Match these to your physical wiring before uploading.

#ifndef PINS_H
#define PINS_H

// --- Solenoid Valves (active HIGH = open) ---
#define VALVE_APEX_CIRC     22   // Apical circumferential
#define VALVE_MID_CIRC      23   // Middle circumferential
#define VALVE_BASE_CIRC     24   // Basal circumferential
#define VALVE_APEX_HEL      25   // Apical helical
#define VALVE_MID_HEL       26   // Middle helical
#define VALVE_BASE_HEL      27   // Basal helical

#define NUM_VALVES          6
const uint8_t VALVE_PINS[NUM_VALVES] = {
    VALVE_APEX_CIRC, VALVE_MID_CIRC, VALVE_BASE_CIRC,
    VALVE_APEX_HEL,  VALVE_MID_HEL,  VALVE_BASE_HEL
};

// --- Pump ---
#define PUMP_PWM_PIN        9    // PWM output to motor driver

// --- Pressure Sensors (0–400 kPa, scaled from 0–5 V / 0–1023 ADC) ---
#define PRESSURE_SENSOR_1   A0
#define PRESSURE_SENSOR_2   A1

// --- Trigger / ECG ---
#define ECG_TRIGGER_PIN     A2

// --- Sensor scaling (update from datasheet) ---
#define SENSOR_SUPPLY_V     5.0f
#define SENSOR_SCALE        80.0f   // kPa per volt — PLACEHOLDER
#define SENSOR_OFFSET       0.0f    // kPa offset   — PLACEHOLDER

#endif // PINS_H
