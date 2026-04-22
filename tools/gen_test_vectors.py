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
    parser = argparse.ArgumentParser(description="Generate RTImg vectors from image inputs")
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    parser.add_argument("--tile", type=int, default=64)
    parser.add_argument("--predictor", default="paeth", choices=["none", "left", "up", "avg", "paeth"])
    args = parser.parse_args()

    input_dir = pathlib.Path(args.input_dir)
    output_dir = pathlib.Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    supported = {".png", ".bmp", ".tif", ".tiff", ".webp"}
    total = 0
    for src in sorted(input_dir.iterdir()):
        if not src.is_file() or src.suffix.lower() not in supported:
            continue
        dst = output_dir / (src.stem + ".rti")
        rtimg_v0.encode_image_to_rtimg(str(src), str(dst), tile_size=args.tile, predictor=args.predictor)
        print(f"ok: {src.name} -> {dst.name}")
        total += 1

    print(f"vectors generated: {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
