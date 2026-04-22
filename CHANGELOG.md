# Changelog

Todos los cambios relevantes de **RTImg** deben registrarse aquí.

El formato sugerido es una variante simple de *Keep a Changelog*, adaptada al estado temprano del proyecto.

## [0.1.0-draft] - 2026-04-22

### Añadido
- definición inicial del proyecto RTImg dentro de RT Stack
- README con alcance real, objetivos y arquitectura
- especificación abierta `specs/rtimg-v0.1.md`
- perfil base lossless-first
- diseño de contenedor binario con header, metadata y tiles
- metadata tipo TLV
- CRC32 por tile en el prototipo de referencia
- prototipo Python con encoder, decoder, parser e inspector
- soporte inicial para `L`, `RGB` y `RGBA` a 8 bits
- predictores `none`, `left`, `up`, `avg` y `paeth`
- compresión `raw` y `zlib`

### Pendiente
- corpus de test vectors estable
- documentación detallada del header binario byte a byte
- port a C
- port a Rust
- perfil lossy experimental
