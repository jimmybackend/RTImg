# RTImg Bitstream Specification

## 1. Alcance

Este documento describe la estructura del contenedor binario RTImg en su estado actual de diseño. Debe leerse junto con `specs/rtimg-v0.1.md`, pero aquí se presenta una visión más operativa y byte-oriented del formato.

La meta es dar una base suficientemente precisa para:

- implementar parser
- implementar inspector
- estabilizar encoder/decoder
- generar test vectors

---

## 2. Convenciones

### Endianness
Todos los enteros multibyte se codifican en **little-endian**.

### Tipos
- `u8`: entero sin signo de 8 bits
- `u16`: entero sin signo de 16 bits
- `u32`: entero sin signo de 32 bits
- `u64`: entero sin signo de 64 bits

### Strings
Las cadenas se almacenan como bytes UTF-8 sin terminador nulo, salvo que un campo indique otra cosa.

---

## 3. Layout general del archivo

```text
[FILE HEADER]
[METADATA SECTION]
[TILE RECORD 0]
[TILE RECORD 1]
...
[TILE RECORD N-1]
```

El parser debe poder leer la cabecera y recorrer los records de tile sin necesidad de decodificar los payloads.

---

## 4. File Header

### 4.1 Propósito
Identificar el archivo y aportar todos los parámetros necesarios para parsear las secciones siguientes.

### 4.2 Estructura lógica

| Offset | Campo | Tipo | Descripción |
|---:|---|---|---|
| 0 | magic | 4 bytes | ASCII `RTI0` |
| 4 | version_major | u8 | versión mayor |
| 5 | version_minor | u8 | versión menor |
| 6 | profile_id | u8 | perfil activo |
| 7 | header_size | u8 | tamaño total de cabecera fija |
| 8 | flags | u32 | flags globales |
| 12 | width | u32 | ancho total |
| 16 | height | u32 | alto total |
| 20 | channels | u8 | número de canales |
| 21 | bit_depth | u8 | bits por canal |
| 22 | color_space_id | u8 | espacio de color |
| 23 | sample_format_id | u8 | representación de muestra |
| 24 | tile_width | u16 | ancho nominal de tile |
| 26 | tile_height | u16 | alto nominal de tile |
| 28 | predictor_id | u8 | predictor por defecto |
| 29 | entropy_codec_id | u8 | códec de entropía del payload |
| 30 | metadata_count | u16 | cantidad de entradas metadata |
| 32 | tile_count | u32 | número total de tiles |
| 36 | metadata_section_size | u32 | tamaño total de metadata |
| 40 | reserved | 24 bytes | reservado para evolución |

### 4.3 Reglas mínimas
- `magic` debe ser exactamente `RTI0`
- `header_size` no puede ser menor que la cabecera conocida
- `width`, `height`, `tile_width`, `tile_height` deben ser > 0
- `channels` debe ser compatible con el modo de color
- `tile_count` debe coincidir con la teselación de la imagen
- `metadata_section_size` puede ser cero solo si `metadata_count == 0`

---

## 5. Identificadores recomendados

### 5.1 `profile_id`
| ID | Significado |
|---:|---|
| 0 | lossless baseline |
| 1 | lossy experimental |
| 2-15 | reservados |

### 5.2 `color_space_id`
| ID | Significado |
|---:|---|
| 0 | grayscale |
| 1 | RGB |
| 2 | RGBA |
| 3 | YCbCr |
| 4-15 | reservados |

### 5.3 `sample_format_id`
| ID | Significado |
|---:|---|
| 0 | unsigned integer |
| 1 | signed integer |
| 2 | float |
| 3-15 | reservados |

### 5.4 `predictor_id`
| ID | Predictor |
|---:|---|
| 0 | none |
| 1 | left |
| 2 | up |
| 3 | average |
| 4 | paeth |

### 5.5 `entropy_codec_id`
| ID | Codec |
|---:|---|
| 0 | raw |
| 1 | zlib |
| 2 | rice (reservado) |
| 3 | huffman (reservado) |
| 4 | rANS (reservado) |

---

## 6. Flags globales

| Bit | Nombre | Descripción |
|---:|---|---|
| 0 | ALPHA_PRESENT | la imagen incluye alpha |
| 1 | METADATA_PRESENT | existe metadata section |
| 2 | TILES_INDEPENDENT | cada tile puede procesarse aisladamente |
| 3 | TILE_CRC_PRESENT | hay CRC32 por tile |
| 4 | TILE_OFFSETS_PRESENT | reservado para tabla de offsets |
| 5 | REGION_DECODABLE_HINT | reservado para acceso parcial optimizado |
| 6-31 | RESERVED | uso futuro |

---

## 7. Metadata Section

La sección de metadata aparece inmediatamente después de la cabecera fija.

### 7.1 Estructura
Consiste en `metadata_count` entradas TLV consecutivas. Cada entrada tiene:

```text
[key_len:u16]
[value_len:u32]
[key:key_len bytes UTF-8]
[value:value_len bytes UTF-8]
```

### 7.2 Reglas
- las claves deben ser únicas dentro del archivo
- el parser puede ignorar claves desconocidas
- el decoder no debe fallar por una metadata no comprendida, salvo corrupción estructural

---

## 8. Tile Record

Cada tile se almacena como un record autocontenido desde el punto de vista de parsing.

### 8.1 Tile Descriptor

| Campo | Tipo | Descripción |
|---|---|---|
| tile_x | u32 | coordenada X del origen del tile |
| tile_y | u32 | coordenada Y del origen del tile |
| tile_w | u16 | ancho real del tile |
| tile_h | u16 | alto real del tile |
| predictor_override | u8 | 255 = usar predictor global |
| entropy_override | u8 | 255 = usar entropía global |
| reserved0 | u16 | reservado |
| raw_size | u32 | tamaño antes de compresión |
| encoded_size | u32 | tamaño después de compresión |
| crc32 | u32 | checksum del payload codificado |

### 8.2 Tile Payload
Bloque opaco de `encoded_size` bytes. Su interpretación depende del perfil activo y del códec de entropía aplicable.

---

## 9. Geometría de tiles

El número de tiles se calcula como:

- `tiles_x = ceil(width / tile_width)`
- `tiles_y = ceil(height / tile_height)`
- `tile_count = tiles_x * tiles_y`

Los tiles del borde pueden tener dimensiones menores que las nominales.

Orden recomendado de almacenamiento:
- raster order, de arriba a abajo y de izquierda a derecha

---

## 10. Payload del perfil lossless

Para el perfil baseline lossless, el payload decodificado representa muestras reconstruibles mediante:

1. orden de recorrido raster dentro del tile
2. predictor espacial por canal
3. residuo entero
4. reconstrucción modular dentro del rango del bit depth

Para 8 bits:
- codificación modular módulo `256`

En una versión posterior con profundidades mayores:
- módulo `2^bit_depth`

---

## 11. Validaciones de parser y decoder

### Parser
- validar que no existan lecturas fuera de rango
- comprobar consistencia básica de tamaños
- validar que `encoded_size` no desborde el archivo

### Decoder
- validar compatibilidad de perfil
- validar integridad del payload si hay CRC
- rechazar predictors o entropy codecs no soportados
- rechazar tiles cuya geometría salga de la imagen

---

## 12. Extensiones previstas

El bitstream se diseña para soportar en el futuro:

- tablas de offsets para acceso aleatorio
- capas o calidad progresiva
- substreams de preview
- YCbCr y perfiles perceptuales
- cuantización y transformada
- chunking especializado para RTStream

Estas extensiones deben añadirse sin romper el principio de parsing robusto y versionado explícito.
