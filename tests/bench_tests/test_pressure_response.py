"""
test_pressure_response.py
Heart Sleeve — Test 2: Pressure Step Response

Goal:
    Characterise how quickly the system can build and release pressure in a
    single actuator channel. Used to tune PID gains and set timing parameters
    for the cardiac state machine.

    Records pressure vs. time during:
        1. Pressure build  (pump on, valve open → target pressure)
        2. Pressure hold   (valve closed, pump off)
        3. Pressure release (exhaust valve open)

Arduino sketch required: sensor_interface.ino (for logging)
                         valve_control.ino   (for actuation)
    NOTE: You need both sketches' behaviour. Either run two Arduinos,
    or implement a combined sketch once basic tests pass.

Pass criteria:
    TODO: fill in from design requirements, e.g.
    - Rise time (10%→90%): < X ms
    - Steady-state error: < X kPa
    - Overshoot: < X %
    - Release time: < X ms

Usage:
    python test_pressure_response.py
"""

import time
import matplotlib.pyplot as plt
import pandas as pd
from serial_capture import open_serial, send_cmd, capture, save_csv, DEFAULT_PORT

# ---- Config --------------------------------------------------------------
PORT            = DEFAULT_PORT
SENSOR_CHANNEL  = "s1_kPa"      # which sensor column to analyse

TARGET_PRESSURE = 50.0           # TODO: set target kPa for your actuator
PUMP_DUTY       = 180            # TODO: tune pump PWM (0-255)
BUILD_DURATION  = 3.0            # seconds to record pressure build
HOLD_DURATION   = 2.0            # seconds to hold
RELEASE_DURATION = 2.0           # seconds to record release

# Pass/fail thresholds — TODO: fill in from design spec
RISE_TIME_MAX_MS   = None   # e.g. 500
OVERSHOOT_MAX_PCT  = None   # e.g. 10
RELEASE_TIME_MAX_MS = None  # e.g. 300


def analyse(df: pd.DataFrame, phase: str) -> dict:
    """Basic step-response metrics on a single pressure column."""
    p = df[SENSOR_CHANNEL].values
    t = df["time_ms"].values

    result = {
        "phase":    phase,
        "n_samples": len(p),
        "p_min":    float(p.min()),
        "p_max":    float(p.max()),
        "p_final":  float(p[-1]) if len(p) else None,
    }

    # TODO: compute rise time, overshoot, settling time once calibration is done
    # Example skeleton:
    # p_start = p[0]
    # p_end   = p[-1]
    # threshold_10 = p_start + 0.10 * (p_end - p_start)
    # threshold_90 = p_start + 0.90 * (p_end - p_start)
    # idx_10 = next((i for i, v in enumerate(p) if v >= threshold_10), None)
    # idx_90 = next((i for i, v in enumerate(p) if v >= threshold_90), None)
    # if idx_10 is not None and idx_90 is not None:
    #     result["rise_time_ms"] = t[idx_90] - t[idx_10]

    return result


def run_test(ser):
    print("=" * 50)
    print("TEST 2 — Pressure Step Response")
    print("=" * 50)
    input("Ensure system is connected and a single valve channel is plumbed. Press Enter...\n")

    # --- Phase 1: pressure build ---
    print("Phase 1: Building pressure...")
    send_cmd(ser, f"p {PUMP_DUTY}")
    send_cmd(ser, "o 1")
    df_build = capture(ser, BUILD_DURATION, label="build")
    send_cmd(ser, "c 1")
    send_cmd(ser, "p 0")

    # --- Phase 2: hold ---
    print("Phase 2: Holding...")
    df_hold = capture(ser, HOLD_DURATION, label="hold")

    # --- Phase 3: release ---
    print("Phase 3: Releasing pressure...")
    send_cmd(ser, "o 1")  # open to atmosphere / exhaust
    df_release = capture(ser, RELEASE_DURATION, label="release")
    send_cmd(ser, "x")

    # --- Combine & save ---
    df_all = pd.concat([df_build, df_hold, df_release], ignore_index=True)
    save_csv(df_all, "pressure_step")

    # --- Analyse ---
    for phase_df, name in [(df_build, "build"), (df_hold, "hold"), (df_release, "release")]:
        if phase_df.empty:
            print(f"  {name}: no data captured")
            continue
        metrics = analyse(phase_df, name)
        print(f"\n  {name.upper()}")
        for k, v in metrics.items():
            print(f"    {k}: {v}")

    # --- Plot ---
    if not df_all.empty:
        plt.figure(figsize=(10, 4))
        plt.plot(df_all["time_ms"], df_all[SENSOR_CHANNEL])
        plt.axhline(TARGET_PRESSURE, color="r", linestyle="--", label=f"Target {TARGET_PRESSURE} kPa")
        plt.xlabel("Time (ms)")
        plt.ylabel("Pressure (kPa)")
        plt.title("Pressure Step Response")
        plt.legend()
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    ser = open_serial(PORT)
    try:
        run_test(ser)
    finally:
        send_cmd(ser, "x")
        ser.close()
