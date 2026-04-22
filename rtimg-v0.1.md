# RTImg Specification v0.1 Draft

**Document status:** Draft 0.1  
**Project:** RTImg  
**Organization:** Rethra Communications  
**Ecosystem:** RT Stack  
**Codec family meaning:** `RT` = **Resilient Transmission**

---

## 1. Purpose

This document defines the initial draft specification for **RTImg**, the native image codec of the **RT Stack** ecosystem.

RTImg is intended to serve as:

- an internal canonical image representation
- a deterministic image transport/storage format
- a tile-oriented codec with future streaming support
- an extensible binary format suitable for reference implementations in Python, C, and Rust

This version focuses on a **lossless-first profile** while reserving structural space for future lossy extensions.

---

## 2. Scope of v0.1

RTImg v0.1 defines:

- binary file identification
- core header format
- metadata section model
- tile descriptor model
- payload encoding rules for a baseline lossless profile
- decoder validation expectations
- forward-compatibility principles

RTImg v0.1 does **not** standardize:

- a stable lossy transform profile
- progressive/layered transport
- HDR or wide-gamut advanced semantics
- hardware acceleration APIs
- streaming container encapsulation

---

## 3. Design goals

RTImg v0.1 is designed to satisfy the following goals:

1. **Open specification**  
   The format must be public and implementable by third parties.

2. **Deterministic decode**  
   A compliant decoder must produce a stable decoded result from a valid file.

3. **Tile independence**  
   Tile payloads should be independently validated and reconstructed.

4. **Operational metadata support**  
   Files may carry machine-readable metadata relevant to RT pipelines.

5. **Future profile extensibility**  
   The bitstream must reserve fields for future evolution.

6. **Practical reference implementation path**  
   A Python implementation must be sufficient to validate the format design.

---

## 4. Terminology

### 4.1 Pixel
A sample location in the 2D raster addressed by coordinates `(x, y)`.

### 4.2 Channel
A component of a pixel value, such as:

- grayscale `L`
- red `R`
- green `G`
- blue `B`
- alpha `A`

### 4.3 Tile
A rectangular region of the image encoded as a separate unit in the bitstream.

### 4.4 Predictor
A rule that estimates the current sample value using previously reconstructed neighbor samples.

### 4.5 Residual
The difference between the original sample and the predicted sample under the selected profile rules.

### 4.6 Profile
A constrained coding mode under the RTImg format family.

---

## 5. Profiles

RTImg reserves multiple profile classes.

### 5.1 Profile 0 — Lossless baseline
This is the mandatory baseline profile for v0.1 reference work.

Characteristics:

- exact reconstruction
- tile-based coding
- spatial prediction allowed
- entropy compression allowed
- no quantization
- no irreversible transform

### 5.2 Reserved future profiles
The following profile categories are reserved for future versions:

- lossy transform profile
- hybrid profile
- progressive/layered profile
- streaming-optimized profile

A decoder that encounters an unsupported profile identifier must fail gracefully.

---

## 6. Supported image model in v0.1 baseline

The recommended mandatory support for the baseline reference implementation is:

- grayscale `L`
- `RGB`
- `RGBA`
- 8-bit unsigned integer samples

### 6.1 Deferred capabilities
These are reserved but not required in v0.1 baseline:

- 10-bit
- 12-bit
- 16-bit
- YCbCr
- ICC profile embedding
- floating-point channels
- HDR metadata

---

## 7. File structure overview

A conforming RTImg file is composed of the following ordered sections:

```text
[FIXED HEADER]
[METADATA SECTION]
[TILE RECORD 0]
[TILE RECORD 1]
...
[TILE RECORD N-1]
```

Each tile record is composed of:

```text
[TILE DESCRIPTOR]
[TILE PAYLOAD]
```

---

## 8. Fixed header

### 8.1 Header purpose
The fixed header identifies the file and communicates the parameters required to parse subsequent sections.

### 8.2 Recommended field layout
A practical baseline header should include at least the following fields:

| Field | Type | Description |
|---|---:|---|
| magic | 4 bytes | ASCII signature, recommended `RTI0` |
| version_major | u8 | major format version |
| version_minor | u8 | minor format version |
| profile_id | u8 | active coding profile |
| flags | u32 | global feature flags |
| width | u32 | image width in pixels |
| height | u32 | image height in pixels |
| channels | u8 | channel count |
| bit_depth | u8 | bits per channel |
| color_space_id | u8 | color space identifier |
| tile_width | u16 | nominal tile width |
| tile_height | u16 | nominal tile height |
| predictor_id | u8 | baseline predictor mode |
| entropy_codec_id | u8 | payload compression mode |
| metadata_count | u16 | number of metadata entries |
| tile_count | u32 | number of tile records |
| reserved | bytes | reserved for future evolution |

### 8.3 Required header validation
A decoder must reject the file if:

- the magic value is invalid
- the major version is unsupported
- width or height is zero
- channels is zero
- tile dimensions are zero
- tile_count is inconsistent with image geometry
- profile_id is unsupported

---

## 9. Flags

The `flags` field is a bitmask.

### 9.1 Recommended initial bit assignments

| Bit | Name | Meaning |
|---:|---|---|
| 0 | ALPHA_PRESENT | image includes alpha semantics |
| 1 | METADATA_PRESENT | metadata section is present |
| 2 | TILES_INDEPENDENT | each tile is independently decodable |
| 3 | TILE_CRC_PRESENT | each tile includes a CRC/checksum |
| 4 | RESERVED_PROGRESSIVE | reserved |
| 5 | RESERVED_LAYERS | reserved |
| 6-31 | RESERVED | reserved for future versions |

A decoder must ignore reserved bits it does not understand unless those bits imply a required feature in a future major version.

---

## 10. Color space identifiers

### 10.1 Baseline recommended identifiers

| ID | Name |
|---:|---|
| 0 | Unknown / implementation-defined |
| 1 | Grayscale |
| 2 | RGB |
| 3 | RGBA |
| 4+ | Reserved |

Future versions may define:

- YCbCr
- linear RGB
- wide-gamut RGB variants
- HDR-oriented encodings

---

## 11. Metadata section

### 11.1 Purpose
RTImg metadata is intended to support operational, provenance, and policy-oriented workflows.

### 11.2 Format model
A simple TLV-inspired metadata entry format is recommended:

```text
[key_length][value_length][key_bytes][value_bytes]
```

Recommended integer sizes:

- `key_length`: `u16`
- `value_length`: `u32`

Strings should be UTF-8 unless otherwise stated by key convention.

### 11.3 Metadata ordering
Metadata entries should be preserved in file order.

### 11.4 Duplicate keys
Duplicate keys are allowed unless a higher-level profile forbids them.
Consumers may apply last-write-wins or preserve all entries, depending on use case.

### 11.5 Suggested metadata keys

- `codec`
- `profile`
- `source_filename`
- `source_format`
- `created_by`
- `pipeline_id`
- `asset_id`
- `integrity_hash`
- `capture_timestamp`
- `transcode_history`
- `export_policy`

---

## 12. Tile model

### 12.1 Tile geometry
Tiles partition the image into rectangular regions.

Nominal tile dimensions are declared in the header, but edge tiles may be smaller.

### 12.2 Tile ordering
The baseline ordering should be row-major by tile origin:

- left to right
- top to bottom

### 12.3 Tile independence
Under the lossless baseline profile, tiles are recommended to be independently decodable.

### 12.4 Tile descriptor fields
Each tile descriptor should include at least:

| Field | Type | Description |
|---|---:|---|
| tile_x | u32 | tile origin x |
| tile_y | u32 | tile origin y |
| tile_width | u16 | actual tile width |
| tile_height | u16 | actual tile height |
| raw_size | u32 | uncompressed tile byte count |
| payload_size | u32 | encoded payload byte count |
| crc32 | u32 | checksum of payload or logical tile data |
| reserved | bytes | future use |

### 12.5 Tile validation
A decoder must reject or mark invalid a tile if:

- payload_size is inconsistent with file boundaries
- raw_size is inconsistent with image mode expectations
- tile geometry exceeds image bounds
- crc validation fails when CRC is mandatory under flags or profile rules

---

## 13. Baseline lossless coding model

### 13.1 Overview
The baseline lossless profile is predictor-based.

Each tile is represented as:

1. normalized pixel samples
2. optional spatial prediction
3. residual stream
4. entropy-compressed payload

### 13.2 Sample domain
For the baseline profile, each channel sample is treated as an unsigned 8-bit integer.

### 13.3 Predictors
Recommended baseline predictor identifiers:

| ID | Name | Rule |
|---:|---|---|
| 0 | NONE | predictor = 0 |
| 1 | LEFT | predictor = left sample |
| 2 | UP | predictor = upper sample |
| 3 | AVG | predictor = floor((left + up) / 2) |
| 4 | PAETH | Paeth predictor |

Predictors must operate on already reconstructed neighbor samples.

### 13.4 Boundary handling
At tile boundaries:

- missing left neighbor is treated as zero
- missing upper neighbor is treated as zero
- missing upper-left neighbor is treated as zero

unless a future profile explicitly changes those rules.

### 13.5 Residual definition
For 8-bit samples, a practical modular reversible residual model is:

```text
residual = (sample - predictor) mod 256
```

Reconstruction:

```text
sample = (predictor + residual) mod 256
```

Any compliant encoder/decoder pair must use exactly the same reversible rule for the declared profile.

---

## 14. Entropy payload encoding

### 14.1 Baseline recommendation
For the reference prototype, payloads may be stored using:

- `RAW` (uncompressed)
- `ZLIB` (deflate-based)

### 14.2 Entropy codec identifiers

| ID | Name |
|---:|---|
| 0 | RAW |
| 1 | ZLIB |
| 2+ | Reserved |

### 14.3 Future codecs
Future versions may define:

- Huffman-coded streams
- Rice coding
- ANS / rANS
- profile-specific entropy coders

---

## 15. Decoder process

A compliant baseline decoder should perform these steps:

1. read the fixed header
2. validate header fields
3. parse metadata entries
4. allocate image output buffer
5. iterate tile records in order
6. validate tile geometry and payload length
7. decode the tile payload using the declared entropy codec
8. reconstruct samples using the declared predictor
9. write reconstructed samples into the final raster
10. expose the reconstructed image to the caller

---

## 16. Integrity and corruption handling

### 16.1 Objective
RTImg is intended to support resilient transport and storage workflows.

### 16.2 Per-tile integrity
Per-tile CRC32 is strongly recommended in v0.1 reference implementations.

### 16.3 Error behavior
A decoder may support one of these behaviors depending on application policy:

- hard fail on first invalid tile
- soft fail and mark damaged regions
- partial decode with corruption reporting

The chosen behavior should be explicit in the implementation documentation.

---

## 17. Mathematical foundations

### 17.1 Raster model
An image is defined over a 2D grid of dimensions:

- width `W`
- height `H`

### 17.2 Channel model
Each pixel carries `C` channel samples.

### 17.3 Prediction
Prediction exploits local spatial correlation in natural images.

### 17.4 Residuals
Residuals tend to have lower entropy than raw samples when prediction is effective.

### 17.5 Lossless reconstruction
No quantization is applied in the baseline profile.
Therefore, exact recovery is required.

### 17.6 Future lossy math
Future lossy profiles may introduce:

- color transforms
- block transforms such as DCT
- quantization matrices
- quality/rate control
- perceptual optimization

Those are explicitly outside the guaranteed v0.1 baseline.

---

## 18. Quality metrics

For the lossless baseline profile:

- mean squared error (MSE) = 0 for a valid roundtrip
- PSNR is mathematically infinite

For future lossy profiles, implementations should consider:

- MSE
- PSNR
- SSIM
- MS-SSIM

---

## 19. Compliance expectations

### 19.1 Encoder compliance
A compliant encoder must:

- write a valid header
- write correct tile descriptors
- obey the declared predictor and entropy codec rules
- produce payload sizes consistent with stored data

### 19.2 Decoder compliance
A compliant decoder must:

- reject invalid header combinations
- reject unsupported required features
- reconstruct a valid baseline image when given a compliant file

### 19.3 Parser compliance
A compliant parser-only tool must be able to:

- identify the file as RTImg
- parse the header
- enumerate metadata entries
- enumerate tile descriptors
- report structural errors

---

## 20. Versioning policy

### 20.1 Major version changes
A major version increment is required when a bitstream change breaks compatibility.

### 20.2 Minor version changes
A minor version increment may be used when:

- optional fields are added in a backward-compatible way
- reserved identifiers are defined without breaking existing valid decoders

### 20.3 Unknown features
A decoder must fail clearly when it encounters a required feature it cannot interpret.

---

## 21. Security considerations

Implementations must guard against:

- integer overflow in dimension math
- malformed metadata lengths
- out-of-bounds tile geometry
- compressed payload bombs
- unchecked allocation sizes
- parser ambiguity from reserved fields misuse

Reference implementations should validate all lengths before allocation and decode.

---

## 22. Interoperability model

RTImg is designed for **controlled interoperability**.

### 22.1 Import
External formats may be imported into RT workflows and normalized into RTImg.

### 22.2 Internal processing
Inside the RT ecosystem, RTImg is the preferred working representation.

### 22.3 Export
External delivery formats should be produced through explicit export or decode workflows.

This separation is intentional and part of the system design.

---

## 23. Recommended implementation order

The practical implementation order is:

1. parser
2. inspector
3. decoder
4. encoder
5. test-vector generator
6. C port
7. Rust port
8. experimental lossy branch

---

## 24. Reference implementation guidance

### 24.1 Python
Python is recommended for the first reference implementation because it allows rapid iteration on:

- bitstream design
- parser validation
- roundtrip testing
- metadata handling
- golden vector creation

### 24.2 C
C is recommended for:

- portable decoder deployment
- performance-sensitive integration
- low-level systems use

### 24.3 Rust
Rust is recommended for:

- safer parser implementations
- cloud services
- strong library ergonomics
- modern CLI tooling

---

## 25. Deferred work

The following topics are intentionally deferred beyond v0.1:

- lossy transform pipeline
- quantization design
- YCbCr normative signaling
- progressive transport syntax
- multi-resolution layers
- ROI prioritization syntax
- SIMD/parallel codec intrinsics
- streaming framing over RTStream

---

## 26. Example implementation notes for v0.1 prototype

A practical first prototype may use:

- Python
- Pillow for image IO
- `zlib` for entropy coding
- `crc32` for tile validation
- predictors: none, left, up, average, paeth

This is acceptable for v0.1 prototyping even though it is not the final performance design.

---

## 27. Summary

RTImg v0.1 defines a realistic foundation for an open RT-native image format based on:

- deterministic decoding
- tile-oriented structure
- metadata support
- lossless baseline reconstruction
- future extensibility toward lossy and streaming-aware profiles

Its main value is not universal replacement of existing image standards, but robust integration into the RT Stack ecosystem.
