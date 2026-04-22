# RTImg and RT Stack Integration

## 1. Propósito

Este documento describe cómo RTImg encaja de forma natural dentro del ecosistema **RT Stack** y por qué su diseño debe responder a necesidades de sistema, no solo a compresión aislada.

---

## 2. RTCore

### 2.1 Ingestión
RTCore puede recibir imágenes en formatos externos como PNG, JPEG, WebP, AVIF u otros. Durante la ingestión:

1. se valida el archivo fuente
2. se normaliza modo, dimensiones y metadata esencial
3. se genera un activo interno en RTImg
4. se registra el origen en metadata

### 2.2 Procesamiento interno
Una vez dentro de RTCore, RTImg sirve como representación canónica para:

- preprocesado
- validación
- inspección técnica
- transformaciones controladas
- preparación para persistencia o transporte

### 2.3 Beneficio
Evita depender de múltiples formatos heterogéneos en el corazón del stack.

---

## 3. RTStream

RTStream es donde la estructura por tiles de RTImg cobra más valor.

### 3.1 Casos de uso
- envío parcial por regiones
- priorización de tiles visibles o críticos
- retransmisión selectiva
- tolerancia a fallos en segmentos aislados

### 3.2 Requisitos de diseño relacionados
Para integrarse bien con RTStream, RTImg debe tender a:

- tiles independientes
- checksums por tile
- capacidad de inspección sin decodificación total
- futura tabla de offsets o index opcional
- posibilidad de payloads progresivos en versiones posteriores

---

## 4. RTCloud

RTCloud puede tratar un archivo RTImg como un objeto rico, no solo como blob binario.

### 4.1 Persistencia
RTImg puede almacenarse junto con:

- identificadores de asset
- hash de integridad
- timestamps
- política de exportación
- historial de transcodificación

### 4.2 Sincronización
Si el modelo de almacenamiento evoluciona a nivel de chunks o tiles, RTImg ya ofrece una base razonable para estrategias de sincronización parcial.

### 4.3 Auditoría
La metadata TLV permite reconstruir el contexto operativo del activo.

---

## 5. Importación y exportación

La filosofía recomendada del ecosistema es:

- **entrada externa flexible**
- **representación interna RTImg**
- **salida externa controlada**

Esto significa que PNG, JPEG, WebP o AVIF seguirán siendo importantes como formatos frontera, pero no necesariamente como formato nativo de trabajo interno.

---

## 6. Beneficios sistémicos de RTImg

RTImg puede aportar al stack:

- formato unificado
- parsing determinista
- inspección simple
- metadata operativa compartida
- resiliencia por tiles
- mejor preparación para cloud y streaming

---

## 7. Riesgos de integración a vigilar

- acoplar demasiado pronto el bitstream a un transporte concreto
- meter reglas de negocio dentro del códec
- congelar metadata antes de conocer necesidades reales de operación
- sacrificar simplicidad del parser por optimizaciones prematuras

La mejor estrategia es mantener el códec limpio y dejar que RTCore/RTStream/RTCloud definan capas superiores de orquestación.

---

## 8. Recomendación de arquitectura

La integración ideal debería exponer:

- librería `rtimg-core` para parsing y codec
- CLI `rtimg` para herramientas de operador
- adaptadores de ingestión/exportación en RTCore
- transporte o chunk mapping en RTStream
- persistencia y políticas en RTCloud

De esta forma, RTImg se mantiene como una base técnica reutilizable y no como un bloque monolítico difícil de mover.
