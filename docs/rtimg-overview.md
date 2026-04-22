# RTImg Overview

## 1. Qué es RTImg

**RTImg** es el códec de imagen nativo de **RT Stack**, el ecosistema técnico de **Rethra Communications**.

Dentro de este contexto, `RT` significa **Resilient Transmission**. Por tanto, RTImg no se concibe solo como un formato para “guardar imágenes”, sino como una pieza del stack que debe responder a necesidades de:

- representación interna canónica
- integridad de datos
- transmisión resiliente
- procesamiento por regiones
- metadata operativa útil para pipelines reales
- integración futura con servicios distribuidos

RTImg acepta que el mundo exterior seguirá usando formatos ampliamente soportados como PNG, JPEG, WebP, AVIF o JPEG XL. Sin embargo, cuando una imagen entra al dominio RT, la propuesta es que pase a representarse internamente como **RTImg**.

---

## 2. Papel dentro de RT Stack

### RTCore
RTCore puede usar RTImg como formato de trabajo unificado para:

- ingestión de imágenes
- normalización de activos
- transformaciones internas
- validación de integridad
- trazabilidad de pipeline

### RTStream
RTStream puede beneficiarse de una estructura por **tiles** para:

- transmisión parcial
- priorización de regiones
- recuperación selectiva de errores
- transporte de payloads en unidades predecibles

### RTCloud
RTCloud puede usar RTImg como base para:

- persistencia de activos canónicos
- sincronización entre nodos
- almacenamiento de metadata operativa
- políticas de exportación controladas

---

## 3. Objetivo técnico del proyecto

El objetivo de RTImg no es “superar a todos los formatos existentes”, sino resolver bien un caso concreto:

> proporcionar un códec de imagen abierto, determinista y extensible, con formato binario propio, capaz de servir como representación interna de RT Stack con soporte para resiliencia, parsing estable, metadata útil y evolución futura hacia perfiles lossy y streaming avanzado.

---

## 4. Principios de diseño

### 4.1 Especificación abierta
La estructura binaria debe poder documentarse y reimplementarse por terceros.

### 4.2 Determinismo
La decodificación debe producir el mismo resultado en cualquier implementación conforme.

### 4.3 Tiles como unidad primaria
El contenedor se apoya en tiles para habilitar:

- paralelismo
- decodificación parcial
- aislamiento de corrupción
- retransmisión selectiva
- compatibilidad futura con streaming

### 4.4 Metadata nativa
RTImg no debe almacenar solo píxeles. También debe poder transportar:

- origen del activo
- identificadores internos
- historial de transcodificación
- políticas de exportación
- hashes de integridad
- timestamps de pipeline

### 4.5 Extensibilidad por perfiles
El formato se plantea como familia de perfiles, no como un único modo rígido.

---

## 5. Estrategia de versiones

La decisión más realista para el arranque del proyecto es:

- diseñar un contenedor preparado para perfiles **lossless** y **lossy**
- implementar primero un perfil **lossless baseline**
- congelar el bitstream básico antes de atacar compresión perceptual compleja

Este enfoque reduce riesgo, facilita pruebas y evita que la v0 se convierta en una promesa difícil de sostener.

---

## 6. Arquitectura funcional

La arquitectura propuesta se divide en estos bloques:

### Encoder
- lectura/adaptación de imagen externa
- normalización del layout interno
- división en tiles
- predicción espacial
- generación de residuos
- compresión de payload
- escritura del bitstream

### Decoder
- parsing del contenedor
- validación de cabecera y checksums
- descompresión por tile
- reconstrucción de muestras
- ensamblado de la imagen final

### Parser
- interpretación de cabecera
- lectura de metadata
- lectura de descriptores de tile
- exposición de estructura sin requerir decodificación total

---

## 7. Estado actual real

RTImg, en el estado actual del repositorio, ya tiene una base seria pero temprana:

- especificación inicial pública
- perfil lossless baseline
- prototipo de referencia en Python
- predictores espaciales básicos
- metadata simple tipo TLV
- CRC por tile
- roadmap razonable a C y Rust

No es todavía un códec maduro de producción. Ese límite forma parte del diseño honesto del proyecto.

---

## 8. Diferenciadores frente a formatos externos

RTImg tiene sentido si su valor principal es **sistémico**:

- formato interno canónico de RT Stack
- estructura por tiles desde el diseño
- metadata operativa rica
- preparación para streaming y cloud
- interoperabilidad externa controlada

En cambio, como formato de distribución universal hoy seguirán siendo superiores PNG, JPEG, WebP, AVIF o JPEG XL, según el caso.
