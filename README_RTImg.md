# RTImg

**RTImg** is the native image codec of the **RT Stack** ecosystem by **Rethra Communications**.

`RT` stands for **Resilient Transmission**.

RTImg is designed as an **open, extensible, deterministic, tile-based image format** intended for internal use across the RT ecosystem, with controlled import/export interoperability to external formats.

---

## Project status

**Current status:** early open specification + reference prototype

This repository defines:

- an open binary image format
- a reference encoder/decoder design
- a practical lossless-first roadmap
- future integration points with:
  - **RTCore**
  - **RTStream**
  - **RTCloud**

The first production goal is **a stable lossless v0 profile** with a clean path toward future lossy profiles.

---

## Why RTImg exists

RTImg is **not** meant to replace universal consumer image formats such as PNG, JPEG, WebP, AVIF, or JPEG XL in the open web.

Its purpose is different:

- accept external image formats at system boundaries
- convert them into a **native RT internal representation**
- enable deterministic processing in RT pipelines
- support robust tile-based decoding and retransmission
- carry operational metadata relevant to RT services
- allow controlled export back to external formats when needed

In short:

> RTImg is the internal image substrate of RT Stack, not just another generic image file format.

---

## Design principles

RTImg is designed around the following principles:

### 1. Native internal format
All imagery entering the RT ecosystem can be normalized into RTImg.

### 2. Open specification
The bitstream and structures are documented publicly.

### 3. Deterministic behavior
Same input + same profile + same settings should produce reproducible output.

### 4. Tile-based resilience
Images are partitioned into independent tiles to improve:

- partial decoding
- streaming
- corruption isolation
- retransmission efficiency
- parallel encoding/decoding

### 5. Metadata for systems, not just files
RTImg metadata is intended to support operational workflows, provenance, and policy enforcement.

### 6. Extensible profiles
The architecture is designed to support:

- **lossless** profiles
- **lossy** profiles
- future progressive or layered transport

---

## Scope of v0

The recommended initial direction is:

- **Architecture:** hybrid and extensible
- **Reference implementation:** **lossless-first**

This means the format should reserve room for lossy operation in the future, but the first stable implementation should focus on exact round-trip reconstruction.

### Why lossless first

Because it allows:

- exact validation
- simpler interoperability testing
- stable test vectors
- easier parser and decoder verification
- lower implementation risk

---

## Core architecture

RTImg is structured around these major components:

### Encoder
Responsible for:

- ingesting normalized pixel data
- dividing the image into tiles
- applying spatial prediction
- generating residuals
- compressing tile payloads
- writing the RTImg bitstream

### Decoder
Responsible for:

- parsing the bitstream
- validating headers and checksums
- decoding tiles
- reconstructing pixels
- rebuilding the full image in memory
- exporting when required

### Parser
A dedicated parser layer is recommended so the format can be:

- inspected without full decode
- validated independently
- reused by tools and services

### Bitstream
The RTImg bitstream is versioned and structured for future compatibility.

### Metadata layer
Metadata should be machine-friendly, deterministic, and optionally extensible using TLV-like structures.

---

## Recommended v0 capabilities

The initial practical profile should support:

- image modes:
  - grayscale (`L`)
  - RGB
  - RGBA
- bit depth:
  - 8-bit per channel
- tile-based storage
- per-tile payload compression
- metadata TLV records
- per-tile integrity checks
- reference encoder and decoder

---

## Bitstream overview

A simplified RTImg file layout looks like this:

```text
[FIXED HEADER]
[METADATA TLV SECTION]
[TILE DESCRIPTOR 0][TILE PAYLOAD 0]
[TILE DESCRIPTOR 1][TILE PAYLOAD 1]
...
[TILE DESCRIPTOR N][TILE PAYLOAD N]
```

Each tile is independently addressable and decodable within the constraints of the selected profile.

---

## What makes RTImg special in RT Stack

RTImg is valuable because it can be deeply integrated into the broader platform.

### RTCore
- internal normalized image representation
- deterministic image preprocessing
- pipeline-safe metadata handling

### RTStream
- tile-aware transmission
- selective retransmission
- partial delivery strategies
- future layered transport support

### RTCloud
- storage with provenance and integrity metadata
- chunk-aware persistence
- controlled export workflows

---

## Honest comparison with existing formats

### PNG
PNG remains stronger for broad lossless interoperability and universal support.
RTImg can be better for tile-level resilience and internal metadata workflows.

### JPEG
JPEG remains strong for ubiquitous photographic distribution.
RTImg is more appropriate as a controlled internal format.

### WebP
WebP is a strong general-purpose web format.
RTImg is more system-oriented and operationally structured.

### AVIF
AVIF is stronger for aggressive modern compression.
RTImg should not try to outcompete AVIF in v0.

### JPEG XL
JPEG XL is technically closer in ambition to what a modern image system can be.
RTImg still makes sense if its advantage is ecosystem integration, resilience, and controlled transport.

---

## Repository layout

```text
rtimg/
├── LICENSE
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── docs/
│   ├── rtimg-overview.md
│   ├── bitstream-spec.md
│   ├── lossless-profile.md
│   ├── lossy-profile-draft.md
│   ├── metadata-tlv.md
│   ├── rtstack-integration.md
│   └── test-vectors.md
├── specs/
│   ├── rtimg-v0.1.md
│   ├── rtimg-header.md
│   ├── rtimg-tile-packet.md
│   └── rtimg-metadata.md
├── reference/
│   ├── python/
│   │   └── rtimg_v0.py
│   ├── c/
│   │   ├── include/
│   │   │   └── rtimg.h
│   │   ├── src/
│   │   │   ├── parser.c
│   │   │   ├── encoder.c
│   │   │   ├── decoder.c
│   │   │   └── crc32.c
│   │   └── tests/
│   └── rust/
│       ├── rtimg-core/
│       ├── rtimg-cli/
│       └── tests/
├── testdata/
│   ├── input/
│   ├── encoded/
│   ├── decoded/
│   └── corpus/
├── tools/
│   ├── inspect_rtimg.py
│   ├── gen_test_vectors.py
│   └── compare_psnr.py
├── tests/
│   ├── test_roundtrip.py
│   ├── test_parser.py
│   ├── test_tiles.py
│   ├── test_metadata.py
│   └── test_corruption.py
└── ci/
    └── github-actions/
```

---

## Roadmap

### Phase 0 — Specification draft
- define header
- define metadata model
- define tile packets
- reserve profiles and flags

### Phase 1 — Python reference implementation
- parser
- inspector
- encoder
- decoder
- roundtrip tests

### Phase 2 — Public v0.1 spec freeze
- freeze header and tile format
- publish test vectors
- validate compatibility rules

### Phase 3 — C implementation
- parser first
- decoder second
- encoder third
- focus on performance and deployability

### Phase 4 — Rust implementation
- safe bitstream parsing
- reusable core crates
- CLI and service integration

### Phase 5 — Experimental lossy profile
- color transform support
- transform coding
- quantization
- quality modes
- metric benchmarking

### Phase 6 — RT ecosystem integration
- RTCore ingestion
- RTStream transport
- RTCloud persistence and governance

---

## Reference prototype

A first prototype can begin in Python for speed of iteration and spec validation.

Suggested starting points:

- Pillow for image IO
- zlib for initial entropy compression
- CRC32 for tile integrity checks
- simple predictors such as:
  - none
  - left
  - up
  - average
  - paeth

The Python version should be treated as:

- a reference implementation
- a test-vector generator
- a parser validation tool

not as the final performance target.

---

## Long-term goals

RTImg should evolve into a format that supports:

- exact internal normalization
- tile-aware resilience
- partial region decode
- strong provenance metadata
- deterministic pipelines
- controlled external interoperability
- future transport and cloud-native workflows

---

## Contributing

At this stage, contributions are most useful in these areas:

- bitstream review
- parser design validation
- lossless test vectors
- metadata model review
- corruption and resilience testing
- C and Rust port planning

---

## License

Recommended: permissive open source licensing for adoption and review.

Good candidates:

- MIT
- Apache-2.0

Choose based on whether patent language and explicit contribution terms are desired.

---

## Summary

RTImg is an open-source, native RT Stack image codec focused on:

- deterministic internal representation
- tile-based resilience
- extensible open bitstream design
- future integration with RTCore, RTStream, and RTCloud

Its strongest initial path is a **lossless-first implementation** with an architecture ready for future lossy evolution.
