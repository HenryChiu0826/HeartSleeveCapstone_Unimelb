# pins.py — Raspberry Pi pin assignments and config for Heart Sleeve
#
# Uses BCM (Broadcom) GPIO numbering throughout.
# Run all scripts with: python <script>.py
#
# Key differences from Arduino/ESP32:
#   - Pi has NO built-in ADC. An external ADC is required for pressure sensors.
#     Supported options (set ADC_TYPE below):
#       "MCP3008"  — SPI,  10-bit, cheap and common
#       "ADS1115"  — I2C,  16-bit, higher accuracy (recommended)
#   - PWM: hardware PWM available on GPIO 12, 13, 18, 19 only.
#     Software PWM on any pin via RPi.GPIO (less precise, may jitter).
#   - GPIO is 3.3 V logic — use a level shifter or relay board for 12 V valves.
#
# Dependencies:
#   pip install RPi.GPIO gpiozero
#   MCP3008: pip install adafruit-mcp3xxx adafruit-blinka
#   ADS1115: pip install adafruit-circuitpython-ads1x15 adafruit-blinka

# ---- ADC selection -------------------------------------------------------
ADC_TYPE = "ADS1115"   # "MCP3008" or "ADS1115" — TODO: set to match hardware

# ---- Solenoid Valves (BCM, active HIGH = open) ---------------------------
VALVE_APEX_CIRC = 17
VALVE_MID_CIRC  = 27
VALVE_BASE_CIRC = 22
VALVE_APEX_HEL  = 10
VALVE_MID_HEL   =  9
VALVE_BASE_HEL  = 11

VALVE_PINS = [
    VALVE_APEX_CIRC, VALVE_MID_CIRC, VALVE_BASE_CIRC,
    VALVE_APEX_HEL,  VALVE_MID_HEL,  VALVE_BASE_HEL,
]

VALVE_NAMES = [
    "Apex Circumferential",
    "Mid  Circumferential",
    "Base Circumferential",
    "Apex Helical",
    "Mid  Helical",
    "Base Helical",
]

# ---- Pump (hardware PWM — BCM 18) ----------------------------------------
PUMP_PWM_PIN    = 18     # hardware PWM pin
PUMP_PWM_FREQ   = 1000   # Hz

# ---- ADC channels (used by sensor_interface.py) -------------------------
PRESSURE_CH_1   = 0      # ADC channel for sensor 1
PRESSURE_CH_2   = 1      # ADC channel for sensor 2

# ---- MCP3008 SPI config (only used if ADC_TYPE = "MCP3008") -------------
MCP3008_CLK  = 11   # SPI CLK  (BCM)
MCP3008_MISO = 9    # SPI MISO (BCM)
MCP3008_MOSI = 10   # SPI MOSI (BCM)
MCP3008_CS   = 8    # SPI CE0  (BCM)

# ---- Sensor scaling ------------------------------------------------------
SENSOR_SUPPLY_V = 3.3     # Pi GPIO is 3.3 V
SENSOR_SCALE    = 60.6    # kPa per volt — PLACEHOLDER: update from datasheet
SENSOR_OFFSET   = 0.0     # kPa offset   — PLACEHOLDER

# ---- Derived: ADC full-scale counts --------------------------------------
ADC_FULLSCALE = {"MCP3008": 1023, "ADS1115": 32767}.get(ADC_TYPE, 1023)
