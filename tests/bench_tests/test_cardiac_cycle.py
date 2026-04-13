"""
test_cardiac_cycle.py
Heart Sleeve — Test 3: Cardiac Cycle Timing

Goal:
    Verify the full actuation sequence (apex → mid → base, circumferential
    then helical) fires in the correct order and within timing tolerances.
    Run against the cardiac_state_machine Simulink model in External Mode,
    or a standalone Arduino sketch implementing the same sequence.

    This script:
      - Records pressure on both sensors throughout one or more cardiac cycles
      - Detects actuation events from pressure rise/fall edges
      - Checks the sequence order and inter-event timing against targets

Pass criteria:
    TODO: fill in from design spec, e.g.
    - Correct valve sequence order
    - Systole duration: X ± Y ms  (target: ~300 ms at 60 BPM)
    - Diastole duration: X ± Y ms (target: ~700 ms at 60 BPM)
    - Apex-to-base propagation delay: X ms

Usage:
    python test_cardiac_cycle.py
    (Start the Simulink cardiac_state_machine model in External Mode first,
     OR run a standalone Arduino cycle sketch — see TODO below.)
"""

import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from serial_capture import open_serial, send_cmd, capture, save_csv, DEFAULT_PORT

# ---- Config --------------------------------------------------------------
PORT            = DEFAULT_PORT
CAPTURE_SECONDS = 10       # how long to record (covers several cycles)
BPM_TARGET      = 60       # expected heart rate
PRESSURE_THRESH = 5.0      # kPa above baseline to count as "actuated"

# TODO: once Simulink model is running, the Arduino is driven externally.
# This script just observes via sensor_interface.
# If using standalone Arduino cycle sketch, send a start command here instead.
START_CMD = None  # e.g. "start" — set once standalone sketch is ready


def detect_events(df: pd.DataFrame, col: str, threshold: float):
    """
    Detect rising and falling edges in a pressure trace.
    Returns list of dicts: {type: 'rise'|'fall', time_ms: float}
    """
    p = df[col].values
    t = df["time_ms"].values
    baseline = float(np.median(p[:10])) if len(p) >= 10 else float(p[0])

    events = []
    above = p[0] > (baseline + threshold)

    for i in range(1, len(p)):
        now_above = p[i] > (baseline + threshold)
        if now_above and not above:
            events.append({"type": "rise", "time_ms": float(t[i]), "pressure_kPa": float(p[i])})
        elif not now_above and above:
            events.append({"type": "fall", "time_ms": float(t[i]), "pressure_kPa": float(p[i])})
        above = now_above

    return events


def check_timing(events: list, bpm_target: float) -> dict:
    """
    Extract cycle timing from detected events.
    TODO: extend once the full 6-valve sequence is instrumented.
    Currently measures time between consecutive rise events as cycle period.
    """
    rises = [e for e in events if e["type"] == "rise"]
    if len(rises) < 2:
        return {"cycles_detected": len(rises), "period_ms": None, "bpm_measured": None}

    periods = [rises[i+1]["time_ms"] - rises[i]["time_ms"] for i in range(len(rises)-1)]
    mean_period = float(np.mean(periods))
    bpm_measured = 60000.0 / mean_period if mean_period > 0 else None

    return {
        "cycles_detected": len(rises),
        "period_ms":       round(mean_period, 1),
        "bpm_measured":    round(bpm_measured, 1) if bpm_measured else None,
        "bpm_target":      bpm_target,
        "bpm_error_pct":   round(abs(bpm_measured - bpm_target) / bpm_target * 100, 1)
                           if bpm_measured else None,
    }


def run_test(ser):
    print("=" * 50)
    print("TEST 3 — Cardiac Cycle Timing")
    print("=" * 50)
    print(f"Recording {CAPTURE_SECONDS}s of pressure data.")
    print("Start the Simulink cardiac_state_machine model (External Mode) now,")
    print("or start your standalone Arduino cycle sketch.")
    input("Press Enter when the cycle is running...\n")

    if START_CMD:
        send_cmd(ser, START_CMD)

    df = capture(ser, CAPTURE_SECONDS, label="cardiac_cycle")
    save_csv(df, "cardiac_cycle")

    if df.empty:
        print("No data captured. Check sensor_interface is streaming.")
        return

    # Detect events on sensor 1 (primary)
    events = detect_events(df, "s1_kPa", PRESSURE_THRESH)
    print(f"\nDetected {len(events)} pressure events on sensor 1:")
    for e in events:
        print(f"  {e['type']:5s}  t={e['time_ms']:.0f} ms  p={e['pressure_kPa']:.1f} kPa")

    # Timing analysis
    timing = check_timing(events, BPM_TARGET)
    print("\n--- Timing ---")
    for k, v in timing.items():
        print(f"  {k}: {v}")

    # TODO: add pass/fail against RISE_TIME_MAX_MS etc. once thresholds are set

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    for ax, col, label in zip(axes, ["s1_kPa", "s2_kPa"], ["Sensor 1", "Sensor 2"]):
        ax.plot(df["time_ms"], df[col], linewidth=0.8)
        ax.set_ylabel("Pressure (kPa)")
        ax.set_title(label)
        ax.grid(True, alpha=0.4)

    axes[-1].set_xlabel("Time (ms)")
    plt.suptitle("Cardiac Cycle Pressure Trace")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    ser = open_serial(PORT)
    try:
        run_test(ser)
    finally:
        ser.close()
