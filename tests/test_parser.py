from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_REF = ROOT / "reference" / "python"
if str(PY_REF) not in sys.path:
    sys.path.insert(0, str(PY_REF))

import rtimg_v0  # type: ignore


class TestParser(unittest.TestCase):
    def test_invalid_magic(self) -> None:
        sample = ROOT / "testdata" / "encoded" / "invalid_magic.rti"
        sample.parent.mkdir(parents=True, exist_ok=True)
        sample.write_bytes(b"NOPE" + b"\x00" * 64)
        with self.assertRaises(rtimg_v0.RTImgError):
            rtimg_v0.read_rtimg(str(sample))


if __name__ == "__main__":
    unittest.main()
