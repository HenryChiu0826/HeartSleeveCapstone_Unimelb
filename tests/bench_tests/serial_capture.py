"""
serial_capture.py
Heart Sleeve — Serial capture utility

Shared helper used by all bench test scripts.
Opens a serial connection to the Arduino and provides:
  - send_cmd()   : send a text command and optionally wait for a response line
  - capture()    : stream CSV lines from sensor_interface into a DataFrame
  - save_csv()   : write captured data to tests/data/

Dependencies:
    pip install pyserial pandas
"""

import time
import csv
import serial
import serial.tools.list_ports
import pandas as pd
from pathlib import Path
from datetime import datetime

# ---- Config (edit these to match your machine) ---------------------------
DEFAULT_PORT     = "COM3"     # TODO: update to your Arduino's COM port
DEFAULT_BAUDRATE = 115200
DEFAULT_TIMEOUT  = 2          # seconds

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def list_ports():
    """Print available serial ports — run this if unsure of your COM port."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    for p in ports:
        print(f"  {p.device:10s}  {p.description}")


def open_serial(port=DEFAULT_PORT, baudrate=DEFAULT_BAUDRATE, timeout=DEFAULT_TIMEOUT):
    """Open and return a serial connection. Waits for Arduino reset."""
    ser = serial.Serial(port, baudrate, timeout=timeout)
    time.sleep(2)  # Arduino resets on serial open; wait for it to be ready
    ser.reset_input_buffer()
    return ser


def send_cmd(ser: serial.Serial, cmd: str, wait_for: str = None, timeout: float = 2.0):
    """
    Send a command string and optionally block until a response line
    containing `wait_for` is received (or timeout expires).
    Returns the matched response line, or None on timeout.
    """
    ser.write((cmd + "\n").encode())
    if wait_for is None:
        return None

    deadline = time.time() + timeout
    while time.time() < deadline:
        line = ser.readline().decode(errors="replace").strip()
        if line and wait_for.lower() in line.lower():
            return line
    return None


def capture(ser: serial.Serial, duration: float, label: str = "") -> pd.DataFrame:
    """
    Capture CSV lines from sensor_interface for `duration` seconds.
    Expected format: time_ms, s1_raw, s1_kPa, s2_raw, s2_kPa

    Returns a DataFrame with columns:
        time_ms, s1_raw, s1_kPa, s2_raw, s2_kPa
    """
    columns = ["time_ms", "s1_raw", "s1_kPa", "s2_raw", "s2_kPa"]
    rows = []

    send_cmd(ser, "r")  # start streaming
    deadline = time.time() + duration

    while time.time() < deadline:
        line = ser.readline().decode(errors="replace").strip()
        if not line or line.startswith("Stream") or "," not in line:
            continue
        parts = line.split(",")
        if len(parts) != 5:
            continue
        try:
            rows.append([float(p) for p in parts])
        except ValueError:
            continue

    send_cmd(ser, "r")  # stop streaming

    df = pd.DataFrame(rows, columns=columns)
    if label:
        df["label"] = label
    return df


def save_csv(df: pd.DataFrame, name: str) -> Path:
    """Save DataFrame to tests/data/<name>_<timestamp>.csv"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = DATA_DIR / f"{name}_{timestamp}.csv"
    df.to_csv(path, index=False)
    print(f"Saved: {path}")
    return path
