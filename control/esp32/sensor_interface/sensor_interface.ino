/*
 * sensor_interface.ino  (ESP32)
 * Heart Sleeve — Pressure Sensor Read & Stream
 *
 * Identical behaviour to the Arduino Mega version.
 * ESP32 differences:
 *   - 12-bit ADC (0–4095) instead of 10-bit (0–1023)
 *   - 3.3 V supply — update SENSOR_SCALE in pins.h accordingly
 *   - ESP32 ADC is non-linear near rail voltages; consider an op-amp buffer
 *     or use analogReadMilliVolts() for better accuracy (ESP-IDF v4.4+)
 *
 * Serial output (CSV, 115200 baud):
 *   timestamp_ms, sensor1_raw, sensor1_kPa, sensor2_raw, sensor2_kPa
 *
 * Serial commands:
 *   r       — toggle streaming on/off
 *   i <ms>  — set sample interval in ms (default 100)
 *   ?       — print help
 */

#include "../pins.h"

// ---- Config --------------------------------------------------------------
static uint32_t sampleInterval = 100;
static bool     streaming = false;

// ---- Helpers -------------------------------------------------------------
float adcToKpa(int raw) {
    float voltage = (raw / (float)ADC_RESOLUTION) * SENSOR_SUPPLY_V;
    return voltage * SENSOR_SCALE + SENSOR_OFFSET;
}

void printHelp() {
    Serial.println(F("Commands:"));
    Serial.println(F("  r          toggle streaming"));
    Serial.println(F("  i <ms>     set sample interval"));
    Serial.println(F("  ?          help"));
    Serial.println(F("CSV header: time_ms, s1_raw, s1_kPa, s2_raw, s2_kPa"));
}

// ---- Arduino lifecycle ---------------------------------------------------
void setup() {
    Serial.begin(115200);

    // Set ADC attenuation for full 3.3 V range (0–3.3 V → 0–4095)
    analogSetAttenuation(ADC_11db);

    Serial.println(F("Heart Sleeve (ESP32) — Sensor Interface Ready"));
    Serial.println(F("NOTE: Update SENSOR_SCALE and SENSOR_OFFSET in pins.h before trusting kPa values."));
    printHelp();
}

void loop() {
    if (Serial.available()) {
        char cmd = Serial.read();
        switch (cmd) {
            case 'r':
                streaming = !streaming;
                Serial.println(streaming ? F("Streaming ON") : F("Streaming OFF"));
                break;
            case 'i': {
                long interval = Serial.parseInt();
                if (interval > 0) {
                    sampleInterval = (uint32_t)interval;
                    Serial.print(F("Interval set to "));
                    Serial.print(sampleInterval);
                    Serial.println(F(" ms"));
                }
                break;
            }
            case '?':
                printHelp();
                break;
            default:
                break;
        }
    }

    if (!streaming) return;

    static uint32_t lastSample = 0;
    uint32_t now = millis();
    if (now - lastSample < sampleInterval) return;
    lastSample = now;

    int raw1 = analogRead(PRESSURE_SENSOR_1);
    int raw2 = analogRead(PRESSURE_SENSOR_2);

    float kpa1 = adcToKpa(raw1);
    float kpa2 = adcToKpa(raw2);

    Serial.print(now);   Serial.print(',');
    Serial.print(raw1);  Serial.print(',');
    Serial.print(kpa1, 2); Serial.print(',');
    Serial.print(raw2);  Serial.print(',');
    Serial.println(kpa2, 2);
}
