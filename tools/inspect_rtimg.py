#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY_REF = ROOT / "reference" / "python"
if str(PY_REF) not in sys.path:
    sys.path.insert(0, str(PY_REF))

import rtimg_v0  # type: ignore


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an RTImg file")
    parser.add_argument("input")
    args = parser.parse_args()
    print(json.dumps(rtimg_v0.inspect_rtimg(args.input), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
