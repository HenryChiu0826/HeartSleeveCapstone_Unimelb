#!/usr/bin/env python3
"""
valve_control.py  (Raspberry Pi)
Heart Sleeve — Valve & Pump Initial Test

Identical behaviour to the Arduino valve_control sketch.
Run from terminal:
    python valve_control.py

Commands:
    o <1-6>    open valve
    c <1-6>    close valve
    a          open all valves
    x          close all valves, pump off
    p <0-100>  set pump duty cycle (%)
    s          print status
    ?          print help
    q          quit (closes all valves first)

Dependencies:
    pip install RPi.GPIO
"""

import sys
import signal
sys.path.insert(0, "..")   # allow: from pins import ...

import RPi.GPIO as GPIO
from pins import VALVE_PINS, VALVE_NAMES, NUM_VALVES if False else None, \
                 PUMP_PWM_PIN, PUMP_PWM_FREQ

# RPi.GPIO doesn't export NUM_VALVES — use len
from pins import VALVE_PINS, VALVE_NAMES, PUMP_PWM_PIN, PUMP_PWM_FREQ

NUM_VALVES = len(VALVE_PINS)

# ---- State ---------------------------------------------------------------
valve_state = [False] * NUM_VALVES
pump_duty   = 0.0   # percent 0–100
pump_pwm    = None


# ---- GPIO setup ----------------------------------------------------------
def setup():
    global pump_pwm
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for pin in VALVE_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(PUMP_PWM_PIN, GPIO.OUT)
    pump_pwm = GPIO.PWM(PUMP_PWM_PIN, PUMP_PWM_FREQ)
    pump_pwm.start(0)


def cleanup():
    all_valves(False)
    if pump_pwm:
        pump_pwm.ChangeDutyCycle(0)
        pump_pwm.stop()
    GPIO.cleanup()


# ---- Helpers -------------------------------------------------------------
def set_valve(index: int, open: bool):
    valve_state[index] = open
    GPIO.output(VALVE_PINS[index], GPIO.HIGH if open else GPIO.LOW)


def all_valves(open: bool):
    for i in range(NUM_VALVES):
        set_valve(i, open)


def set_pump(duty: float):
    global pump_duty
    pump_duty = max(0.0, min(100.0, duty))
    pump_pwm.ChangeDutyCycle(pump_duty)


def print_status():
    print("--- Status ---")
    for i in range(NUM_VALVES):
        state = "OPEN" if valve_state[i] else "CLOSED"
        print(f"  Valve {i+1} ({VALVE_NAMES[i]}): {state}")
    print(f"  Pump duty: {pump_duty:.0f}%")


def print_help():
    print("Commands:")
    print("  o <1-6>    open valve")
    print("  c <1-6>    close valve")
    print("  a          open all valves")
    print("  x          close all valves, pump off")
    print("  p <0-100>  set pump duty (%)")
    print("  s          status")
    print("  ?          help")
    print("  q          quit")


# ---- Main loop -----------------------------------------------------------
def main():
    setup()
    signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))

    print("Heart Sleeve (RPi) — Valve Control Ready")
    print_help()

    while True:
        try:
            raw = input("\n> ").strip()
        except EOFError:
            break

        if not raw:
            continue

        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd == "o":
            if len(parts) < 2 or not parts[1].isdigit():
                print("Usage: o <1-6>")
                continue
            n = int(parts[1])
            if 1 <= n <= NUM_VALVES:
                set_valve(n - 1, True)
                print(f"Opened valve {n}")
            else:
                print("Invalid valve number (1-6)")

        elif cmd == "c":
            if len(parts) < 2 or not parts[1].isdigit():
                print("Usage: c <1-6>")
                continue
            n = int(parts[1])
            if 1 <= n <= NUM_VALVES:
                set_valve(n - 1, False)
                print(f"Closed valve {n}")
            else:
                print("Invalid valve number (1-6)")

        elif cmd == "a":
            all_valves(True)
            print("All valves OPEN")

        elif cmd == "x":
            all_valves(False)
            set_pump(0)
            print("All valves CLOSED, pump OFF")

        elif cmd == "p":
            if len(parts) < 2:
                print("Usage: p <0-100>")
                continue
            try:
                duty = float(parts[1])
                set_pump(duty)
                print(f"Pump duty set to {pump_duty:.0f}%")
            except ValueError:
                print("Usage: p <0-100>")

        elif cmd == "s":
            print_status()

        elif cmd in ("?", "help"):
            print_help()

        elif cmd == "q":
            break

        else:
            print(f"Unknown command '{cmd}'. Type ? for help.")

    cleanup()
    print("Goodbye.")


if __name__ == "__main__":
    main()
