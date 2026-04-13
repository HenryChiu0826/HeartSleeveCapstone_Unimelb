# Control System

This directory contains all software for the heart sleeve control system: MATLAB Simulink models and standalone firmware for three supported microcontroller platforms.

## Supported Platforms

| Platform | Folder | Language | Status |
|---|---|---|---|
| Arduino Mega 2560 | `arduino/` | C++ (Arduino) | Primary — Simulink External Mode supported |
| ESP32 | `esp32/` | C++ (Arduino framework) | Alternative — faster CPU, Wi-Fi/BT capable |
| Raspberry Pi | `rpi/` | Python | Alternative — full Linux, easier data logging |

---

## Hardware

### Arduino Mega 2560

| Component | Specification |
|---|---|
| Microcontroller | Arduino Mega 2560 |
| Interface | MATLAB Simulink (External Mode via USB) |
| Pump control | PWM → motor driver (e.g. L298N / IBT-2) |
| Valve control | Digital output → MOSFET → solenoid valve |
| Pressure feedback | Analog input ← pressure sensor (0–400 kPa) |
| ADC | 10-bit (0–1023), 5 V supply |

### ESP32

| Component | Specification |
|---|---|
| Microcontroller | ESP32 (e.g. ESP32 Dev Module) |
| Interface | Arduino IDE / USB serial |
| Pump control | LEDC PWM → motor driver |
| Valve control | Digital output → MOSFET → solenoid valve |
| Pressure feedback | ADC1 only (ADC2 conflicts with Wi-Fi) |
| ADC | 12-bit (0–4095), 3.3 V supply |
| Extras | Wi-Fi, Bluetooth — available for future wireless logging |

> **Note:** ESP32 GPIO is 3.3 V logic. Use a level shifter or relay board when driving 5 V/12 V components.

### Raspberry Pi

| Component | Specification |
|---|---|
| Platform | Raspberry Pi (any model with GPIO header) |
| Interface | Python script via terminal / SSH |
| Pump control | Hardware PWM (GPIO 18) via RPi.GPIO |
| Valve control | GPIO output → MOSFET → solenoid valve |
| Pressure feedback | External ADC required (no built-in ADC on Pi) |
| Recommended ADC | ADS1115 (I2C, 16-bit) or MCP3008 (SPI, 10-bit) |

> **Note:** Raspberry Pi GPIO is 3.3 V logic. Use a level shifter or relay board when driving 5 V/12 V components.

---

## Simulink Models

| File | Description |
|---|---|
| `open_loop_test.slx` | Basic valve/pump toggle — use first to verify hardware wiring |
| `pressure_pid.slx` | Closed-loop PID pressure controller per actuator channel |
| `cardiac_state_machine.slx` | Full system model: Stateflow state machine for cardiac cycle sequencing + PID inner loop |

Simulink External Mode is currently supported with the **Arduino Mega only**. ESP32 and RPi run standalone firmware independently of MATLAB.

### Running in External Mode (Arduino)

1. Open the desired `.slx` file
2. Go to **Model Settings → Hardware Implementation → Hardware board**: `Arduino Mega 2560`
3. Connect Arduino via USB
4. Click **Monitor & Tune** (External Mode) to run the model on the PC while streaming I/O to/from the Arduino in real time
5. Use **Scope** blocks to monitor pressure responses live

### Sensor Scaling

Raw ADC values must be scaled to physical pressure units. Add a `Gain` + `Bias` block after each analog input:

```
pressure_kPa = (ADC_raw / ADC_max) * V_supply * sensor_scale_factor + offset
```

| Platform | ADC_max | V_supply |
|---|---|---|
| Arduino Mega | 1023 | 5.0 V |
| ESP32 | 4095 | 3.3 V |
| Raspberry Pi (ADS1115) | 32767 | 3.3 V |
| Raspberry Pi (MCP3008) | 1023 | 3.3 V |

Refer to your pressure sensor datasheet for `sensor_scale_factor` and `offset`. Update the values in the relevant `pins.h` / `pins.py` file.

---

## Firmware

All three platforms implement the same two sketch/scripts:

| File | Description |
|---|---|
| `valve_control` | Open/close individual solenoid valves and set pump PWM via serial/terminal commands |
| `sensor_interface` | Read and stream pressure sensor data as CSV over serial/terminal |

### Arduino / ESP32

Deployed via Arduino IDE. Each platform folder contains a shared `pins.h` — update pin numbers and sensor scaling constants before uploading.

**ESP32 setup:**
1. Add board URL in Arduino IDE Preferences:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
2. Install **esp32 by Espressif Systems** via Boards Manager
3. Select **Tools → Board → ESP32 Arduino → ESP32 Dev Module**
4. No additional libraries required — all functions are part of the ESP32 Arduino core

### Raspberry Pi

Run Python scripts directly from terminal. Requires external ADC wired via I2C or SPI.

**Dependencies:**
```bash
pip install RPi.GPIO
# ADS1115 (recommended):
pip install adafruit-circuitpython-ads1x15 adafruit-blinka
# MCP3008 (alternative):
pip install adafruit-mcp3xxx adafruit-blinka
```

Set `ADC_TYPE` in `rpi/pins.py` to match your hardware, then run:
```bash
python valve_control/valve_control.py
python sensor_interface/sensor_interface.py --save
```

---

## Pin Assignments

### Arduino Mega

| Function | Pin |
|---|---|
| Valve 1 — Apex circumferential | Digital 22 |
| Valve 2 — Mid circumferential | Digital 23 |
| Valve 3 — Base circumferential | Digital 24 |
| Valve 4 — Apex helical | Digital 25 |
| Valve 5 — Mid helical | Digital 26 |
| Valve 6 — Base helical | Digital 27 |
| Pump PWM | PWM 9 |
| Pressure Sensor 1 | A0 |
| Pressure Sensor 2 | A1 |
| ECG / trigger | A2 |

### ESP32

| Function | Pin (BCM) |
|---|---|
| Valve 1 — Apex circumferential | GPIO 23 |
| Valve 2 — Mid circumferential | GPIO 22 |
| Valve 3 — Base circumferential | GPIO 21 |
| Valve 4 — Apex helical | GPIO 19 |
| Valve 5 — Mid helical | GPIO 18 |
| Valve 6 — Base helical | GPIO 5 |
| Pump PWM (LEDC) | GPIO 16 |
| Pressure Sensor 1 | GPIO 34 (ADC1_CH6) |
| Pressure Sensor 2 | GPIO 35 (ADC1_CH7) |
| ECG / trigger | GPIO 32 (ADC1_CH4) |

### Raspberry Pi

| Function | Pin (BCM) |
|---|---|
| Valve 1 — Apex circumferential | GPIO 17 |
| Valve 2 — Mid circumferential | GPIO 27 |
| Valve 3 — Base circumferential | GPIO 22 |
| Valve 4 — Apex helical | GPIO 10 |
| Valve 5 — Mid helical | GPIO 9 |
| Valve 6 — Base helical | GPIO 11 |
| Pump PWM (hardware) | GPIO 18 |
| Pressure Sensor 1 | ADC channel 0 (external chip) |
| Pressure Sensor 2 | ADC channel 1 (external chip) |

> All pin assignments are defined in each platform's `pins.h` / `pins.py` and can be changed there without editing the main sketch/script.

---

## Control Strategy

The cardiac cycle is modelled as a state machine with the following states:

```
IDLE → SYSTOLE_TRIGGER → APEX_ON → MID_ON → BASE_ON → APEX_OFF → MID_OFF → BASE_OFF → DIASTOLE_HOLD → IDLE
```

Timing parameters T1–T7 (delays between state transitions) are exposed as tunable parameters and can be adjusted live in Simulink External Mode (Arduino) or edited in the script config (ESP32/RPi) without recompiling.

Trigger sources (switchable in the model):
- **Simulated** — internal pulse generator at set BPM (default for bench testing)
- **ECG** — R-wave peak detection from analog input
- **Pressure** — aortic flow rate threshold crossing
