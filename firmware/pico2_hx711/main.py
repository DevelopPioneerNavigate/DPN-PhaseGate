"""DPN PhaseGate PG-01 raw measurement transmitter (MicroPython Pico 2).

Load onto an approved, safely wired MicroPython Pico 2 only.
NO actuator commands. NO object transfer. NO 5V GPIO. NO power output control.

Station A: set STATION_ID="A".
Station B: set STATION_ID="B" on its separate board.
"""
import sys
import time
from machine import Pin

STATION_ID = "A"  # IMPORTANT: explicitly change to B for the second physical board
DOUT_PIN = 14     # Confirm actual board pinout, voltage compatibility, safe wiring
SCK_PIN = 15
RATE_LIMIT_MS = 115
ADC_READY_TIMEOUT_MS = 150

if STATION_ID not in ("A", "B"):
    raise ValueError("station ID must be A or B")

dout = Pin(DOUT_PIN, Pin.IN)
clock = Pin(SCK_PIN, Pin.OUT, value=0)


def read_counts():
    """One 24-bit channel A, gain 128 conversion; no calibrated grams."""
    start = time.ticks_ms()
    while dout.value():
        if time.ticks_diff(time.ticks_ms(), start) > ADC_READY_TIMEOUT_MS:
            return None
        time.sleep_ms(1)
    value = 0
    for _ in range(24):
        clock.value(1)
        time.sleep_us(1)
        value = (value << 1) | dout.value()
        clock.value(0)
        time.sleep_us(1)
    # 25th pulse selects gain 128, channel A, for the next conversion.
    clock.value(1)
    time.sleep_us(1)
    clock.value(0)
    if value & 0x800000:
        value -= 0x1000000
    return value


def checksum(value):
    result = 0
    for byte in value:
        result ^= ord(byte)
    return result


def run():
    seq = 0
    last = time.ticks_ms()
    while True:
        count = read_counts()
        now = time.ticks_ms()
        if count is None:
            # No fabricated reading during ADC startup or disconnection.
            time.sleep_ms(40)
            continue
        if time.ticks_diff(now, last) < RATE_LIMIT_MS:
            time.sleep_ms(15)
            continue
        last = now
        body = "PG1|{}|{}|{}|{}|RAW".format(STATION_ID,seq,now,count)
        sys.stdout.write("{}|{:02X}\n".format(body,checksum(body)))
        seq += 1
        if seq > 2147483647:
            # Fail closed rather than send nonmonotonic sequences. Manually reboot/reconnect.
            raise RuntimeError("sequence exhausted: stop and restart inspected station")
        time.sleep_ms(10)


if __name__ == "__main__":
    run()
