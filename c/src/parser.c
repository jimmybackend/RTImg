#include "rtimg.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int read_exact(FILE *fp, void *buf, size_t len) {
    return fread(buf, 1, len, fp) == len ? RTIMG_OK : RTIMG_ERR_IO;
}

static int validate_header(const rtimg_header_t *h) {
    if (memcmp(h->magic, RTIMG_MAGIC, 4) != 0) return RTIMG_ERR_MAGIC;
    if (h->version_major != RTIMG_VERSION_MAJOR) return RTIMG_ERR_VERSION;
    if (h->width == 0 || h->height == 0 || h->channels == 0 || h->bit_depth == 0) return RTIMG_ERR_FORMAT;
    if (h->tile_width == 0 || h->tile_height == 0) return RTIMG_ERR_FORMAT;
    return RTIMG_OK;
}

static int read_metadata(FILE *fp, rtimg_file_t *out_file) {
    uint16_t i;
    out_file->metadata_len = out_file->header.metadata_count;
    if (out_file->metadata_len == 0) return RTIMG_OK;
    out_file->metadata = calloc(out_file->metadata_len, sizeof(rtimg_metadata_entry_t));
    if (!out_file->metadata) return RTIMG_ERR_MEMORY;
    for (i = 0; i < out_file->header.metadata_count; ++i) {
        uint16_t key_len = 0;
        uint32_t value_len = 0;
        if (read_exact(fp, &key_len, sizeof(key_len)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &value_len, sizeof(value_len)) != RTIMG_OK) return RTIMG_ERR_IO;
        out_file->metadata[i].key = calloc((size_t)key_len + 1u, 1u);
        out_file->metadata[i].value = calloc((size_t)value_len + 1u, 1u);
        if (!out_file->metadata[i].key || !out_file->metadata[i].value) return RTIMG_ERR_MEMORY;
        if (read_exact(fp, out_file->metadata[i].key, key_len) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, out_file->metadata[i].value, value_len) != RTIMG_OK) return RTIMG_ERR_IO;
    }
    return RTIMG_OK;
}

static int read_tiles(FILE *fp, rtimg_file_t *out_file) {
    uint32_t i;
    out_file->tile_len = out_file->header.tile_count;
    if (out_file->tile_len == 0) return RTIMG_OK;
    out_file->tiles = calloc(out_file->tile_len, sizeof(rtimg_tile_t));
    if (!out_file->tiles) return RTIMG_ERR_MEMORY;
    for (i = 0; i < out_file->header.tile_count; ++i) {
        rtimg_tile_t *tile = &out_file->tiles[i];
        if (read_exact(fp, &tile->x, sizeof(tile->x)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->y, sizeof(tile->y)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->w, sizeof(tile->w)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->h, sizeof(tile->h)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->raw_len, sizeof(tile->raw_len)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->comp_len, sizeof(tile->comp_len)) != RTIMG_OK) return RTIMG_ERR_IO;
        if (read_exact(fp, &tile->crc32, sizeof(tile->crc32)) != RTIMG_OK) return RTIMG_ERR_IO;
        tile->payload = malloc(tile->comp_len);
        if (!tile->payload) return RTIMG_ERR_MEMORY;
        if (read_exact(fp, tile->payload, tile->comp_len) != RTIMG_OK) return RTIMG_ERR_IO;
        if ((out_file->header.flags & RTIMG_FLAG_TILE_CRC_PRESENT) != 0u && rtimg_crc32(tile->payload, tile->comp_len) != tile->crc32) {
            return RTIMG_ERR_CHECKSUM;
        }
    }
    return RTIMG_OK;
}

int rtimg_parse_file(const char *path, rtimg_file_t *out_file) {
    FILE *fp;
    int rc;
    if (!path || !out_file) return RTIMG_ERR_FORMAT;
    memset(out_file, 0, sizeof(*out_file));
    fp = fopen(path, "rb");
    if (!fp) return RTIMG_ERR_IO;
    rc = read_exact(fp, &out_file->header, sizeof(out_file->header));
    if (rc == RTIMG_OK) rc = validate_header(&out_file->header);
    if (rc == RTIMG_OK) rc = read_metadata(fp, out_file);
    if (rc == RTIMG_OK) rc = read_tiles(fp, out_file);
    fclose(fp);
    if (rc != RTIMG_OK) rtimg_free_file(out_file);
    return rc;
}

void rtimg_free_file(rtimg_file_t *file) {
    size_t i;
    if (!file) return;
    if (file->metadata) {
        for (i = 0; i < file->metadata_len; ++i) {
            free(file->metadata[i].key);
            free(file->metadata[i].value);
        }
        free(file->metadata);
    }
    if (file->tiles) {
        for (i = 0; i < file->tile_len; ++i) free(file->tiles[i].payload);
        free(file->tiles);
    }
    memset(file, 0, sizeof(*file));
}
