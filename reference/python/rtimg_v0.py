
#!/usr/bin/env python3
"""
RTImg v0 - prototipo de codec de imagen para RT Stack
Perfil implementado: lossless predictivo + compresión zlib por tiles

Dependencias:
    pip install pillow

Uso:
    python rtimg_v0.py encode input.png output.rti --tile 64 --predictor paeth
    python rtimg_v0.py decode output.rti restored.png
    python rtimg_v0.py inspect output.rti
    python rtimg_v0.py psnr original.png restored.png
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import struct
import sys
import zlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

from PIL import Image

MAGIC = b"RTI0"
VERSION_MAJOR = 0
VERSION_MINOR = 1

PROFILE_LOSSLESS = 0

COLORSPACE_GRAY = 0
COLORSPACE_RGB = 1
COLORSPACE_RGBA = 2

ENTROPY_RAW = 0
ENTROPY_ZLIB = 1

PRED_NONE = 0
PRED_LEFT = 1
PRED_UP = 2
PRED_AVG = 3
PRED_PAETH = 4

FLAGS_ALPHA = 1 << 0
FLAGS_METADATA = 1 << 1
FLAGS_TILES_INDEPENDENT = 1 << 2
FLAGS_CRC32 = 1 << 3

HEADER_STRUCT = struct.Struct("<4sBBBBIIBBBBHHBBHI")
# magic, vmaj, vmin, profile, flags, width, height, channels, bit_depth,
# color_space, reserved, tile_w, tile_h, predictor, entropy, metadata_count, tile_count

TILE_STRUCT = struct.Struct("<IIHHIII")
# x, y, w, h, raw_len, comp_len, crc32


class RTImgError(Exception):
    pass


@dataclass
class RTImgHeader:
    width: int
    height: int
    channels: int
    bit_depth: int
    color_space: int
    tile_w: int
    tile_h: int
    predictor: int
    entropy: int
    flags: int
    profile: int = PROFILE_LOSSLESS
    version_major: int = VERSION_MAJOR
    version_minor: int = VERSION_MINOR
    reserved: int = 0


@dataclass
class TilePacket:
    x: int
    y: int
    w: int
    h: int
    raw_len: int
    comp_len: int
    crc32: int
    payload: bytes


@dataclass
class RTImgFile:
    header: RTImgHeader
    metadata: Dict[str, str] = field(default_factory=dict)
    tiles: List[TilePacket] = field(default_factory=list)


def paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def predictor_value(kind: int, left: int, up: int, up_left: int) -> int:
    if kind == PRED_NONE:
        return 0
    if kind == PRED_LEFT:
        return left
    if kind == PRED_UP:
        return up
    if kind == PRED_AVG:
        return (left + up) // 2
    if kind == PRED_PAETH:
        return paeth_predictor(left, up, up_left)
    raise RTImgError(f"Predictor no soportado: {kind}")


def load_image_for_rtimg(path: str) -> Tuple[Image.Image, int, int]:
    img = Image.open(path)
    if img.mode not in ("L", "RGB", "RGBA"):
        if "A" in img.getbands():
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

    if img.mode == "L":
        color_space = COLORSPACE_GRAY
        channels = 1
    elif img.mode == "RGB":
        color_space = COLORSPACE_RGB
        channels = 3
    elif img.mode == "RGBA":
        color_space = COLORSPACE_RGBA
        channels = 4
    else:
        raise RTImgError(f"Modo de imagen no soportado: {img.mode}")

    return img, color_space, channels


def image_from_raw(width: int, height: int, channels: int, data: bytes) -> Image.Image:
    if channels == 1:
        return Image.frombytes("L", (width, height), data)
    if channels == 3:
        return Image.frombytes("RGB", (width, height), data)
    if channels == 4:
        return Image.frombytes("RGBA", (width, height), data)
    raise RTImgError(f"Número de canales no soportado: {channels}")


def iter_tiles(width: int, height: int, tile_w: int, tile_h: int) -> Iterable[Tuple[int, int, int, int]]:
    for y in range(0, height, tile_h):
        h = min(tile_h, height - y)
        for x in range(0, width, tile_w):
            w = min(tile_w, width - x)
            yield x, y, w, h


def encode_tile_lossless(tile_bytes: bytes, w: int, h: int, channels: int, predictor: int) -> bytes:
    out = bytearray(len(tile_bytes))
    stride = w * channels

    for y in range(h):
        row_off = y * stride
        prev_row_off = (y - 1) * stride
        for x in range(w):
            for c in range(channels):
                idx = row_off + x * channels + c
                sample = tile_bytes[idx]

                left = tile_bytes[idx - channels] if x > 0 else 0
                up = tile_bytes[prev_row_off + x * channels + c] if y > 0 else 0
                up_left = tile_bytes[prev_row_off + (x - 1) * channels + c] if (x > 0 and y > 0) else 0

                pred = predictor_value(predictor, left, up, up_left)
                out[idx] = (sample - pred) & 0xFF

    return bytes(out)


def decode_tile_lossless(residual_bytes: bytes, w: int, h: int, channels: int, predictor: int) -> bytes:
    out = bytearray(len(residual_bytes))
    stride = w * channels

    for y in range(h):
        row_off = y * stride
        prev_row_off = (y - 1) * stride
        for x in range(w):
            for c in range(channels):
                idx = row_off + x * channels + c
                residual = residual_bytes[idx]

                left = out[idx - channels] if x > 0 else 0
                up = out[prev_row_off + x * channels + c] if y > 0 else 0
                up_left = out[prev_row_off + (x - 1) * channels + c] if (x > 0 and y > 0) else 0

                pred = predictor_value(predictor, left, up, up_left)
                out[idx] = (pred + residual) & 0xFF

    return bytes(out)


def compress_payload(data: bytes, entropy: int) -> bytes:
    if entropy == ENTROPY_RAW:
        return data
    if entropy == ENTROPY_ZLIB:
        return zlib.compress(data, level=9)
    raise RTImgError(f"Entropía no soportada: {entropy}")


def decompress_payload(data: bytes, entropy: int, expected_size: int) -> bytes:
    if entropy == ENTROPY_RAW:
        result = data
    elif entropy == ENTROPY_ZLIB:
        result = zlib.decompress(data)
    else:
        raise RTImgError(f"Entropía no soportada: {entropy}")

    if len(result) != expected_size:
        raise RTImgError(
            f"Tamaño inesperado al descomprimir: esperado={expected_size}, obtenido={len(result)}"
        )
    return result


def extract_tile_bytes(img: Image.Image, x: int, y: int, w: int, h: int) -> bytes:
    tile = img.crop((x, y, x + w, y + h))
    return tile.tobytes()


def insert_tile_bytes(canvas: bytearray, width: int, channels: int, x: int, y: int, w: int, h: int, tile_bytes: bytes) -> None:
    src_stride = w * channels
    dst_stride = width * channels
    for row in range(h):
        src_start = row * src_stride
        src_end = src_start + src_stride
        dst_start = ((y + row) * dst_stride) + (x * channels)
        dst_end = dst_start + src_stride
        canvas[dst_start:dst_end] = tile_bytes[src_start:src_end]


def serialize_metadata(metadata: Dict[str, str]) -> bytes:
    buf = io.BytesIO()
    for key, value in metadata.items():
        k = key.encode("utf-8")
        v = value.encode("utf-8")
        buf.write(struct.pack("<HI", len(k), len(v)))
        buf.write(k)
        buf.write(v)
    return buf.getvalue()


def parse_metadata(stream: io.BufferedReader, count: int) -> Dict[str, str]:
    metadata = {}
    for _ in range(count):
        header = stream.read(6)
        if len(header) != 6:
            raise RTImgError("No se pudo leer el encabezado TLV de metadata")
        key_len, val_len = struct.unpack("<HI", header)
        key = stream.read(key_len)
        value = stream.read(val_len)
        if len(key) != key_len or len(value) != val_len:
            raise RTImgError("No se pudo leer el cuerpo TLV de metadata")
        metadata[key.decode("utf-8")] = value.decode("utf-8")
    return metadata


def write_rtimg(rt: RTImgFile, output_path: str) -> None:
    metadata_count = len(rt.metadata)
    tile_count = len(rt.tiles)

    with open(output_path, "wb") as f:
        f.write(
            HEADER_STRUCT.pack(
                MAGIC,
                rt.header.version_major,
                rt.header.version_minor,
                rt.header.profile,
                rt.header.flags,
                rt.header.width,
                rt.header.height,
                rt.header.channels,
                rt.header.bit_depth,
                rt.header.color_space,
                rt.header.reserved,
                rt.header.tile_w,
                rt.header.tile_h,
                rt.header.predictor,
                rt.header.entropy,
                metadata_count,
                tile_count,
            )
        )

        f.write(serialize_metadata(rt.metadata))

        for tile in rt.tiles:
            f.write(
                TILE_STRUCT.pack(
                    tile.x,
                    tile.y,
                    tile.w,
                    tile.h,
                    tile.raw_len,
                    tile.comp_len,
                    tile.crc32,
                )
            )
            f.write(tile.payload)


def read_rtimg(path: str) -> RTImgFile:
    with open(path, "rb") as f:
        header_raw = f.read(HEADER_STRUCT.size)
        if len(header_raw) != HEADER_STRUCT.size:
            raise RTImgError("Archivo RTImg truncado en cabecera")

        (
            magic,
            version_major,
            version_minor,
            profile,
            flags,
            width,
            height,
            channels,
            bit_depth,
            color_space,
            reserved,
            tile_w,
            tile_h,
            predictor,
            entropy,
            metadata_count,
            tile_count,
        ) = HEADER_STRUCT.unpack(header_raw)

        if magic != MAGIC:
            raise RTImgError("Magic inválido: no es un archivo RTImg")
        if profile != PROFILE_LOSSLESS:
            raise RTImgError(f"Perfil no implementado por este prototipo: {profile}")
        if bit_depth != 8:
            raise RTImgError(f"Bit depth no implementado por este prototipo: {bit_depth}")

        header = RTImgHeader(
            width=width,
            height=height,
            channels=channels,
            bit_depth=bit_depth,
            color_space=color_space,
            tile_w=tile_w,
            tile_h=tile_h,
            predictor=predictor,
            entropy=entropy,
            flags=flags,
            profile=profile,
            version_major=version_major,
            version_minor=version_minor,
            reserved=reserved,
        )

        metadata = parse_metadata(f, metadata_count)

        tiles = []
        for _ in range(tile_count):
            tile_hdr = f.read(TILE_STRUCT.size)
            if len(tile_hdr) != TILE_STRUCT.size:
                raise RTImgError("Archivo RTImg truncado en descriptor de tile")

            x, y, w, h, raw_len, comp_len, crc32_value = TILE_STRUCT.unpack(tile_hdr)
            payload = f.read(comp_len)
            if len(payload) != comp_len:
                raise RTImgError("Archivo RTImg truncado en payload de tile")

            if flags & FLAGS_CRC32:
                calc = zlib.crc32(payload) & 0xFFFFFFFF
                if calc != crc32_value:
                    raise RTImgError(
                        f"CRC32 inválido en tile ({x},{y}) esperado={crc32_value} obtenido={calc}"
                    )

            tiles.append(
                TilePacket(
                    x=x,
                    y=y,
                    w=w,
                    h=h,
                    raw_len=raw_len,
                    comp_len=comp_len,
                    crc32=crc32_value,
                    payload=payload,
                )
            )

    return RTImgFile(header=header, metadata=metadata, tiles=tiles)


def encode_image_to_rtimg(
    input_path: str,
    output_path: str,
    tile_size: int = 64,
    predictor: int = PRED_PAETH,
    entropy: int = ENTROPY_ZLIB,
    extra_metadata: Dict[str, str] | None = None,
) -> RTImgFile:
    img, color_space, channels = load_image_for_rtimg(input_path)

    flags = FLAGS_TILES_INDEPENDENT | FLAGS_CRC32
    if channels == 4:
        flags |= FLAGS_ALPHA

    metadata = {
        "codec": "RTImg",
        "profile": "lossless-v0",
        "source_filename": os.path.basename(input_path),
        "source_mode": img.mode,
    }
    if extra_metadata:
        metadata.update(extra_metadata)
    if metadata:
        flags |= FLAGS_METADATA

    header = RTImgHeader(
        width=img.width,
        height=img.height,
        channels=channels,
        bit_depth=8,
        color_space=color_space,
        tile_w=tile_size,
        tile_h=tile_size,
        predictor=predictor,
        entropy=entropy,
        flags=flags,
    )

    rtfile = RTImgFile(header=header, metadata=metadata, tiles=[])

    for x, y, w, h in iter_tiles(img.width, img.height, tile_size, tile_size):
        raw_tile = extract_tile_bytes(img, x, y, w, h)
        residual = encode_tile_lossless(raw_tile, w, h, channels, predictor)
        payload = compress_payload(residual, entropy)

        rtfile.tiles.append(
            TilePacket(
                x=x,
                y=y,
                w=w,
                h=h,
                raw_len=len(residual),
                comp_len=len(payload),
                crc32=zlib.crc32(payload) & 0xFFFFFFFF,
                payload=payload,
            )
        )

    write_rtimg(rtfile, output_path)
    return rtfile


def decode_rtimg_to_image(input_path: str, output_path: str) -> RTImgFile:
    rt = read_rtimg(input_path)
    canvas = bytearray(rt.header.width * rt.header.height * rt.header.channels)

    for tile in rt.tiles:
        residual = decompress_payload(tile.payload, rt.header.entropy, tile.raw_len)
        raw_tile = decode_tile_lossless(
            residual,
            tile.w,
            tile.h,
            rt.header.channels,
            rt.header.predictor,
        )
        insert_tile_bytes(
            canvas,
            rt.header.width,
            rt.header.channels,
            tile.x,
            tile.y,
            tile.w,
            tile.h,
            raw_tile,
        )

    img = image_from_raw(rt.header.width, rt.header.height, rt.header.channels, bytes(canvas))
    img.save(output_path)
    return rt


def mse_from_images(path_a: str, path_b: str) -> float:
    img_a = Image.open(path_a).convert("RGBA")
    img_b = Image.open(path_b).convert("RGBA")

    if img_a.size != img_b.size:
        raise RTImgError("Las imágenes deben tener el mismo tamaño para calcular MSE/PSNR")

    a = img_a.tobytes()
    b = img_b.tobytes()

    acc = 0
    n = len(a)
    for i in range(n):
        d = a[i] - b[i]
        acc += d * d
    return acc / n if n else 0.0


def psnr_from_paths(path_a: str, path_b: str, peak: float = 255.0) -> float:
    mse = mse_from_images(path_a, path_b)
    if mse == 0:
        return float("inf")
    return 10.0 * math.log10((peak * peak) / mse)


def predictor_from_name(name: str) -> int:
    table = {
        "none": PRED_NONE,
        "left": PRED_LEFT,
        "up": PRED_UP,
        "avg": PRED_AVG,
        "paeth": PRED_PAETH,
    }
    try:
        return table[name.lower()]
    except KeyError as exc:
        valid = ", ".join(table.keys())
        raise RTImgError(f"Predictor inválido '{name}'. Válidos: {valid}") from exc


def entropy_from_name(name: str) -> int:
    table = {
        "raw": ENTROPY_RAW,
        "zlib": ENTROPY_ZLIB,
    }
    try:
        return table[name.lower()]
    except KeyError as exc:
        valid = ", ".join(table.keys())
        raise RTImgError(f"Entropía inválida '{name}'. Válidas: {valid}") from exc


def colorspace_name(cs: int) -> str:
    return {
        COLORSPACE_GRAY: "GRAY",
        COLORSPACE_RGB: "RGB",
        COLORSPACE_RGBA: "RGBA",
    }.get(cs, f"UNKNOWN({cs})")


def predictor_name(pred: int) -> str:
    return {
        PRED_NONE: "none",
        PRED_LEFT: "left",
        PRED_UP: "up",
        PRED_AVG: "avg",
        PRED_PAETH: "paeth",
    }.get(pred, f"unknown({pred})")


def entropy_name(ent: int) -> str:
    return {
        ENTROPY_RAW: "raw",
        ENTROPY_ZLIB: "zlib",
    }.get(ent, f"unknown({ent})")


def inspect_rtimg(path: str) -> None:
    rt = read_rtimg(path)
    total_comp = sum(t.comp_len for t in rt.tiles)
    total_raw = sum(t.raw_len for t in rt.tiles)
    ratio = (total_raw / total_comp) if total_comp else 0.0

    report = {
        "magic": MAGIC.decode("ascii"),
        "version": f"{rt.header.version_major}.{rt.header.version_minor}",
        "profile": rt.header.profile,
        "size": [rt.header.width, rt.header.height],
        "channels": rt.header.channels,
        "bit_depth": rt.header.bit_depth,
        "color_space": colorspace_name(rt.header.color_space),
        "tile_size": [rt.header.tile_w, rt.header.tile_h],
        "predictor": predictor_name(rt.header.predictor),
        "entropy": entropy_name(rt.header.entropy),
        "flags": rt.header.flags,
        "tile_count": len(rt.tiles),
        "bytes_raw_tiles": total_raw,
        "bytes_compressed_tiles": total_comp,
        "compression_ratio_raw_over_compressed": round(ratio, 4),
        "metadata": rt.metadata,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RTImg v0 - prototipo codec de imagen lossless")
    sub = parser.add_subparsers(dest="command", required=True)

    p_enc = sub.add_parser("encode", help="Codifica una imagen a RTImg")
    p_enc.add_argument("input", help="Imagen de entrada (PNG/JPEG/etc.)")
    p_enc.add_argument("output", help="Archivo .rti de salida")
    p_enc.add_argument("--tile", type=int, default=64, help="Tamaño de tile cuadrado")
    p_enc.add_argument("--predictor", default="paeth", help="none|left|up|avg|paeth")
    p_enc.add_argument("--entropy", default="zlib", help="raw|zlib")
    p_enc.add_argument(
        "--meta",
        action="append",
        default=[],
        help="Metadata en formato clave=valor. Puede repetirse varias veces.",
    )

    p_dec = sub.add_parser("decode", help="Decodifica un RTImg a imagen estándar")
    p_dec.add_argument("input", help="Archivo .rti")
    p_dec.add_argument("output", help="Imagen de salida")

    p_ins = sub.add_parser("inspect", help="Inspecciona un archivo RTImg")
    p_ins.add_argument("input", help="Archivo .rti")

    p_psnr = sub.add_parser("psnr", help="Calcula PSNR entre dos imágenes")
    p_psnr.add_argument("image_a")
    p_psnr.add_argument("image_b")

    return parser


def parse_meta_args(items: List[str]) -> Dict[str, str]:
    meta = {}
    for item in items:
        if "=" not in item:
            raise RTImgError(f"Metadata inválida '{item}'. Debe ser clave=valor")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise RTImgError("La clave de metadata no puede estar vacía")
        meta[key] = value
    return meta


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        if args.command == "encode":
            meta = parse_meta_args(args.meta)
            rt = encode_image_to_rtimg(
                args.input,
                args.output,
                tile_size=args.tile,
                predictor=predictor_from_name(args.predictor),
                entropy=entropy_from_name(args.entropy),
                extra_metadata=meta,
            )
            print(
                f"OK encode: {args.input} -> {args.output} | "
                f"{rt.header.width}x{rt.header.height} | "
                f"tiles={len(rt.tiles)} | predictor={predictor_name(rt.header.predictor)} | "
                f"entropy={entropy_name(rt.header.entropy)}"
            )
            return 0

        if args.command == "decode":
            rt = decode_rtimg_to_image(args.input, args.output)
            print(
                f"OK decode: {args.input} -> {args.output} | "
                f"{rt.header.width}x{rt.header.height} | channels={rt.header.channels}"
            )
            return 0

        if args.command == "inspect":
            inspect_rtimg(args.input)
            return 0

        if args.command == "psnr":
            value = psnr_from_paths(args.image_a, args.image_b)
            if math.isinf(value):
                print("PSNR: inf dB (reconstrucción idéntica)")
            else:
                print(f"PSNR: {value:.4f} dB")
            return 0

        parser.print_help()
        return 1

    except RTImgError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR no controlado: {exc}", file=sys.stderr)
        return 99


if __name__ == "__main__":
    raise SystemExit(main())
