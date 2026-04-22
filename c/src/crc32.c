#include "rtimg.h"

uint32_t rtimg_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFu;
    size_t i;
    int bit;

    for (i = 0; i < len; ++i) {
        crc ^= (uint32_t)data[i];
        for (bit = 0; bit < 8; ++bit) {
            crc = (crc & 1u) ? ((crc >> 1) ^ 0xEDB88320u) : (crc >> 1);
        }
    }

    return crc ^ 0xFFFFFFFFu;
}
