# 🫀 Soft Robotic Heart Sleeve — Capstone Project

> A hydraulically actuated soft robotic cardiac assist device, developed as an alternative to traditional ventricular assist devices (VADs).

**Team:** Chaniru Gunasekera · Benjamin Xiang · Henry Chiu  
**Institution:** University of Melbourne  
**Year:** 2026

---

## Overview

This project develops a **soft robotic sleeve** that wraps around the exterior of the heart, assisting contraction through hydraulically actuated silicone actuators. The device does not contact blood, avoids anticoagulation requirements, and mimics the natural biomechanics of the myocardium by combining circumferential compression and helical twisting motions.

The project spans mechanical design, soft actuator fabrication, fluid power systems, embedded control, and sensor integration — validated against a custom cardiac phantom test bed.

---

## Repository Structure

```
heart-sleeve/
│
├── control/                    # Embedded control system
│   ├── simulink/               # MATLAB Simulink models
│   │   ├── open_loop_test.slx
│   │   ├── pressure_pid.slx
│   │   └── cardiac_state_machine.slx
│   ├── arduino/                # Arduino Mega firmware
│   │   ├── valve_control/
│   │   └── sensor_interface/
│   └── README.md
│
├── cad/                        # Mechanical design files
│   ├── actuator_molds/         # 3D-printable molds for silicone casting
│   ├── sleeve_assembly/        # Full sleeve assembly
│   ├── phantom_heart/          # Cardiac phantom geometry
│   └── README.md
│
├── simulation/                 # FEA & CFD models
│   ├── fea/                    # Finite element analysis
│   ├── cfd/                    # Computational fluid dynamics
│   └── README.md
│
├── electronics/                # PCB schematics and wiring
│   ├── schematics/
│   ├── pcb/
│   └── README.md
│
├── docs/                       # Documentation and reports
│   ├── proposal/
│   ├── references/
│   └── figures/
│
└── tests/                      # Experimental data and test scripts
    ├── bench_tests/
    └── data/
```

---

## System Architecture

The device consists of three integrated subsystems:

| Subsystem | Description |
|---|---|
| **Heart Sleeve** | Silicone sleeve with embedded Hydraulic Actuated Muscle (HAM) actuators (circumferential + helical) |
| **Hydraulic Actuation System** | Pump(s), solenoid valves, pressure regulators, and fluid lines |
| **Control System** | Arduino Mega + MATLAB Simulink; closed-loop pressure control with simulated cardiac synchronisation |

### Control System

The control system interfaces an **Arduino Mega 2560** with **MATLAB Simulink** via the Simulink Support Package for Arduino Hardware (External Mode). Key features:

- Closed-loop PID pressure control per actuator channel
- Stateflow cardiac cycle state machine (systole/diastole sequencing)
- ECG or aortic flow rate trigger support
- Real-time data logging via Simulink Scopes and `To Workspace` blocks
- PWM-driven solenoid valve control via MOSFET drivers

---

## Getting Started

### Prerequisites

**Software:**
- MATLAB R2024b or later with Simulink
- Simulink Support Package for Arduino Hardware
- Simulink Desktop Real-Time toolbox
- Arduino IDE (for standalone firmware upload)

**Hardware:**
- Arduino Mega 2560
- Solenoid valves (3/2-way, 12V)
- MOSFET driver board (e.g., IRF520 or similar)
- DC diaphragm pump(s)
- Pressure sensors (e.g., MPXHZ6400 or equivalent, 0–400 kPa range)

## Fabrication

Silicone actuators are cast using **3D-printed PLA molds** (FDM for early prototypes, SLA for final geometry). Final sleeve models are manufactured via SLA silicone printing through FabLab.

Mold files are located in `cad/actuator_molds/`. Fabrication procedures are documented in [`cad/README.md`](cad/README.md).

---

## Testing

The device is validated on a **silicone cardiac phantom** with one or two ventricles, targeting physiological performance metrics:

- Stroke volume (target: ~70 mL)
- Actuation timing accuracy (synchronised to simulated cardiac cycle)
- Pressure response and rise time
- Actuator deformation and fatigue

Bench test scripts and data are in `tests/`.

---

## References

Key literature informing this project:

- Roche, E.T. et al. (2017). *Soft robotic sleeve supports heart function.* Science Translational Medicine, 9(373). [DOI:10.1126/scitranslmed.aaf3925](https://doi.org/10.1126/scitranslmed.aaf3925)
- Weymann, A. et al. (2023). *Artificial Muscles and Soft Robotic Devices for Treatment of End-Stage Heart Failure.* Advanced Materials, 35, 2207390.
- Xavier, M.S. et al. (2022). *Soft Pneumatic Actuators: A Review of Design, Fabrication, Modeling, Sensing, Control and Applications.*

---

## License

This project is developed for academic purposes at the University of Melbourne. All design files, code, and documentation are shared for educational use.

---

## Contact

For questions, open an issue or contact the team via the university project portal.
