from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "reference" / "python" / "rtimg_v0.py"
TMP = ROOT / "testdata"


class TestRoundtrip(unittest.TestCase):
    def test_encode_decode_roundtrip(self) -> None:
        src = TMP / "input" / "roundtrip.png"
        enc = TMP / "encoded" / "roundtrip.rti"
        dec = TMP / "decoded" / "roundtrip.png"
        src.parent.mkdir(parents=True, exist_ok=True)
        enc.parent.mkdir(parents=True, exist_ok=True)
        dec.parent.mkdir(parents=True, exist_ok=True)

        Image.new("RGB", (8, 8), (10, 20, 30)).save(src)
        subprocess.run([sys.executable, str(SCRIPT), "encode", str(src), str(enc), "--tile", "4"], check=True)
        subprocess.run([sys.executable, str(SCRIPT), "decode", str(enc), str(dec)], check=True)

        orig = Image.open(src)
        restored = Image.open(dec)
        self.assertEqual(orig.mode, restored.mode)
        self.assertEqual(orig.size, restored.size)
        self.assertEqual(orig.tobytes(), restored.tobytes())


if __name__ == "__main__":
    unittest.main()
