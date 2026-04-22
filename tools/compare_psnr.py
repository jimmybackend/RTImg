#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_REF = ROOT / "reference" / "python"
if str(PY_REF) not in sys.path:
    sys.path.insert(0, str(PY_REF))

import rtimg_v0  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two images and report PSNR")
    parser.add_argument("original")
    parser.add_argument("reconstructed")
    args = parser.parse_args()

    value = rtimg_v0.psnr_from_paths(args.original, args.reconstructed)
    print("PSNR: inf (exact reconstruction)" if value == float("inf") else f"PSNR: {value:.4f} dB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
