# RTImg Test Vectors

## 1. Objetivo

Los test vectors son esenciales para que RTImg deje de ser solo un diseño conceptual y pase a ser un formato verificable.

Sirven para:

- validar parser
- validar roundtrip
- comprobar compatibilidad entre implementaciones
- detectar regresiones
- ensayar corrupción y manejo de errores

---

## 2. Estrategia general

Se recomienda separar los vectores en cuatro grupos:

### A. Positivos mínimos
Archivos pequeños y correctos que cualquier implementación debería abrir.

### B. Roundtrip
Casos donde una imagen de entrada debe recuperarse exactamente tras encode + decode.

### C. Estructurales negativos
Archivos corruptos o truncados que el parser debe rechazar.

### D. Futuro
Casos reservados para perfiles no implementados aún, usados para comprobar rechazo limpio de features no soportadas.

---

## 3. Matriz inicial recomendada

| ID | Caso | Modo | Tamaño | Tile | Predictor | Entropía | Resultado esperado |
|---|---|---|---|---:|---|---|---|
| TV-001 | pixel negro único | L | 1x1 | 1 | none | raw | válido |
| TV-002 | gradiente gris pequeño | L | 8x8 | 8 | left | zlib | válido |
| TV-003 | checker RGB | RGB | 8x8 | 8 | paeth | zlib | válido |
| TV-004 | RGBA borde alpha | RGBA | 16x16 | 8 | avg | zlib | válido |
| TV-005 | tile irregular derecha | RGB | 17x9 | 8 | left | zlib | válido |
| TV-006 | tile irregular inferior | RGB | 9x17 | 8 | up | zlib | válido |
| TV-007 | metadata mínima | RGB | 4x4 | 4 | none | raw | válido |
| TV-008 | metadata múltiple | RGBA | 4x4 | 4 | paeth | zlib | válido |
| TV-009 | magic inválido | n/a | n/a | n/a | n/a | n/a | rechazo |
| TV-010 | CRC incorrecto | RGB | 8x8 | 8 | left | zlib | rechazo |
| TV-011 | payload truncado | RGB | 8x8 | 8 | left | zlib | rechazo |
| TV-012 | profile desconocido | RGB | 8x8 | 8 | left | zlib | rechazo limpio |

---

## 4. Corpus visual recomendado

Además de vectores mínimos, conviene mantener un corpus pequeño pero variado:

- color plano
- gradiente horizontal
- gradiente vertical
- damero
- ruido pseudoaleatorio
- imagen con alpha duro
- patrón con bordes finos
- captura con texto
- foto simple convertida a 8-bit RGB

Esto ayuda a comparar compresibilidad y detectar problemas de predicción.

---

## 5. Qué validar en cada vector

### Parser
- lectura completa
- consistencia de tamaños
- manejo de errores
- rechazo de corrupción

### Decoder
- integridad de reconstrucción
- control de límites
- cumplimiento del predictor
- verificación de CRC

### Encoder
- estabilidad del bitstream emitido
- concordancia con la spec
- roundtrip exacto en lossless

---

## 6. Formato de publicación de vectores

Se recomienda que cada vector publicado tenga:

- archivo fuente si aplica
- archivo `.rti`
- checksum del archivo
- metadata esperada
- imagen reconstruida esperada
- resultado de validación esperado
- notas sobre el caso

---

## 7. Convención de nombres

Ejemplo de nombres:

- `tv-001-l-1x1-none-raw.rti`
- `tv-003-rgb-8x8-paeth-zlib.rti`
- `tv-010-invalid-crc.rti`

---

## 8. Automatización

Las pruebas automáticas deberían cubrir al menos:

- encode/decode
- compare byte a byte
- inspect/parsing
- corruptions conocidas
- compatibilidad con versiones previas del bitstream draft

---

## 9. Valor estratégico

Sin test vectors, el proyecto corre el riesgo de quedarse en documentación. Con test vectors, RTImg pasa a ser un formato verificable y portable entre implementaciones, que es exactamente lo que necesita antes de crecer hacia C, Rust y perfiles lossy.
