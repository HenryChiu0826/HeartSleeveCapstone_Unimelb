/*
 * valve_control.ino
 * Heart Sleeve — Valve & Pump Initial Test
 *
 * Purpose: Manually open/close individual solenoid valves and set pump speed
 *          via Serial commands. Use this first to verify hardware wiring before
 *          running any closed-loop control.
 *
 * Serial commands (115200 baud):
 *   o <n>   — open valve n   (1–6)
 *   c <n>   — close valve n  (1–6)
 *   a       — open all valves
 *   x       — close all valves
 *   p <0-255> — set pump PWM duty cycle
 *   s       — print current valve states + pump duty
 *   ?       — print this help
 */

#include "../pins.h"

// ---- State ---------------------------------------------------------------
static uint8_t pumpDuty = 0;
static bool    valveState[NUM_VALVES] = {false};

// ---- Helpers -------------------------------------------------------------
void setValve(uint8_t index, bool open) {
    if (index >= NUM_VALVES) return;
    valveState[index] = open;
    digitalWrite(VALVE_PINS[index], open ? HIGH : LOW);
}

void allValves(bool open) {
    for (uint8_t i = 0; i < NUM_VALVES; i++) setValve(i, open);
}

void setPump(uint8_t duty) {
    pumpDuty = duty;
    analogWrite(PUMP_PWM_PIN, duty);
}

void printStatus() {
    Serial.println(F("--- Status ---"));
    const char* names[NUM_VALVES] = {
        "Apex-Circ", "Mid-Circ ", "Base-Circ",
        "Apex-Hel ", "Mid-Hel  ", "Base-Hel "
    };
    for (uint8_t i = 0; i < NUM_VALVES; i++) {
        Serial.print(F("  Valve "));
        Serial.print(i + 1);
        Serial.print(F(" ("));
        Serial.print(names[i]);
        Serial.print(F("): "));
        Serial.println(valveState[i] ? F("OPEN") : F("CLOSED"));
    }
    Serial.print(F("  Pump PWM: "));
    Serial.println(pumpDuty);
}

void printHelp() {
    Serial.println(F("Commands:"));
    Serial.println(F("  o <1-6>    open valve"));
    Serial.println(F("  c <1-6>    close valve"));
    Serial.println(F("  a          open all valves"));
    Serial.println(F("  x          close all valves"));
    Serial.println(F("  p <0-255>  set pump duty"));
    Serial.println(F("  s          status"));
    Serial.println(F("  ?          help"));
}

// ---- Arduino lifecycle ---------------------------------------------------
void setup() {
    Serial.begin(115200);

    // Init valve pins
    for (uint8_t i = 0; i < NUM_VALVES; i++) {
        pinMode(VALVE_PINS[i], OUTPUT);
        digitalWrite(VALVE_PINS[i], LOW);  // all closed on startup
    }

    // Init pump pin
    pinMode(PUMP_PWM_PIN, OUTPUT);
    analogWrite(PUMP_PWM_PIN, 0);

    Serial.println(F("Heart Sleeve — Valve Control Ready"));
    printHelp();
}

void loop() {
    if (!Serial.available()) return;

    char cmd = Serial.read();

    switch (cmd) {
        case 'o': {
            int n = Serial.parseInt();
            if (n >= 1 && n <= NUM_VALVES) {
                setValve(n - 1, true);
                Serial.print(F("Opened valve ")); Serial.println(n);
            } else {
                Serial.println(F("Invalid valve number (1-6)"));
            }
            break;
        }
        case 'c': {
            int n = Serial.parseInt();
            if (n >= 1 && n <= NUM_VALVES) {
                setValve(n - 1, false);
                Serial.print(F("Closed valve ")); Serial.println(n);
            } else {
                Serial.println(F("Invalid valve number (1-6)"));
            }
            break;
        }
        case 'a':
            allValves(true);
            Serial.println(F("All valves OPEN"));
            break;
        case 'x':
            allValves(false);
            setPump(0);
            Serial.println(F("All valves CLOSED, pump OFF"));
            break;
        case 'p': {
            int duty = Serial.parseInt();
            duty = constrain(duty, 0, 255);
            setPump((uint8_t)duty);
            Serial.print(F("Pump duty set to ")); Serial.println(duty);
            break;
        }
        case 's':
            printStatus();
            break;
        case '?':
            printHelp();
            break;
        default:
            break;  // ignore whitespace / newlines
    }
}
