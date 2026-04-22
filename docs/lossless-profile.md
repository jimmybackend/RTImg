# RTImg Lossless Profile

## 1. Objetivo del perfil

El perfil **lossless baseline** es la base técnica más realista para iniciar RTImg. Su finalidad es:

- validar el contenedor binario
- garantizar roundtrip exacto
- establecer una implementación de referencia confiable
- construir corpus de pruebas y test vectors
- preparar la evolución futura sin depender todavía de cuantización ni tuning perceptual

---

## 2. Alcance actual

La baseline propuesta cubre:

- imágenes `L`, `RGB`, `RGBA`
- 8 bits por canal
- tiles independientes
- predicción espacial básica
- compresión `raw` o `zlib`
- metadata TLV
- CRC por tile

Quedan fuera de esta baseline:

- HDR
- YCbCr
- transformadas
- cuantización
- perfiles perceptuales
- progresivo por capas

---

## 3. Modelo matemático

### 3.1 Señal de entrada
Sea una imagen discreta `I(x, y, c)` donde:

- `x` es la coordenada horizontal
- `y` es la coordenada vertical
- `c` es el canal
- el valor de muestra está en `0..255`

### 3.2 Orden de recorrido
Cada tile se recorre en orden raster:

- fila por fila
- de izquierda a derecha
- de arriba a abajo
- canal por canal dentro de cada píxel

---

## 4. Predicción espacial

La predicción se apoya en vecinos ya reconstruidos.

Definiciones:
- `L`: muestra izquierda
- `U`: muestra superior
- `UL`: muestra superior izquierda

### 4.1 Predictor `none`
`P = 0`

Útil para depuración o datos poco correlacionados.

### 4.2 Predictor `left`
`P = L`

Simple y generalmente eficaz en regiones suaves horizontales.

### 4.3 Predictor `up`
`P = U`

Simple y útil cuando la correlación vertical domina.

### 4.4 Predictor `average`
`P = floor((L + U) / 2)`

Equilibrio básico entre izquierda y arriba.

### 4.5 Predictor `paeth`
Usa la heurística clásica de Paeth:

1. `base = L + U - UL`
2. se elige entre `L`, `U` o `UL` el que minimiza la distancia a `base`

Es un predictor razonable para una baseline lossless porque mejora la compresibilidad sin volver complejo el decoder.

---

## 5. Residuos

Para una muestra original `X` y una predicción `P` se define:

`R = (X - P) mod 256`

La reconstrucción es:

`X = (P + R) mod 256`

Este enfoque mantiene la reversibilidad exacta con aritmética entera modular.

---

## 6. Serialización de muestras por tile

El payload lógico de un tile, antes de compresión por entropía, se serializa así:

1. recorrer filas del tile
2. recorrer columnas del tile
3. recorrer canales del píxel
4. calcular predictor según vecinos reconstruidos dentro del tile
5. almacenar el residuo resultante

Para la baseline actual, los vecinos fuera del tile se consideran cero. Eso preserva independencia total entre tiles.

### Consecuencia
La compresión puede ser algo peor que con predicción global entre tiles, pero se gana:

- simplicidad
- paralelismo
- resiliencia
- independencia estructural

---

## 7. Entropy stage

### 7.1 `raw`
El payload se almacena sin compresión adicional.

Útil para depuración y test vectors.

### 7.2 `zlib`
El payload serializado de residuos se comprime con zlib.

Ventajas:
- implementación disponible
- fácil validación
- permite demostrar diseño sin inventar aún un códec entrópico complejo

---

## 8. Reglas del decoder

Un decoder conforme del perfil lossless baseline debe:

- validar header y compatibilidad de perfil
- parsear metadata
- decodificar cada tile en orden o por demanda
- validar CRC si está presente
- reconstruir exactamente las muestras originales
- reensamblar la imagen respetando ancho, alto y canales

Si el archivo es válido y el perfil está soportado, el resultado debe ser **bit-exact**.

---

## 9. Métricas

Para este perfil:

- `MSE = 0`
- `PSNR = infinito`

Por tanto, las métricas perceptuales no se usan para validar corrección. La validación principal es:

- igualdad byte a byte
- checksums
- roundtrip estable
- compatibilidad de parser

---

## 10. Ventajas de empezar por aquí

- especificación validable
- pruebas automáticas sencillas
- menor complejidad inicial
- base sólida para puertos a C y Rust
- definición clara del contrato del decoder

Este perfil no busca ratios espectaculares. Busca construir la **columna vertebral** del proyecto.
