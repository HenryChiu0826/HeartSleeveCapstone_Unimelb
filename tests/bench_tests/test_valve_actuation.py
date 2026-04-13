"""
test_valve_actuation.py
Heart Sleeve — Test 1: Valve Actuation Verification

Goal:
    Confirm each of the 6 solenoid valves opens and closes correctly.
    Check for audible click, pressure change (if system is pressurised),
    and that no cross-talk occurs between channels.

Arduino sketch required: valve_control.ino

Pass criteria:
    TODO: define once hardware is available, e.g.
    - Audible/tactile click on each valve actuation
    - Pressure rise > X kPa within Y ms of opening (if pressurised)
    - No unintended valve actuation on adjacent channels

Usage:
    python test_valve_actuation.py
"""

import time
import serial
from serial_capture import open_serial, send_cmd, DEFAULT_PORT

# ---- Config --------------------------------------------------------------
PORT            = DEFAULT_PORT
VALVE_OPEN_MS   = 500    # how long to hold each valve open during test
VALVE_COUNT     = 6

VALVE_NAMES = [
    "Apex Circumferential",
    "Mid  Circumferential",
    "Base Circumferential",
    "Apex Helical",
    "Mid  Helical",
    "Base Helical",
]

# ---- Results template (fill in during testing) ---------------------------
# Each entry: (valve_number, clicked, pressure_response_kPa, notes)
RESULTS = [
    # (1, None, None, ""),   # TODO: fill in after testing
    # (2, None, None, ""),
    # (3, None, None, ""),
    # (4, None, None, ""),
    # (5, None, None, ""),
    # (6, None, None, ""),
]


def run_test(ser: serial.Serial):
    print("=" * 50)
    print("TEST 1 — Valve Actuation")
    print("=" * 50)
    print("Ensure system is in a safe state (low/no pressure) before starting.")
    input("Press Enter to begin...\n")

    for i in range(1, VALVE_COUNT + 1):
        print(f"\nValve {i}: {VALVE_NAMES[i-1]}")
        print(f"  Opening valve {i}...")
        send_cmd(ser, f"o {i}")
        time.sleep(VALVE_OPEN_MS / 1000)

        # TODO: read pressure sensor here if pressurised
        # e.g. capture a short burst and check for pressure rise

        print(f"  Closing valve {i}...")
        send_cmd(ser, f"c {i}")
        time.sleep(0.2)

        result = input("  Did valve actuate? (y/n/s=skip): ").strip().lower()
        notes  = input("  Notes (press Enter to skip): ").strip()
        RESULTS.append((i, result == "y", None, notes))

    # Safety: close everything
    send_cmd(ser, "x")

    print("\n--- Summary ---")
    all_pass = True
    for valve_num, clicked, pressure, notes in RESULTS:
        status = "PASS" if clicked else "FAIL"
        if not clicked:
            all_pass = False
        print(f"  Valve {valve_num} ({VALVE_NAMES[valve_num-1]}): {status}  {notes}")

    print(f"\nOverall: {'PASS' if all_pass else 'FAIL'}")
    return all_pass


if __name__ == "__main__":
    ser = open_serial(PORT)
    try:
        run_test(ser)
    finally:
        send_cmd(ser, "x")  # always close all valves on exit
        ser.close()
