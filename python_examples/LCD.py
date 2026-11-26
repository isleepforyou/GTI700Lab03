import os
import sys
import time
from textwrap import wrap

from smbus2 import SMBus

ENABLE = 0x04
BACKLIGHT = 0x08


def send_nibble(bus, address, nibble):
    bus.write_byte(address, nibble | BACKLIGHT | ENABLE)
    bus.write_byte(address, nibble | BACKLIGHT)
    time.sleep(0.00005)


def send_byte(bus, address, value, data=False):
    register = int(data)
    send_nibble(bus, address, (value & 0xF0) | register)
    send_nibble(bus, address, ((value & 0x0F) << 4) | register)


def initialize(bus, address):
    time.sleep(0.05)
    # Le contrôleur démarre en mode 8 bits, puis passe en mode 4 bits.
    for nibble, pause in ((0x30, 0.005), (0x30, 0.001), (0x30, 0.001), (0x20, 0.001)):
        send_nibble(bus, address, nibble)
        time.sleep(pause)
    for command in (0x28, 0x08, 0x01, 0x06, 0x0C):
        send_byte(bus, address, command)
        if command == 0x01:
            time.sleep(0.002)


def display(bus, address, text, columns, rows, frame_seconds):
    offsets = (0x00, 0x40) if rows == 2 else (0x00, 0x40, 0x14, 0x54)
    lines = wrap(text, width=columns)
    for start in range(0, len(lines), rows):
        if start:
            time.sleep(frame_seconds)
        frame = lines[start:start + rows]
        for row, offset in enumerate(offsets):
            send_byte(bus, address, 0x80 | offset)
            line = frame[row] if row < len(frame) else ""
            for char in line.ljust(columns):
                send_byte(bus, address, ord(char), data=True)


def main(text):
    columns = int(os.environ.get("GTI700_LCD_COLUMNS", "16"))
    rows = int(os.environ.get("GTI700_LCD_ROWS", "2"))
    if (columns, rows) not in ((16, 2), (20, 4)):
        raise ValueError("Dimensions prises en charge : 16x2 et 20x4.")
    address = int(os.environ.get("GTI700_LCD_ADDRESS", "0x27"), 0)
    frame_seconds = float(os.environ.get("GTI700_LCD_FRAME_SECONDS", "2.25"))

    with SMBus(1) as bus:
        initialize(bus, address)
        display(bus, address, text, columns, rows, frame_seconds)


if __name__ == "__main__":
    main(sys.argv[1])
