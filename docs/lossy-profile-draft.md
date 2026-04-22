# RTImg Lossy Profile Draft

## 1. Estado de este documento

Este documento es un **borrador no normativo**. No define todavía un perfil estable de producción. Su propósito es dejar bien encaminada la evolución de RTImg hacia compresión perceptual.

---

## 2. Por qué un perfil lossy es necesario

Si RTImg aspira a ser una familia completa de códecs dentro de RT Stack, tarde o temprano necesita un modo lossy para:

- reducir tamaño de transporte
- generar previsualizaciones
- distribuir versiones de trabajo livianas
- servir contenidos donde la fidelidad exacta no sea imprescindible

Sin embargo, empezar directamente por un perfil lossy complicaría demasiado la v0 del proyecto. Por eso este perfil se define primero como borrador.

---

## 3. Objetivos del perfil lossy futuro

El perfil lossy debería perseguir estas metas:

- mantener la estructura general del contenedor RTImg
- seguir usando tiles como unidad primaria
- permitir varios niveles de calidad
- aprovechar correlación espacial y/o frecuencial
- ser compatible con metadata y políticas de exportación
- permitir métricas reproducibles de evaluación

---

## 4. Modelo técnico recomendado

### 4.1 Conversión de color
Para imágenes RGB/RGBA, el camino recomendado es:

- convertir RGB a YCbCr
- tratar luma y croma de forma diferenciada
- evaluar posibilidad de subsampling 4:4:4 al inicio, dejando 4:2:0 para fases posteriores

### 4.2 Transformada
Dentro de cada tile, la unidad de análisis puede dividirse en bloques más pequeños, por ejemplo:

- 8x8
- 16x16

La transformada inicial más razonable sería una **DCT** o una transformada entera compatible con reconstrucción estable.

### 4.3 Cuantización
La cuantización controlaría el compromiso entre calidad y compresión.

Opciones a estudiar:
- tabla fija global por calidad
- tablas por componente
- tablas por tile en escenarios avanzados

### 4.4 Entropía
Tras transformada y cuantización, los coeficientes podrían comprimirse con:

- Huffman canónico
- Rice
- rANS

Para evitar saltos de complejidad demasiado grandes, una primera versión experimental podría incluso encapsular coeficientes serializados y comprimidos con zlib, únicamente para validar la ruta del pipeline.

---

## 5. Estructura propuesta del payload lossy

Una ruta razonable sería:

1. tile -> bloques internos
2. RGB -> YCbCr
3. transformada por bloque
4. cuantización
5. ordenación de coeficientes
6. codificación entrópica
7. empaquetado en payload de tile

En una versión más madura, podría añadirse:

- varias capas de calidad
- preview layer
- truncado progresivo
- refinamiento de regiones

---

## 6. Qué no conviene hacer al principio

No conviene que el primer perfil lossy intente resolver a la vez:

- compresión extrema
- HDR
- capas
- animación
- aprendizaje perceptual sofisticado
- compatibilidad directa con todos los formatos externos

Eso haría el proyecto innecesariamente frágil.

---

## 7. Métricas recomendadas

Para evaluar un perfil lossy hacen falta métricas básicas y repetibles:

- PSNR
- SSIM
- MS-SSIM

Más adelante podría añadirse una evaluación perceptual más compleja, pero no debe bloquear la fase experimental inicial.

---

## 8. Riesgos reales

Los riesgos principales del perfil lossy son:

- congelar demasiado pronto decisiones erróneas
- tener un decoder difícil de mantener
- crear un modo “experimental” imposible de comparar
- prometer eficiencia similar a AVIF o JPEG XL sin base suficiente

Por eso el desarrollo debe ser gradual y muy medido.

---

## 9. Recomendación práctica

El camino más profesional es este:

1. estabilizar el contenedor y el perfil lossless
2. publicar test vectors y corpus
3. portar parser/decoder base a C o Rust
4. diseñar el perfil lossy con benchmarks desde el principio
5. declarar el primer modo lossy como **experimental** hasta tener métricas y compatibilidad suficientemente claras
