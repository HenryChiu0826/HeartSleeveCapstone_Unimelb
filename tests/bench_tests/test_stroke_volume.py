"""
test_stroke_volume.py
Heart Sleeve — Test 4: Stroke Volume on Cardiac Phantom

Goal:
    Measure the volume of fluid displaced per cardiac cycle when the sleeve
    is fitted on the silicone phantom. Target stroke volume is ~70 mL.

    Volume can be estimated by:
      a) Measuring fluid displacement in a graduated cylinder (manual)
      b) Integrating flow rate from a flow sensor (if available)
      c) Correlating actuator pressure × stroke from FEA/calibration curve

    This script supports method (b) if a flow sensor is wired to an analog
    input. For method (a), it provides a manual data entry template.

Pass criteria:
    TODO: fill in from design spec
    - Stroke volume: 70 ± X mL
    - Ejection fraction proxy: > X %
    - Repeatability (std dev across N cycles): < X mL

Usage:
    python test_stroke_volume.py
"""

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from serial_capture import open_serial, send_cmd, capture, save_csv, DEFAULT_PORT

# ---- Config --------------------------------------------------------------
PORT             = DEFAULT_PORT
CAPTURE_SECONDS  = 20        # record across multiple cycles
CYCLES_TO_RUN    = 5         # how many cycles to average over

# Flow sensor config — TODO: set if using a flow sensor
FLOW_SENSOR_PIN  = None      # e.g. "s2_kPa" column if remapped to flow sensor
FLOW_SCALE       = None      # mL/s per kPa — calibrate from sensor datasheet

# Manual measurement template — fill in during testing
MANUAL_MEASUREMENTS = {
    # "trial_1": None,   # mL — TODO: measure from graduated cylinder
    # "trial_2": None,
    # "trial_3": None,
    # "trial_4": None,
    # "trial_5": None,
}

# Target
STROKE_VOLUME_TARGET_ML = 70.0
STROKE_VOLUME_TOL_ML    = 10.0  # TODO: tighten once baseline is established


def compute_stroke_volume_from_flow(df: pd.DataFrame) -> float:
    """
    Integrate flow rate over one systole phase to get stroke volume.
    Requires FLOW_SENSOR_PIN and FLOW_SCALE to be set.
    TODO: implement once flow sensor is wired.
    """
    if FLOW_SENSOR_PIN is None or FLOW_SCALE is None:
        return None

    # Placeholder integration
    flow_mLs = df[FLOW_SENSOR_PIN] * FLOW_SCALE          # convert to mL/s
    dt_s     = df["time_ms"].diff().fillna(0) / 1000.0   # ms → s
    # TODO: mask to systole phase only (positive flow)
    volume_mL = float((flow_mLs * dt_s).sum())
    return volume_mL


def analyse_manual():
    """Summarise manually entered stroke volume measurements."""
    values = [v for v in MANUAL_MEASUREMENTS.values() if v is not None]
    if not values:
        print("No manual measurements recorded yet.")
        return

    arr = np.array(values)
    print(f"\n--- Stroke Volume (manual) ---")
    print(f"  N trials:  {len(arr)}")
    print(f"  Mean:      {arr.mean():.1f} mL")
    print(f"  Std dev:   {arr.std():.1f} mL")
    print(f"  Min/Max:   {arr.min():.1f} / {arr.max():.1f} mL")
    print(f"  Target:    {STROKE_VOLUME_TARGET_ML} ± {STROKE_VOLUME_TOL_ML} mL")

    passed = abs(arr.mean() - STROKE_VOLUME_TARGET_ML) <= STROKE_VOLUME_TOL_ML
    print(f"  Result:    {'PASS' if passed else 'FAIL'}")

    plt.figure()
    plt.bar(range(1, len(arr)+1), arr, color="steelblue")
    plt.axhline(STROKE_VOLUME_TARGET_ML, color="r", linestyle="--", label="Target")
    plt.axhspan(
        STROKE_VOLUME_TARGET_ML - STROKE_VOLUME_TOL_ML,
        STROKE_VOLUME_TARGET_ML + STROKE_VOLUME_TOL_ML,
        alpha=0.15, color="green", label="Tolerance band"
    )
    plt.xlabel("Trial")
    plt.ylabel("Stroke Volume (mL)")
    plt.title("Stroke Volume — Manual Measurements")
    plt.legend()
    plt.tight_layout()
    plt.show()


def run_test(ser):
    print("=" * 50)
    print("TEST 4 — Stroke Volume on Phantom")
    print("=" * 50)

    if MANUAL_MEASUREMENTS:
        analyse_manual()
        return

    if FLOW_SENSOR_PIN is None:
        print("No flow sensor configured and no manual measurements entered.")
        print("Fill in MANUAL_MEASUREMENTS dict at the top of this file after")
        print("measuring displaced volume from the graduated cylinder.")
        return

    print(f"Recording {CAPTURE_SECONDS}s of flow sensor data...")
    input("Start cardiac cycle and press Enter...\n")

    df = capture(ser, CAPTURE_SECONDS, label="stroke_volume")
    save_csv(df, "stroke_volume")

    sv = compute_stroke_volume_from_flow(df)
    if sv is not None:
        print(f"\nEstimated stroke volume: {sv:.1f} mL  (target: {STROKE_VOLUME_TARGET_ML} mL)")
        passed = abs(sv - STROKE_VOLUME_TARGET_ML) <= STROKE_VOLUME_TOL_ML
        print(f"Result: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    # Manual mode: just analyse entered measurements without opening serial
    if MANUAL_MEASUREMENTS and all(v is not None for v in MANUAL_MEASUREMENTS.values()):
        analyse_manual()
    else:
        ser = open_serial(PORT)
        try:
            run_test(ser)
        finally:
            ser.close()
