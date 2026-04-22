# Especificación RTImg v0.1 (Draft)

**Estado del documento:** Draft 0.1  
**Proyecto:** RTImg  
**Organización:** Rethra Communications  
**Ecosistema:** RT Stack  
**Significado de RT:** Resilient Transmission

---

## 1. Propósito

Este documento define la especificación inicial de **RTImg**, el códec de imagen nativo del ecosistema **RT Stack**.

RTImg está pensado para servir como:

- representación canónica interna de imagen
- formato binario determinista para almacenamiento y transporte
- códec orientado a tiles con proyección futura a streaming
- base de referencia implementable en Python, C y Rust

Esta versión se centra en un perfil **lossless-first**, reservando espacio estructural para futuras extensiones lossy.

---

## 2. Alcance de la v0.1

RTImg v0.1 define:

- identificación binaria del archivo
- formato de cabecera principal
- modelo de metadata
- modelo de descriptor de tile
- reglas de payload para un perfil base lossless
- validaciones mínimas del decoder
- principios de compatibilidad futura

No estandariza todavía:

- un perfil lossy estable
- transporte progresivo o por capas
- HDR o wide gamut
- APIs de aceleración hardware
- encapsulación final para streaming en RTStream

---

## 3. Objetivos de diseño

1. **Especificación abierta**  
   El formato debe poder ser implementado por terceros.

2. **Decodificación determinista**  
   Un decoder conforme debe reconstruir siempre el mismo resultado a partir de un archivo válido.

3. **Independencia por tile**  
   Cada tile debe poder validarse y reconstruirse como unidad separada.

4. **Metadata operativa**  
   El formato debe poder transportar datos útiles para pipelines reales.

5. **Extensibilidad de perfiles**  
   El bitstream debe reservar espacio para evolución futura.

6. **Ruta práctica de implementación**  
   Una referencia en Python debe ser suficiente para validar el diseño.

---

## 4. Terminología

### 4.1 Pixel
Ubicación de muestra dentro de la rejilla 2D, direccionada por coordenadas `(x, y)`.

### 4.2 Canal
Componente de un píxel, por ejemplo:

- `L`
- `R`
- `G`
- `B`
- `A`

### 4.3 Tile
Región rectangular de la imagen codificada como unidad separada del bitstream.

### 4.4 Predictor
Regla que estima el valor actual a partir de vecinos reconstruidos previamente.

### 4.5 Residuo
Diferencia entre el valor original y el valor predicho.

### 4.6 Perfil
Modo de codificación restringido dentro de la familia RTImg.

---

## 5. Perfiles

### 5.1 Perfil 0 — Lossless baseline
Perfil obligatorio de referencia para la v0.1.

Características:

- reconstrucción exacta
- codificación por tiles
- predicción espacial opcional
- compresión entrópica opcional
- sin cuantización
- sin transformada irreversible

### 5.2 Perfiles reservados
Se reservan para futuras versiones:

- perfil lossy con transformada
- perfil híbrido
- perfil progresivo o por capas
- perfil optimizado para streaming

Si un decoder encuentra un `profile_id` no soportado, debe fallar de forma controlada.

---

## 6. Modelo de imagen soportado en la baseline

Soporte recomendado para la implementación de referencia:

- `L`
- `RGB`
- `RGBA`
- muestras enteras sin signo de 8 bits

### 6.1 Capacidades diferidas
Reservadas pero no obligatorias en v0.1:

- 10 bits
- 12 bits
- 16 bits
- YCbCr
- perfiles ICC
- canales en coma flotante
- metadata HDR

---

## 7. Estructura general del archivo

Un archivo RTImg conforme se organiza así:

```text
[FIXED HEADER]
[METADATA SECTION]
[TILE RECORD 0]
[TILE RECORD 1]
...
[TILE RECORD N-1]
```

Cada tile record contiene:

```text
[TILE DESCRIPTOR]
[TILE PAYLOAD]
```

---

## 8. Cabecera fija

### 8.1 Propósito
La cabecera fija identifica el archivo y entrega los parámetros mínimos para parsear las secciones siguientes.

### 8.2 Campos mínimos recomendados

| Campo | Tipo | Descripción |
|---|---:|---|
| magic | 4 bytes | firma ASCII recomendada `RTI0` |
| version_major | u8 | versión mayor del formato |
| version_minor | u8 | versión menor del formato |
| profile_id | u8 | perfil activo |
| flags | u32 | flags globales |
| width | u32 | ancho en píxeles |
| height | u32 | alto en píxeles |
| channels | u8 | número de canales |
| bit_depth | u8 | bits por canal |
| color_space_id | u8 | identificador de color space |
| tile_width | u16 | ancho nominal de tile |
| tile_height | u16 | alto nominal de tile |
| predictor_id | u8 | predictor base |
| entropy_codec_id | u8 | compresión del payload |
| metadata_count | u16 | cantidad de entradas de metadata |
| tile_count | u32 | número de tiles |
| reserved | bytes | reservado para futuro |

### 8.3 Validaciones mínimas
El decoder debe rechazar el archivo si:

- `magic` es inválido
- la versión mayor no es soportada
- `width` o `height` valen cero
- `channels` vale cero
- `tile_width` o `tile_height` valen cero
- `tile_count` no coincide con la geometría de la imagen
- `profile_id` no es soportado

---

## 9. Flags

`flags` es un bitmask.

### 9.1 Asignación inicial recomendada

| Bit | Nombre | Significado |
|---:|---|---|
| 0 | ALPHA_PRESENT | la imagen incluye alpha |
| 1 | METADATA_PRESENT | existe sección de metadata |
| 2 | TILES_INDEPENDENT | cada tile es decodificable de forma independiente |
| 3 | TILE_CRC_PRESENT | cada tile incluye CRC/checksum |
| 4 | RESERVED_PROGRESSIVE | reservado |
| 5 | RESERVED_LAYERS | reservado |
| 6-31 | RESERVED | reservado |

El decoder debe ignorar bits reservados no comprendidos salvo que una versión futura indique que son obligatorios.

---

## 10. Color space identifiers

### 10.1 Identificadores base recomendados

| ID | Nombre |
|---:|---|
| 0 | Unknown / implementation-defined |
| 1 | Grayscale |
| 2 | RGB |
| 3 | RGBA |
| 4+ | Reservado |

Futuras versiones podrán definir:

- YCbCr
- RGB lineal
- variantes wide gamut
- perfiles orientados a HDR

---

## 11. Metadata

### 11.1 Objetivo
La metadata de RTImg debe soportar trazabilidad, control operacional y políticas de pipeline.

### 11.2 Modelo recomendado
Se recomienda una estructura tipo TLV simple.

Cada entrada puede representarse como:

```text
[key_len][value_len][key][value]
```

Donde:

- `key_len` = longitud de la clave
- `value_len` = longitud del valor
- `key` = UTF-8
- `value` = UTF-8

### 11.3 Claves sugeridas

- `codec`
- `profile`
- `source_filename`
- `origin_format`
- `created_by`
- `asset_id`
- `pipeline_id`
- `integrity_hash`
- `transcode_history`
- `capture_timestamp`

---

## 12. Tiles

### 12.1 Modelo
La imagen se divide en tiles rectangulares. Los tiles de borde pueden ser menores que el tamaño nominal.

### 12.2 Ventajas funcionales
Los tiles permiten:

- decodificación parcial
- paralelismo
- retransmisión selectiva
- aislamiento de corrupción
- integración natural con RTStream y RTCloud

### 12.3 Descriptor mínimo de tile

| Campo | Tipo | Descripción |
|---|---:|---|
| x | u32 | coordenada X del tile |
| y | u32 | coordenada Y del tile |
| w | u16 | ancho real del tile |
| h | u16 | alto real del tile |
| raw_len | u32 | longitud esperada del tile en bruto |
| comp_len | u32 | longitud del payload comprimido |
| crc32 | u32 | checksum del payload comprimido o reconstruido |

---

## 13. Camino lossless base

### 13.1 Flujo recomendado del encoder

1. leer imagen externa
2. normalizar a `L`, `RGB` o `RGBA`
3. dividir en tiles
4. aplicar predictor espacial por canal
5. calcular residuos
6. comprimir el payload
7. escribir cabecera, metadata y tiles

### 13.2 Predictores recomendados

- none
- left
- up
- avg
- paeth

### 13.3 Regla de residuo
Para 8 bits:

- `R = (X - P) mod 256`
- reconstrucción: `X = (P + R) mod 256`

Donde:

- `X` = muestra original
- `P` = predictor
- `R` = residuo

---

## 14. Entropía

La primera implementación de referencia puede usar:

- `raw`
- `zlib`

Se reservan para el futuro:

- Huffman canónico
- Rice
- ANS / rANS

---

## 15. Reconstrucción

El decoder debe:

1. validar cabecera
2. leer metadata
3. iterar tiles
4. descomprimir payload
5. reconstruir muestras con el predictor seleccionado
6. reensamblar la imagen completa

En el perfil baseline lossless, la reconstrucción debe ser exacta.

---

## 16. Métricas básicas

Para lossless:

- MSE = 0
- PSNR = infinito

Para futuros perfiles lossy:

- MSE
- PSNR
- SSIM (recomendado a futuro)

---

## 17. Compatibilidad futura

La v0.1 debe considerarse una base estructural, no una definición cerrada del ecosistema completo.

La compatibilidad futura debe apoyarse en:

- versionado explícito
- profile IDs
- flags reservados
- campos reservados en header
- rechazo controlado de features no soportadas

---

## 18. Estado actual honesto

RTImg v0.1 es una especificación temprana, útil para:

- crear test vectors
- validar bitstream
- estabilizar parser y decoder
- construir tooling inicial

No es todavía un formato de producción maduro ni una alternativa universal a los formatos consolidados del mercado.
