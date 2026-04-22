#include "rtimg.h"

static uint8_t rtimg_paeth(uint8_t a, uint8_t b, uint8_t c) {
    int p = (int)a + (int)b - (int)c;
    int pa = p > a ? p - a : a - p;
    int pb = p > b ? p - b : b - p;
    int pc = p > c ? p - c : c - p;
    if (pa <= pb && pa <= pc) return a;
    if (pb <= pc) return b;
    return c;
}

static uint8_t rtimg_predict(uint8_t predictor_id, uint8_t left, uint8_t up, uint8_t up_left) {
    switch (predictor_id) {
        case RTIMG_PRED_NONE: return 0;
        case RTIMG_PRED_LEFT: return left;
        case RTIMG_PRED_UP: return up;
        case RTIMG_PRED_AVG: return (uint8_t)(((uint16_t)left + (uint16_t)up) / 2u);
        case RTIMG_PRED_PAETH: return rtimg_paeth(left, up, up_left);
        default: return 0;
    }
}

int rtimg_decode_lossless_tile(const uint8_t *residuals, size_t residual_len, uint16_t tile_width, uint16_t tile_height, uint8_t channels, uint8_t predictor_id, uint8_t *out_pixels, size_t out_len) {
    size_t expected = (size_t)tile_width * (size_t)tile_height * (size_t)channels;
    size_t stride = (size_t)tile_width * (size_t)channels;
    size_t y, x;
    uint8_t c;

    if (!residuals || !out_pixels) return RTIMG_ERR_FORMAT;
    if (residual_len != expected || out_len != expected) return RTIMG_ERR_FORMAT;

    for (y = 0; y < tile_height; ++y) {
        size_t row_off = y * stride;
        size_t prev_row_off = (y == 0) ? 0 : ((y - 1) * stride);
        for (x = 0; x < tile_width; ++x) {
            for (c = 0; c < channels; ++c) {
                size_t idx = row_off + (x * channels) + c;
                uint8_t left = (x > 0) ? out_pixels[idx - channels] : 0;
                uint8_t up = (y > 0) ? out_pixels[prev_row_off + (x * channels) + c] : 0;
                uint8_t up_left = (x > 0 && y > 0) ? out_pixels[prev_row_off + ((x - 1) * channels) + c] : 0;
                uint8_t pred = rtimg_predict(predictor_id, left, up, up_left);
                out_pixels[idx] = (uint8_t)((pred + residuals[idx]) & 0xFFu);
            }
        }
    }

    return RTIMG_OK;
}
