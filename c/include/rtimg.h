#ifndef RTIMG_H
#define RTIMG_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RTIMG_MAGIC "RTI0"
#define RTIMG_VERSION_MAJOR 0
#define RTIMG_VERSION_MINOR 1

#define RTIMG_PROFILE_LOSSLESS 0

#define RTIMG_COLORSPACE_GRAY 0
#define RTIMG_COLORSPACE_RGB  1
#define RTIMG_COLORSPACE_RGBA 2

#define RTIMG_ENTROPY_RAW  0
#define RTIMG_ENTROPY_ZLIB 1

#define RTIMG_PRED_NONE  0
#define RTIMG_PRED_LEFT  1
#define RTIMG_PRED_UP    2
#define RTIMG_PRED_AVG   3
#define RTIMG_PRED_PAETH 4

#define RTIMG_FLAG_ALPHA_PRESENT     (1u << 0)
#define RTIMG_FLAG_METADATA_PRESENT  (1u << 1)
#define RTIMG_FLAG_TILES_INDEPENDENT (1u << 2)
#define RTIMG_FLAG_TILE_CRC_PRESENT  (1u << 3)

#define RTIMG_OK 0
#define RTIMG_ERR_IO -1
#define RTIMG_ERR_MAGIC -2
#define RTIMG_ERR_VERSION -3
#define RTIMG_ERR_FORMAT -4
#define RTIMG_ERR_UNSUPPORTED -5
#define RTIMG_ERR_MEMORY -6
#define RTIMG_ERR_CHECKSUM -7

typedef struct rtimg_header_s {
    char magic[4];
    uint8_t version_major;
    uint8_t version_minor;
    uint8_t profile_id;
    uint8_t flags;
    uint32_t width;
    uint32_t height;
    uint8_t channels;
    uint8_t bit_depth;
    uint8_t color_space;
    uint8_t reserved;
    uint16_t tile_width;
    uint16_t tile_height;
    uint8_t predictor_id;
    uint8_t entropy_codec_id;
    uint16_t metadata_count;
    uint32_t tile_count;
} rtimg_header_t;

typedef struct rtimg_tile_s {
    uint32_t x;
    uint32_t y;
    uint16_t w;
    uint16_t h;
    uint32_t raw_len;
    uint32_t comp_len;
    uint32_t crc32;
    uint8_t *payload;
} rtimg_tile_t;

typedef struct rtimg_metadata_entry_s {
    char *key;
    char *value;
} rtimg_metadata_entry_t;

typedef struct rtimg_file_s {
    rtimg_header_t header;
    rtimg_metadata_entry_t *metadata;
    size_t metadata_len;
    rtimg_tile_t *tiles;
    size_t tile_len;
} rtimg_file_t;

int rtimg_parse_file(const char *path, rtimg_file_t *out_file);
void rtimg_free_file(rtimg_file_t *file);

int rtimg_decode_lossless_tile(
    const uint8_t *residuals,
    size_t residual_len,
    uint16_t tile_width,
    uint16_t tile_height,
    uint8_t channels,
    uint8_t predictor_id,
    uint8_t *out_pixels,
    size_t out_len
);

int rtimg_encode_lossless_tile(
    const uint8_t *pixels,
    size_t pixel_len,
    uint16_t tile_width,
    uint16_t tile_height,
    uint8_t channels,
    uint8_t predictor_id,
    uint8_t *out_residuals,
    size_t out_len
);

uint32_t rtimg_crc32(const uint8_t *data, size_t len);

#ifdef __cplusplus
}
#endif

#endif
