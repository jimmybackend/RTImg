# RTImg Metadata TLV

## 1. Objetivo

RTImg necesita transportar más que información visual. Al formar parte de RT Stack, también debe poder contener datos de operación y trazabilidad.

Por eso la metadata se modela como una sección **TLV-like** simple, legible y extensible.

---

## 2. Diseño elegido

Cada entrada usa este esquema:

```text
[key_len:u16]
[value_len:u32]
[key:key_len bytes UTF-8]
[value:value_len bytes UTF-8]
```

Esto permite una implementación directa en Python, C y Rust sin depender de estructuras complejas ni serializadores externos.

---

## 3. Razones para usar TLV simple

- fácil de parsear
- fácil de depurar
- estable para la v0
- extensible
- suficiente para metadata textual y operativa
- no obliga a introducir JSON binario u otros formatos antes de tiempo

---

## 4. Reglas básicas

### 4.1 Claves
- UTF-8
- únicas dentro de un mismo archivo
- recomendación: minúsculas con `_` o `.` como separador

Ejemplos:
- `asset_id`
- `origin_format`
- `pipeline_id`
- `integrity_hash`
- `created_by`

### 4.2 Valores
- UTF-8 en la baseline actual
- no se exige semántica global cerrada
- las implementaciones pueden preservar claves desconocidas

### 4.3 Orden
El orden no debe tener significado semántico obligatorio.

---

## 5. Claves recomendadas

### 5.1 Procedencia
- `source_filename`
- `source_mode`
- `origin_format`
- `ingest_source`

### 5.2 Pipeline
- `pipeline_id`
- `job_id`
- `stage`
- `created_by`

### 5.3 Identidad y trazabilidad
- `asset_id`
- `parent_asset_id`
- `transcode_history`
- `capture_timestamp`

### 5.4 Integridad y control
- `integrity_hash`
- `policy.export`
- `policy.visibility`
- `policy.retention`

---

## 6. Ejemplo conceptual

```text
key = "origin_format"
value = "image/png"

key = "asset_id"
value = "img-00001234"

key = "created_by"
value = "rtcore-ingest"
```

---

## 7. Validaciones del parser

El parser debe:

- validar que `key_len` y `value_len` no salgan de rango
- rechazar entradas truncadas
- permitir valores vacíos si la implementación lo considera válido
- rechazar claves duplicadas si la política del repositorio así lo exige

---

## 8. Extensiones futuras

En versiones posteriores se podría ampliar el modelo para soportar:

- tipos explícitos por valor
- metadata binaria
- namespaces
- firmas criptográficas
- estructuras anidadas

Pero ninguna de estas extensiones debería romper la simplicidad del path base de parsing.

---

## 9. Relación con RT Stack

La metadata es una de las razones por las que RTImg tiene sentido como formato de ecosistema. Permite que RTCore, RTStream y RTCloud compartan no solo la imagen, sino también el contexto técnico de cómo esa imagen fue producida, verificada, almacenada o exportada.
