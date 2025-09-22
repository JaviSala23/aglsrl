# Proyecto AGL — Versión 1 (Diseño Formalizado)

## 1. Objetivo General
Sistema para **gestión de tickets de entrada/salida de mercadería** y **almacenaje** en plantas y zonas mixtas, con control de camiones, choferes, documentación y stock.

---

## 2. Entidades Principales

### Ubicación
- **Tipos**: `PLANTA` (con encargado), `ZONA_MIXTA` (sin encargado).
- Geodatos: dirección, lat/lng, polígono, accesos.

### Almacenaje
- Asociado a una **Ubicación**.
- **Tipos**: `SILO`, `SILO_BOLSA`, `GALPON`.
- Campos: código, capacidad, estado, coordenadas.

### Sub‑almacenaje (dentro de Galpón)
- **Tipos**: `GRANEL`, `BOLSA_25`, `BOLSA_50`, `BIGBAG_500`, `BIGBAG_1000`.
- Campos: sector, cantidad unidades, peso total, lote/identificador.

### Mercadería
- Catálogo de especies y calidades.
- **Campos**: especie (soja, maíz, girasol, trigo…), calidad/grado, observaciones.
- Nota: la **presentación** y **unidad de medida** se registran en el **Ticket** (movimiento), no en la mercadería.

### Vehículos y Choferes
- **Vehículo Tractor/Camión**: dominio, tara declarada/verificada, estado operativo.
- **Acoplado/Semirremolque**: dominio, tipo, tara.
- **Conjunto Vehicular**: relación tractor + uno o varios acoplados (incluye bitrenes con hasta 3 dominios).
- **Chofer**: nombre, DNI, licencia (opcional), vencimiento (opcional).
- **Documentación Vehicular**: RTO, VTV, Seguro, CNRT (opcionales).

### Ticket
- **Tipos**: `ENTRADA` / `SALIDA`.
- **Estados**:
  - `EN_PESAJE_ENTRADA`: al registrar peso bruto al ingresar a planta.
  - `CARGA` (si es salida) / `DESCARGA` (si es entrada).
  - `EN_PESAJE_SALIDA`: al registrar peso de salida previo a cierre.
  - `CERRADO`: cierre administrativo definitivo.
  - `ANULADO`: tickets inválidos o que no prosperaron.
- **Modo**: `modo_valido = true/false`.  
  - `true` = operación conforme.  
  - `false` = operación en modo **DARK** (documentación incompleta o mercadería observada).
- **Mercadería asociada**: referencia obligatoria a catálogo de Mercadería.
- **Movimiento (presentación registrada en el ticket)**:
  - `presentacion_movimiento`: FK a **CatalogoPresentacion**.
  - `unidad_medida_mov`: FK a **UnidadMedida**.
  - `cantidad_movimiento`.
  - `peso_unitario_opcional`.
  - `condicion_acondicionamiento` (opcional).
- **Almacenaje destino/origen**: FK a **Almacenaje** o **Sub‑almacenaje** según corresponda.
- **Pesajes**: bruto, tara, neto.
- **Vinculaciones**: vehículo tractor, acoplado, chofer, transportista.

---

## 3. Catálogos Controlados

### CatalogoPresentacion
- `GRANEL`, `BOLSA_25`, `BOLSA_50`, `BIGBAG_500`, `BIGBAG_1000`.

### UnidadMedida
- `KG`, `TN`, `BOLSAS`, `UNIDADES`.

### FactorConversion
- Ejemplo: TN→KG = 1000.

### PesoUnitarioReferencia
- BOLSA_25 = 25 kg
- BOLSA_50 = 50 kg
- BIGBAG_500 = 500 kg
- BIGBAG_1000 = 1000 kg

### ReglaAlmacenajePresentacion
- `SILO` → GRANEL.
- `SILO_BOLSA` → GRANEL.
- `GALPON` → GRANEL, BOLSA_25, BOLSA_50, BIGBAG_500, BIGBAG_1000.

---

## 4. Stock y Conversión
- Todo stock se consolida en **KG**.
- Si ticket en TN → convertir con factor.
- Si en BOLSAS/UNIDADES → `kg = cantidad × peso_unitario`.
- El sistema guarda ambos: la **forma original del movimiento** (ej. 18 BIGBAG_500) y el **equivalente en kg**.

---

## 5. Roles y Permisos
- **Auxiliar**: crear tickets, registrar pesajes.
- **Encargado**: lo anterior + asignar almacenaje, editar ticket, cerrar con observaciones.
- **Administración**: todo + carga de documentación, marcar `modo_valido`, cierre definitivo, anulación.

---

## 6. Reportes Iniciales
1. Stock por ubicación/almacenaje (kg + forma original).
2. Movimientos por ticket (entrada/salida, mercadería, camión).
3. Padrón vehicular y choferes.
4. Alertas de vencimientos.
5. Consumo/producción por presentación (bolsas/bigbags).

---

## 7. Roadmap Iteraciones
- Iteración 1: Formalización de modelos (este documento).
- Iteración 2: Diccionario de datos y altas iniciales de catálogos.
- Iteración 3: Flujos de tickets con ejemplos.
- Iteración 4: Plantillas de documentos (QR, reportes).
- Iteración 5: Integración con CPs, remitos y liquidaciones.

---

## 8. Diagrama Entidad–Relación (texto)
- **Ubicación** 1—N **Almacenaje**
- **Almacenaje** 1—N **Sub‑almacenaje**
- **Almacenaje/Sub‑almacenaje** N—N **Ticket** (según origen/destino)
- **Mercadería** 1—N **Ticket**
- **Vehículo Tractor** 1—N **Ticket**
- **Acoplado** 0..1—N **Ticket**
- **Chofer** 1—N **Ticket**
- **Transportista** 1—N **Ticket**
- **Ticket** N—1 **CatalogoPresentacion** + N—1 **UnidadMedida**
- **CatalogoPresentacion** 1—N **PesoUnitarioReferencia**
- **UnidadMedida** N—N **FactorConversion**
- **Almacenaje.tipo** N—N **ReglaAlmacenajePresentacion** → **CatalogoPresentacion**

## 9. Matriz de Compatibilidad Almacenaje × Presentación
| Almacenaje Tipo | GRANEL | BOLSA_25 | BOLSA_50 | BIGBAG_500 | BIGBAG_1000 |
|-----------------|--------|----------|----------|------------|-------------|
| SILO            | ✔      | ✘        | ✘        | ✘          | ✘           |
| SILO_BOLSA      | ✔      | ✘        | ✘        | ✘          | ✘           |
| GALPON          | ✔      | ✔        | ✔        | ✔          | ✔           |

> Esta matriz inicial define qué combinaciones son válidas al registrar movimientos en tickets. Puede extenderse en futuras iteraciones (ej.: permitir bolsas en silos especiales).


## 8. Diagrama ER (texto)
- **Ubicación** (1) ─── (N) **Almacenaje**
  - Ubicación(id) ↔ Almacenaje(ubicacion_id)
- **Almacenaje** (1) ─── (N) **Sub‑almacenaje**
  - Almacenaje(id) ↔ SubAlmacenaje(almacenaje_id)
- **Mercadería** (1) ─── (N) **Ticket**
  - Mercadería(id) ↔ Ticket(mercaderia_id)
- **Vehículo (Tractor)** (1) ─── (N) **Ticket**
  - Vehículo(id) ↔ Ticket(tractor_id)
- **Acoplado** (0..1) ─── (N) **Ticket**
  - Acoplado(id) ↔ Ticket(acoplado_id)
- **ConjuntoVehicular** (0..1) ─── (N) **Ticket**
  - ConjuntoVehicular(id) ↔ Ticket(conjunto_id)
- **Chofer** (1) ─── (N) **Ticket**
  - Chofer(id) ↔ Ticket(chofer_id)
- **Transportista** (1) ─── (N) **Ticket**
  - Transportista(id) ↔ Ticket(transportista_id)
- **CatalogoPresentacion** (1) ─── (N) **Ticket** (presentacion_movimiento)
- **UnidadMedida** (1) ─── (N) **Ticket** (unidad_medida_mov)
- **Almacenaje/Sub‑almacenaje** (0..1) ─── (N) **Ticket** (origen/destino según tipo)

> Notas:
> - Todo **stock** se consolida por Almacenaje/Sub‑almacenaje en **KG**.
> - El **Ticket** guarda la forma original del movimiento (presentación, unidad, cantidad, peso unitario opcional).

## 9. Matriz de compatibilidad Almacenaje × Presentación (v1)

| Almacenaje.tipo | GRANEL | BOLSA_25 | BOLSA_50 | BIGBAG_500 | BIGBAG_1000 |
|---|:---:|:---:|:---:|:---:|:---:|
| SILO | ✓ | – | – | – | – |
| SILO_BOLSA | ✓ | – | – | – | – |
| GALPON | ✓ | ✓ | ✓ | ✓ | ✓ |

**Reglas adicionales**
- `SILO` y `SILO_BOLSA` operan **solo GRANEL**; en Silo Bolsa se puede segmentar por **tramos**.
- `GALPON` admite **todas** las presentaciones. Se recomienda sectorización para bolsas/bigbags.
- Para **SALIDAS**, verificar disponibilidad en la unidad seleccionada antes de pasar a `EN_PESAJE_SALIDA`.

## 10. Flujos resumidos por tipo de Ticket
**ENTRADA**
1) Crear → `EN_PESAJE_ENTRADA` → registrar **bruto**
2) `DESCARGA` → asignar **Almacenaje/Sub** compatible
3) `EN_PESAJE_SALIDA` → registrar **tara** → resultado `DESCARGADO`
4) Administración: `modo_valido` (true/false) y **CERRADO** (o **ANULADO**)

**SALIDA**
1) Crear → `EN_PESAJE_ENTRADA` → registrar **bruto** (si aplica) o iniciar en balanza
2) `CARGA` → **reserva/egreso** en Almacenaje/Sub compatible
3) `EN_PESAJE_SALIDA` → registrar **tara** → resultado `CARGADO`
4) Administración: `modo_valido` (true/false) y **CERRADO** (o **ANULADO**)

