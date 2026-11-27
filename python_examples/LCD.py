#!/usr/bin/env python3
import errno
import os
import math
import sys
import time
from contextlib import closing

try:
	from smbus import SMBus  # Bibliothèque utilisée dans le code fourni du LCD1602
except ImportError:
	from smbus2 import SMBus

ENABLE = 0x04
REGISTER_SELECT = 0x01
BACKLIGHT = 0x08
ROW_OFFSETS = (0x00, 0x40, 0x14, 0x54)
I2C_BUS = 1  # SDA1 (GPIO2) et SCL1 (GPIO3)
LCD_ADDRESSES = (*range(0x20, 0x28), *range(0x38, 0x40))


def detect_address(bus):
	"""Find a single responding PCF8574/PCF8574A address."""
	found = []
	for address in LCD_ADDRESSES:
		try:
			bus.read_byte(address)
		except OSError as error:
			if error.errno not in (errno.ENXIO, getattr(errno, "EREMOTEIO", 121)):
				raise
		else:
			found.append(address)
	if len(found) != 1:
		addresses = ", ".join(f"0x{address:02x}" for address in found)
		if found:
			raise ValueError(f"Several I2C devices found ({addresses}); set GTI700_LCD_ADDRESS explicitly")
		raise ValueError("LCD not detected on I2C bus 1; check SDA1, SCL1, power and ground with i2cdetect -y 1")
	return found[0]


class LCD:
	def __init__(self, bus, address):
		self.bus = bus
		self.address = address

	def _nibble(self, value):
		# Keep RS high for character data; dropping RS makes the LCD interpret
		# every character as a command. RW stays low for writes.
		value = (value & (0xF0 | REGISTER_SELECT)) | BACKLIGHT
		self.bus.write_byte(self.address, value)
		self.bus.write_byte(self.address, value | ENABLE)
		time.sleep(0.0005)
		self.bus.write_byte(self.address, value & ~ENABLE)
		time.sleep(0.0001)

	def _send(self, value, data=False):
		register = REGISTER_SELECT if data else 0
		self._nibble((value & 0xF0) | register)
		self._nibble(((value << 4) & 0xF0) | register)
		if not data and value in (0x01, 0x02):
			time.sleep(0.002)

	def initialize(self):
		self.bus.write_byte(self.address, BACKLIGHT)
		time.sleep(0.05)
		self._nibble(0x30)
		time.sleep(0.005)
		self._nibble(0x30)
		time.sleep(0.001)
		self._nibble(0x30)
		self._nibble(0x20)
		self._send(0x28)
		self._send(0x0C)
		self._send(0x01)
		self._send(0x06)

	def write_page(self, text, columns, rows):
		self._send(0x01)
		for row in range(rows):
			self._send(0x80 + ROW_OFFSETS[row])
			line = text[row * columns:(row + 1) * columns].ljust(columns)
			for character in line:
				self._send(ord(character), data=True)


def main():
	if len(sys.argv) != 2:
		print("Usage: LCD.py <text>", file=sys.stderr)
		return 2

	try:
		address_setting = os.environ.get("GTI700_LCD_ADDRESS", "0x27").strip().lower()
		address = None if address_setting == "auto" else int(address_setting, 0)
		columns = int(os.environ.get("GTI700_LCD_COLUMNS", "16"))
		rows = int(os.environ.get("GTI700_LCD_ROWS", "2"))
		frame_seconds = float(os.environ.get("GTI700_LCD_FRAME_SECONDS", "1.2"))
	except ValueError as error:
		print(f"Invalid LCD configuration: {error}", file=sys.stderr)
		return 2

	if (address is not None and address not in LCD_ADDRESSES) or columns < 1 or rows not in (1, 2, 4):
		print("LCD address or dimensions are invalid", file=sys.stderr)
		return 2
	if not math.isfinite(frame_seconds) or frame_seconds <= 0:
		print("LCD dimensions or frame delay are invalid", file=sys.stderr)
		return 2

	text = sys.argv[1]
	page_size = columns * rows
	pages = [text[index:index + page_size] for index in range(0, len(text), page_size)]
	if not pages:
		pages = [""]

	try:
		with closing(SMBus(I2C_BUS)) as bus:
			if address is None:
				address = detect_address(bus)
			lcd = LCD(bus, address)
			lcd.initialize()
			for index, page in enumerate(pages):
				lcd.write_page(page, columns, rows)
				if index < len(pages) - 1:
					time.sleep(frame_seconds)
	except (OSError, ValueError) as error:
		print(f"LCD I2C error: {error}", file=sys.stderr)
		return 1

	return 0


if __name__ == "__main__":
	sys.exit(main())
