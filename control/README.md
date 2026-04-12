# Control System

This directory contains all software for the heart sleeve control system, split between MATLAB Simulink models and Arduino firmware.

## Hardware

| Component | Specification |
|---|---|
| Microcontroller | Arduino Mega 2560 |
| Interface | MATLAB Simulink (External Mode via USB) |
| Pump control | PWM → motor driver (e.g. L298N / IBT-2) |
| Valve control | Digital output → MOSFET → solenoid valve |
| Pressure feedback | Analog input ← pressure sensor (0–400 kPa) |

## Simulink Models

| File | Description |
|---|---|
| `open_loop_test.slx` | Basic valve/pump toggle — use first to verify hardware wiring |
| `pressure_pid.slx` | Closed-loop PID pressure controller per actuator channel |
| `cardiac_state_machine.slx` | Full system model: Stateflow state machine for cardiac cycle sequencing + PID inner loop |

### Running in External Mode

1. Open the desired `.slx` file
2. Go to **Model Settings → Hardware Implementation → Hardware board**: `Arduino Mega 2560`
3. Connect Arduino via USB
4. Click **Monitor & Tune** (External Mode) to run the model on the PC while streaming I/O to/from the Arduino in real time
5. Use **Scope** blocks to monitor pressure responses live

### Sensor Scaling

Raw ADC values (0–1023) from the Arduino Analog Input block must be scaled to physical pressure units. Add a `Gain` + `Bias` block after each analog input:

```
pressure_kPa = (ADC_raw / 1023) * V_supply * sensor_scale_factor + offset
```

Refer to your pressure sensor datasheet for `sensor_scale_factor` and `offset`.

## Arduino Firmware

Standalone firmware (for operation without MATLAB) is in `arduino/`. These sketches are deployed directly to the Arduino Mega via Arduino IDE.

| Sketch | Description |
|---|---|
| `valve_control/` | Open/close solenoid valves by serial command |
| `sensor_interface/` | Read and stream pressure sensor data over serial |

## Pin Assignments (Default)

| Function | Arduino Pin |
|---|---|
| Valve 1 (Apical circumferential) | Digital 22 |
| Valve 2 (Middle circumferential) | Digital 23 |
| Valve 3 (Basal circumferential) | Digital 24 |
| Valve 4 (Apical helical) | Digital 25 |
| Valve 5 (Middle helical) | Digital 26 |
| Valve 6 (Basal helical) | Digital 27 |
| Pump PWM | PWM 9 |
| Pressure Sensor 1 | Analog A0 |
| Pressure Sensor 2 | Analog A1 |
| ECG / trigger input | Analog A2 |

> Pin assignments can be changed in `cardiac_state_machine.slx` under the Hardware I/O block parameters.

## Control Strategy

The cardiac cycle is modelled as a state machine with the following states:

```
IDLE → SYSTOLE_TRIGGER → APEX_ON → MID_ON → BASE_ON → APEX_OFF → MID_OFF → BASE_OFF → DIASTOLE_HOLD → IDLE
```

Timing parameters T1–T7 (delays between state transitions) are exposed as tunable parameters and can be adjusted live in External Mode without recompiling.

Trigger sources (switchable in the model):
- **Simulated** — internal pulse generator at set BPM (default for bench testing)
- **ECG** — R-wave peak detection from analog input
- **Pressure** — aortic flow rate threshold crossing
