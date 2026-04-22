from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_REF = ROOT / "reference" / "python"
if str(PY_REF) not in sys.path:
    sys.path.insert(0, str(PY_REF))

import rtimg_v0  # type: ignore


class TestTiles(unittest.TestCase):
    def test_tile_iteration(self) -> None:
        tiles = list(rtimg_v0.iter_tiles(130, 65, 64, 64))
        self.assertEqual(len(tiles), 6)
        self.assertEqual(tiles[0], (0, 0, 64, 64))
        self.assertEqual(tiles[-1], (128, 64, 2, 1))


if __name__ == "__main__":
    unittest.main()
