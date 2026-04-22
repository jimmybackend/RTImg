# RTImg

**RTImg** es el códec de imagen nativo del ecosistema **RT Stack** de **Rethra Communications**.

`RT` significa **Resilient Transmission**.

RTImg nace como un formato de imagen **abierto, extensible, determinista y orientado a tiles**, pensado para ser la representación interna canónica de imagen dentro de **RTCore**, **RTStream** y **RTCloud**.

## Estado real del proyecto

**Estado actual:** diseño técnico inicial + especificación abierta v0.1 + prototipo de referencia en Python.

Hoy el proyecto define de forma realista:

- un formato binario propio
- un perfil base **lossless**
- procesamiento por **tiles independientes**
- metadata técnica en estructura tipo TLV
- encoder, decoder y parser de referencia en Python
- una hoja de ruta para evolución hacia perfiles **lossy** y puertos a **C** y **Rust**

RTImg **no** pretende reemplazar a PNG, JPEG, WebP, AVIF o JPEG XL como formato universal de la web. Su objetivo es distinto: ser el **formato interno de trabajo** del universo RT.

## Papel de RTImg dentro de RT Stack

RTImg debe ocupar este lugar dentro del stack:

- **Entrada externa:** RT Stack puede aceptar PNG, JPEG, WebP, AVIF u otros formatos.
- **Normalización interna:** esos activos se convierten a RTImg.
- **Procesamiento interno:** RTCore opera sobre RTImg como formato canónico.
- **Transporte:** RTStream puede transmitir tiles o regiones concretas.
- **Persistencia y trazabilidad:** RTCloud puede almacenar RTImg con metadata operativa y de integridad.
- **Salida controlada:** la interoperabilidad externa se resuelve por exportación o decodificación controlada.

## Principios de diseño

### 1. Formato interno nativo
Toda imagen que entra al ecosistema puede representarse en RTImg.

### 2. Especificación abierta
El bitstream debe ser público e implementable por terceros.

### 3. Comportamiento determinista
Misma entrada + mismo perfil + mismos parámetros = mismo resultado reproducible.

### 4. Resiliencia por tiles
El formato se apoya en tiles para favorecer:

- decodificación parcial
- paralelismo
- aislamiento de corrupción
- retransmisión selectiva
- futura integración con RTStream

### 5. Metadata operativa
RTImg no guarda solo datos visuales; también debe poder transportar:

- procedencia
- linaje de pipeline
- identificadores internos
- políticas de exportación
- hashes de integridad

### 6. Arquitectura extensible
El diseño se plantea como familia de perfiles:

- **RTImg-L**: lossless
- **RTImg-Q**: lossy / perceptual
- perfiles futuros progresivos o por capas

## Decisión técnica actual

La decisión más realista para arrancar es:

- **arquitectura híbrida a nivel de formato**
- **implementación inicial lossless**

Eso permite validar el bitstream, las herramientas y el roundtrip exacto antes de entrar en transformadas, cuantización y tuning perceptual.

## Arquitectura actual propuesta

### Encoder
- adapta la imagen de entrada
- normaliza modo y canales
- divide en tiles
- aplica predicción espacial
- genera residuos
- comprime payloads por tile
- escribe el bitstream RTImg

### Decoder
- parsea el archivo
- valida cabecera y checksums
- descomprime tiles
- reconstruye píxeles
- rearma la imagen final

### Parser
- interpreta el contenedor
- valida la estructura
- expone metadata y descriptores sin necesidad de decodificar toda la imagen

### Bitstream
Estructura general:

```text
[HEADER FIJO]
[METADATA TLV]
[TILE DESCRIPTOR 0][TILE PAYLOAD 0]
[TILE DESCRIPTOR 1][TILE PAYLOAD 1]
...
[TILE DESCRIPTOR N][TILE PAYLOAD N]
```

## Capacidades reales del prototipo actual

El prototipo Python incluido en este repositorio soporta:

- imágenes `L`, `RGB`, `RGBA`
- 8 bits por canal
- predictor `none`, `left`, `up`, `avg`, `paeth`
- compresión `raw` o `zlib`
- metadata TLV simple
- CRC32 por tile
- decodificación exacta en perfil **lossless**

## Qué hace especial a RTImg

RTImg tiene sentido si su ventaja es sistémica, no solo de ratio de compresión:

- representación canónica de imagen en RT Stack
- tiles independientes y retransmisibles
- metadata orientada a operaciones reales
- decodificación parcial por región
- alineación futura con streaming y cloud
- control explícito de importación y exportación

## Comparación honesta

### Frente a PNG
PNG seguirá siendo superior como formato lossless universal. RTImg puede ser mejor como formato interno con tiles, checksums y metadata operacional.

### Frente a JPEG
JPEG seguirá siendo formato de distribución masiva. RTImg encaja mejor como formato nativo de trabajo interno.

### Frente a WebP
WebP es un formato generalista. RTImg es un formato de sistema.

### Frente a AVIF
AVIF gana en compresión moderna agresiva. RTImg no busca superarlo en esta fase.

### Frente a JPEG XL
JPEG XL es el competidor técnico más serio si se habla de ambición moderna de códec. RTImg sigue teniendo sentido si su foco es integración profunda con RT Stack, resiliencia y operación controlada.

## Roadmap resumido

### Fase 0
- diseño del bitstream
- definición de header, metadata y tiles
- congelar el perfil lossless base

### Fase 1
- encoder/decoder/parser en Python
- corpus de pruebas
- roundtrip exacto

### Fase 2
- publicación de la especificación v0.1
- test vectors oficiales
- inspector de archivos

### Fase 3
- port a C del parser y decoder
- encoder C después

### Fase 4
- port a Rust
- crates `core`, `bitstream`, `cli`

### Fase 5
- perfil lossy experimental
- YCbCr
- transformadas
- cuantización
- métricas comparativas

## Estructura del repositorio

```text
rtimg/
├── LICENSE
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── .gitignore
├── docs/
│   └── project-overview.md
├── specs/
│   └── rtimg-v0.1.md
└── reference/
    └── python/
        └── rtimg_v0.py
```

## Uso del prototipo

```bash
pip install pillow
python reference/python/rtimg_v0.py encode input.png output.rti --tile 64 --predictor paeth
python reference/python/rtimg_v0.py decode output.rti restored.png
python reference/python/rtimg_v0.py inspect output.rti
python reference/python/rtimg_v0.py psnr input.png restored.png
```

## Nota importante

Este repositorio representa el **estado real actual** del proyecto: una base seria, abierta y coherente para empezar RTImg correctamente, pero todavía lejos de una versión de producción madura.
