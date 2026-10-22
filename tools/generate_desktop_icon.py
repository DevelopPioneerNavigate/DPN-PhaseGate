"""Generate a custom PhaseGate Windows ICO, using Python standard library only.

Emits a PNG-compressed 256x256 frame inside the ICO container, accepted by
Windows icon readers and PyInstaller --icon.
"""
from __future__ import annotations
import math
import struct
import zlib
from pathlib import Path


def png_chunk(kind: bytes, data: bytes):
    return (struct.pack(">I", len(data)) + kind + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def render(size=256):
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            dx = x + .5 - size / 2
            dy = y + .5 - size / 2
            radius = math.hypot(dx, dy)
            angle = math.atan2(dy, dx)
            outer = math.exp(-((radius - size * .36) / (size * .037)) ** 2)
            inner = math.exp(-((radius - size * .245) / (size * .010)) ** 2)
            core = math.exp(-(radius / (size * .053)) ** 2)
            blue = .5 + .5 * math.cos(angle + math.pi / 4)
            luminance = min(1, outer + inner * .4 + core)
            red = int(min(255, 11 + 145 * outer * (1 - blue) + 52 * inner + 140 * core))
            green = int(min(255, 17 + 160 * outer * blue + 45 * inner + 174 * core))
            b = int(min(255, 35 + 200 * outer + 130 * inner + 210 * core))
            a = 255 if radius < size * .47 else max(0, int(255 * (size * .50-radius)/(size*.03)))
            row.extend((red, green, b, a))
        rows.append(bytes(row))
    rgba = zlib.compress(b"".join(rows), level=8)
    png = (b"\x89PNG\r\n\x1a\n"
           + png_chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
           + png_chunk(b"IDAT", rgba)
           + png_chunk(b"IEND", b""))
    return struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII",
        0, 0, 0, 0, 1, 32, len(png), 22) + png


def main():
    dest = Path("build/phasegate.ico")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(render())
    print(f"Created {dest} ({dest.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
