from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_REF = ROOT / "reference" / "python"
if str(PY_REF) not in sys.path:
    sys.path.insert(0, str(PY_REF))

import rtimg_v0  # type: ignore


class TestMetadata(unittest.TestCase):
    def test_metadata_roundtrip(self) -> None:
        payload = {"asset_id": "demo-001", "origin_format": "png"}
        encoded = rtimg_v0.serialize_metadata(payload)
        import io
        decoded = rtimg_v0.parse_metadata(io.BytesIO(encoded), len(payload))
        self.assertEqual(decoded, payload)


if __name__ == "__main__":
    unittest.main()
