from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "reference" / "python" / "rtimg_v0.py"
TMP = ROOT / "testdata"


class TestCorruption(unittest.TestCase):
    def test_crc_detection_after_mutation(self) -> None:
        src = TMP / "input" / "corrupt.png"
        enc = TMP / "encoded" / "corrupt.rti"
        out = TMP / "decoded" / "corrupt.png"
        src.parent.mkdir(parents=True, exist_ok=True)
        enc.parent.mkdir(parents=True, exist_ok=True)
        out.parent.mkdir(parents=True, exist_ok=True)

        Image.new("RGB", (8, 8), (100, 110, 120)).save(src)
        subprocess.run([sys.executable, str(SCRIPT), "encode", str(src), str(enc), "--tile", "4"], check=True)

        data = bytearray(enc.read_bytes())
        data[-1] ^= 0x01
        enc.write_bytes(data)

        completed = subprocess.run([sys.executable, str(SCRIPT), "decode", str(enc), str(out)])
        self.assertNotEqual(completed.returncode, 0)


if __name__ == "__main__":
    unittest.main()
