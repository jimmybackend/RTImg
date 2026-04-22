# Contribuir a RTImg

Gracias por tu interés en colaborar con **RTImg**.

Este proyecto está en una fase temprana. La prioridad actual no es acumular features rápidamente, sino construir una base técnica sólida, verificable y coherente con el objetivo real del proyecto: ser el formato de imagen nativo de **RT Stack**.

## Principios de contribución

Antes de proponer cambios, ten en cuenta estos principios:

- la especificación manda sobre la implementación
- la compatibilidad del bitstream importa más que el atajo local
- una mejora debe poder explicarse y probarse
- preferimos cambios pequeños, revisables y bien documentados
- el proyecto no debe prometer más madurez de la que realmente tiene

## Áreas en las que sí conviene contribuir

### 1. Parser y validación
- validación de cabeceras
- detección de corrupción
- verificación de campos inconsistentes
- robustez frente a entradas inválidas

### 2. Test vectors
- imágenes pequeñas reproducibles
- casos límite de tiles
- pruebas de roundtrip
- archivos dañados para pruebas negativas

### 3. Documentación
- aclaraciones de bitstream
- diagramas de estructura
- ejemplos de metadata
- comparativas honestas con otros formatos

### 4. Implementación de referencia
- mejoras del encoder/decoder Python
- limpieza del código
- separación clara entre parser, codec y CLI
- preparación para port a C y Rust

## Flujo recomendado

1. abre un issue describiendo el problema o propuesta
2. explica el impacto en bitstream, compatibilidad y tooling
3. si toca el formato, documenta el cambio antes o junto al código
4. añade pruebas cuando aplique
5. evita mezclar refactors grandes con cambios de comportamiento

## Qué no hacer

- no cambies silenciosamente la estructura del archivo
- no introduzcas un perfil lossy “experimental” sin documentar su semántica
- no asumas campos o relaciones que no estén definidos
- no vendas el proyecto como “production-ready” si no lo es
- no envíes PRs enormes sin contexto

## Estilo técnico esperado

- nombres claros
- validaciones explícitas
- errores legibles
- comportamiento determinista
- documentación alineada con la implementación real

## Commits y PRs

Se recomienda que los commits sean concretos. Ejemplos razonables:

- `parser: validate tile_count against geometry`
- `python: add crc32 verification for tile payloads`
- `spec: clarify metadata TLV encoding`
- `tests: add roundtrip corpus for rgba tiles`

En cada PR intenta incluir:

- objetivo del cambio
- alcance real
- compatibilidad o ruptura
- pruebas añadidas
- archivos de especificación impactados

## Discusión técnica

Cuando una propuesta afecte el formato, intenta responder estas preguntas:

- ¿rompe compatibilidad?
- ¿mejora resiliencia, claridad o extensibilidad?
- ¿puede validarse con test vectors?
- ¿ayuda de verdad al ecosistema RT?

## Licencia de contribuciones

Salvo que se indique lo contrario, al contribuir aceptas que tu aporte pueda distribuirse bajo la licencia del repositorio.
