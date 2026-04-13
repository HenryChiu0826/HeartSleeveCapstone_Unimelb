#!/usr/bin/env python3
"""
sensor_interface.py  (Raspberry Pi)
Heart Sleeve — Pressure Sensor Read & Stream

Identical behaviour to the Arduino sensor_interface sketch.
Streams CSV pressure readings to stdout (and optionally a file).

The Pi has no built-in ADC. Set ADC_TYPE in pins.py to match your hardware:
    "ADS1115"  — I2C 16-bit ADC (recommended, higher accuracy)
    "MCP3008"  — SPI 10-bit ADC (cheap and common)

Run:
    python sensor_interface.py             # stream to terminal
    python sensor_interface.py --save      # also save to CSV file

Commands (type while running):
    r      toggle streaming on/off
    i <ms> set sample interval
    q      quit

Output CSV:
    time_ms, s1_raw, s1_kPa, s2_raw, s2_kPa

Dependencies:
    ADS1115: pip install adafruit-circuitpython-ads1x15 adafruit-blinka
    MCP3008: pip install adafruit-mcp3xxx adafruit-blinka
"""

import sys
import time
import signal
import argparse
import threading
import csv
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "..")
from pins import (ADC_TYPE, PRESSURE_CH_1, PRESSURE_CH_2,
                  SENSOR_SUPPLY_V, SENSOR_SCALE, SENSOR_OFFSET, ADC_FULLSCALE,
                  MCP3008_CLK, MCP3008_MISO, MCP3008_MOSI, MCP3008_CS)

# ---- ADC initialisation --------------------------------------------------
def init_adc():
    """Initialise and return an ADC object based on ADC_TYPE in pins.py."""
    if ADC_TYPE == "ADS1115":
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn

        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        ch1 = AnalogIn(ads, getattr(ADS, f"P{PRESSURE_CH_1}"))
        ch2 = AnalogIn(ads, getattr(ADS, f"P{PRESSURE_CH_2}"))

        def read():
            return ch1.value, ch2.value
        return read

    elif ADC_TYPE == "MCP3008":
        import busio
        import digitalio
        import board
        import adafruit_mcp3xxx.mcp3008 as MCP
        from adafruit_mcp3xxx.analog_in import AnalogIn

        spi = busio.SPI(clock=board.SCLK, MISO=board.MISO, MOSI=board.MOSI)
        cs  = digitalio.DigitalInOut(board.CE0)
        mcp = MCP.MCP3008(spi, cs)

        ch1 = AnalogIn(mcp, getattr(MCP, f"P{PRESSURE_CH_1}"))
        ch2 = AnalogIn(mcp, getattr(MCP, f"P{PRESSURE_CH_2}"))

        def read():
            return ch1.value, ch2.value
        return read

    else:
        raise ValueError(f"Unknown ADC_TYPE '{ADC_TYPE}' in pins.py. Use 'ADS1115' or 'MCP3008'.")


def adc_to_kpa(raw: int) -> float:
    voltage = (raw / ADC_FULLSCALE) * SENSOR_SUPPLY_V
    return voltage * SENSOR_SCALE + SENSOR_OFFSET


# ---- Streaming -----------------------------------------------------------
streaming       = False
sample_interval = 0.1    # seconds
start_time      = time.time()


def stream_loop(read_adc, writer=None):
    global streaming, sample_interval

    print("time_ms, s1_raw, s1_kPa, s2_raw, s2_kPa")
    if writer:
        writer.writerow(["time_ms", "s1_raw", "s1_kPa", "s2_raw", "s2_kPa"])

    while True:
        if not streaming:
            time.sleep(0.05)
            continue

        raw1, raw2 = read_adc()
        kpa1 = adc_to_kpa(raw1)
        kpa2 = adc_to_kpa(raw2)
        t_ms = int((time.time() - start_time) * 1000)

        line = f"{t_ms},{raw1},{kpa1:.2f},{raw2},{kpa2:.2f}"
        print(line)

        if writer:
            writer.writerow([t_ms, raw1, f"{kpa1:.2f}", raw2, f"{kpa2:.2f}"])

        time.sleep(sample_interval)


def command_loop():
    global streaming, sample_interval

    print("NOTE: Update SENSOR_SCALE and SENSOR_OFFSET in pins.py before trusting kPa values.")
    print("Commands: r=toggle  i <ms>=interval  q=quit  ?=help")

    while True:
        try:
            raw = input().strip().lower()
        except EOFError:
            break

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0]

        if cmd == "r":
            streaming = not streaming
            print("Streaming ON" if streaming else "Streaming OFF")

        elif cmd == "i":
            if len(parts) >= 2:
                try:
                    ms = float(parts[1])
                    sample_interval = ms / 1000.0
                    print(f"Interval set to {ms:.0f} ms")
                except ValueError:
                    print("Usage: i <ms>")

        elif cmd == "q":
            break

        elif cmd in ("?", "help"):
            print("  r          toggle streaming")
            print("  i <ms>     set sample interval")
            print("  q          quit")


# ---- Entry point ---------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", action="store_true", help="Save output to CSV in ../../tests/data/")
    args = parser.parse_args()

    print(f"Heart Sleeve (RPi) — Sensor Interface  [ADC: {ADC_TYPE}]")

    read_adc = init_adc()

    writer   = None
    csv_file = None

    if args.save:
        data_dir = Path(__file__).parent.parent.parent / "tests" / "data"
        data_dir.mkdir(exist_ok=True)
        ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = data_dir / f"sensor_stream_{ts}.csv"
        csv_file = open(csv_path, "w", newline="")
        writer   = csv.writer(csv_file)
        print(f"Saving to: {csv_path}")

    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))

    # Stream in background thread, commands in main thread
    t = threading.Thread(target=stream_loop, args=(read_adc, writer), daemon=True)
    t.start()

    try:
        command_loop()
    finally:
        streaming = False
        if csv_file:
            csv_file.close()
        print("Goodbye.")


if __name__ == "__main__":
    main()
