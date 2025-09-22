# AGL — Diseño Funcional v1.1 (MD)

> **Propósito:** Documento de **diseño funcional** en Markdown (sin código) para la Versión 1.1. Incluye **Cuentas + Agenda**, **Tickets**, **Ubicaciones/Almacenajes**, **Mercaderías**, **Vehículos** y **reglas**. Sirve como base para implementación posterior.

---

## 1. Objetivo y Alcance de v1.1

* Establecer el **modelo de datos funcional** y las **reglas** para operar tickets de **Entrada/Salida** con trazabilidad de **Ubicaciones/Almacenajes**, **Mercaderías**, **Vehículos** y **Cuentas**.
* Definir **Cuentas** (Cliente/Proveedor/Transportista/Cuenta Propia) y una **Agenda centralizada** (Contactos/Medios/Domicilios) reutilizable en Tickets y documentos.
* Mantener **presentaciones/unidades** registradas **en el Ticket** (no en el catálogo de Mercaderías) y consolidar **stock en KG**.

---

## 2. Entidades y Diccionario (sin código)

### 2.1 Cuentas (Agenda + Fiscal/ARCA)

**Tipo de Cuenta (catálogo)**
Valores: `CLIENTE`, `PROVEEDOR`, `TRANSPORTISTA`, `CUENTA_PROPIA`.

**Cuenta**

* `id` (PK)
* `razon_social` (Obligatorio)
* `tipo_principal` (FK → Tipo de Cuenta) (Obligatorio)
* **Fiscal (ARCA)**: `cuit` (Opc.), `condicion_iva` (Opc.), `iibb` (Opc.), `domicilio_fiscal` (Opc.), `punto_venta` (Opc.)
* `observaciones` (Opc.)

> **AGL** debe existir como Cuenta con `tipo_principal = CUENTA_PROPIA` para poder figurar como **origen/destino/remitente/destinatario** cuando aplique.

**Agenda centralizada**

* **Contacto**: `id`, `cuenta_id` (FK), `nombre` (Obl.), `cargo` (Opc.), `es_principal` (bool, Opc.), `observaciones` (Opc.)
* **MedioContacto**: `id`, `contacto_id` (FK), `tipo` ∈ {`TELEFONO`,`EMAIL`,`OTRO`}, `valor` (Obl.), `etiqueta` (Opc.)
* **Domicilio**: `id`, `cuenta_id` (FK), `direccion` (Obl.), `etiqueta` (Opc.: fiscal/planta/depósito), `lat`/`lng` (Opc.)

**Notas**

* **No** se guardan roles operativos (remitente, destinatario, etc.) en la Cuenta. **Se asignan dentro del Ticket**.

---

### 2.2 Ubicaciones y Almacenajes

**Ubicación**

* `id`, `nombre`, `tipo` ∈ {`PLANTA`,`ZONA_MIXTA`}, `encargado_nombre` (si PLANTA)
* Geodatos: `lat`/`lng`, `direccion_mapa`, `google_place_id` (opc.)
* Polígono/Accesos (opc.): `geo_poligono`, `accesos[]` (puntos lat/lng + desc.)

**Almacenaje (principal)**

* `id`, `ubicacion_id` (FK), `tipo` ∈ {`SILO`,`SILO_BOLSA`,`GALPON`}, `codigo`, `capacidad_kg` (opc.), `estado` ∈ {`DISPONIBLE`,`OCUPADO`,`FUMIGACION`,`MANTENIMIENTO`,`BLOQUEADO`}
* Geodatos: `lat`/`lng` (opc.)
* Silo Bolsa: `geo_tramo` (polilínea, min. 2 puntos), `longitud_m` (opc.), `sentido` (opc.)

**Sub‑almacenaje**

* `id`, `almacenaje_id` (FK), `tipo` ∈ {`GRANEL`,`BOLSA_25`,`BOLSA_50`,`BIGBAG_500`,`BIGBAG_1000`}, `sector_codigo` (opc.), `descripcion` (opc.)

---

### 2.3 Mercaderías y Movimiento

**Mercadería (catálogo)**

* `id`, `especie` (soja/maíz/girasol/trigo/otros), `calidad_grado` (opc.), `observaciones` (opc.)

**Presentaciones y Unidades (catálogos)**

* `CatalogoPresentacion`: `GRANEL`, `BOLSA_25`, `BOLSA_50`, `BIGBAG_500`, `BIGBAG_1000`
* `UnidadMedida`: `KG`, `TN`, `BOLSAS`, `UNIDADES`
* `FactorConversion`: pares (`TN`→`KG`=1000, etc.)
* `PesoUnitarioReferencia`: por presentación (ej. 25/50/500/1000 kg)
* `ReglaAlmacenajePresentacion`: compatibilidad por `SILO`/`SILO_BOLSA`/`GALPON`

**Movimiento (se guarda en el Ticket)**

* `presentacion_movimiento` (FK a `CatalogoPresentacion`)
* `unidad_medida_mov` (FK a `UnidadMedida`)
* `cantidad_movimiento` (numérico)
* `peso_unitario_opcional` (num., para bolsas/bigbags; si no, usar referencia)
* `condicion_acondicionamiento` (opc.: fumigado, húmedo, procesado)

**Stock (unidad estándar)**

* Toda afectación se consolida en **KG** (conversión desde unidad del movimiento)

---

### 2.4 Vehículos y Personas

* **Vehículo (Tractor/Camión)**: `id`, `dominio` (único), `tara_declarada`, `tara_verificada`, `estado_operativo` ∈ {`HABILITADO`,`OBSERVADO`,`BLOQUEADO`}, `observaciones`
* **Acoplado/Semirremolque**: `id`, `dominio` (único), `tipo`, `tara_declarada`, `tara_verificada`, `estado_operativo`, `observaciones`
* **ConjuntoVehicular**: `id`, `tractor_id` (FK), `acoplados[]` (FK list) — soporta **bitrén**
* **Chofer**: `id`, `nombre` (Obl.), `dni` (opc.), `licencia` (opc.), `licencia_vto` (opc.), `celular` (opc.)
* **Documentación Vehicular**: opcional (null permitido) — `tipo` (RTO/VTV/Seguro/CNRT/otros), `numero`, `vencimiento`, `vehiculo_id/acoplado_id`

---

### 2.5 Ticket (movimiento)

**Tipos**: `ENTRADA` / `SALIDA`
**Estados automáticos**: `EN_PESAJE_ENTRADA` → `CARGA` (si SALIDA) / `DESCARGA` (si ENTRADA) → `EN_PESAJE_SALIDA` → `CERRADO` | `ANULADO`
**Modo**: `modo_valido = true/false` (false = **modo DARK**; lo define Administración)

**Vínculos principales**

* `ubicacion_id` (FK Ubicación)
* `almacenaje_id` (FK Almacenaje, obligatorio antes de `EN_PESAJE_SALIDA` en ENTRADA; en SALIDA para reserva/egreso)
* `subalmacenaje_id` (FK Sub‑almacenaje, opc.)
* `mercaderia_id` (FK Mercadería)
* Vehículos/Personas: `tractor_id` (FK), `acoplado_id` (FK opc.), `conjunto_id` (opc.), `chofer_id` (FK)
* `transportista_cuenta_id` (FK Cuenta tipo principal **sugerido**: TRANSPORTISTA)

**Cuentas en el Ticket (roles operativos)**

* **Entrada**:

  * `origen_cuenta_id` (Obl.) — puede ser **AGL (CUENTA\_PROPIA)** o tercero
  * `remitente_comercial_primario_id` (Obl.)
  * `remitente_comercial_secundario_id` (Opc.)
  * `destino_ubicacion_id` (Opc., si descarga en propia) / `destino_cuenta_id` (Opc., si descarga a tercero)
* **Salida**:

  * `destinatario_cuenta_id` (Obl.) — puede ser **AGL** o cliente/tercero
  * `remitente_cuenta_id` (Opc., si corresponde)
  * `destino_ubicacion_id` (Opc., a propia) / `destino_cuenta_id` (Opc., a tercero)

**Pesajes**

* `peso_bruto_kg` (opc.), `peso_tara_kg` (opc.) → `peso_neto_kg` (derivado, no negativo)

**Movimiento (datos del envío/recepción)**

* `presentacion_movimiento`, `unidad_medida_mov`, `cantidad_movimiento`, `peso_unitario_opcional`, `condicion_acondicionamiento`

**Derivados**

* `resultado_operativo` ∈ {`CARGADO`,`DESCARGADO`} al completar `EN_PESAJE_SALIDA`
* `equivalente_kg` para stock (conversiones según catálogos)

---

## 3. Reglas y Validaciones

1. **Compatibilidad** Presentación × Almacenaje según `ReglaAlmacenajePresentacion`.
2. **Stock** siempre en **KG** (conversiones TN↔KG y bolsas/bigbags por peso unitario).
3. **Estados** avanzan **automáticamente** por acciones (pesajes, asignación, fin de operación). El usuario **no** edita estados manualmente.
4. **Cierre** lo ejecuta **Administración** (marca `modo_valido` y pasa a `CERRADO` o `ANULADO`).
5. **Documentación** (vehicular/licencias) es opcional a nivel de datos; su ausencia puede reflejarse con `modo_valido=false`.

---

## 4. Relaciones (ER textual)

* Ubicación (1) — (N) Almacenaje
* Almacenaje (1) — (N) Sub‑almacenaje
* Mercadería (1) — (N) Ticket
* Cuenta (1..N) — Ticket (como: origen, remitentes, destinatario, destino, transportista)
* Vehículo Tractor (1) — (N) Ticket; Acoplado (0..1) — (N) Ticket; Conjunto (0..1) — (N) Ticket
* Chofer (1) — (N) Ticket
* Catálogos (Presentación/Unidad/Conversiones/Pesos) — (N) Ticket (para movimiento)

---

## 5. Criterios de Aceptación (extracto)

1. **Crear Ticket ENTRADA** con: `origen_cuenta_id`, `remitente_comercial_primario_id`, `mercaderia_id`, vehículo/chofer, `presentacion/unidad/cantidad` ⇒ estado `EN_PESAJE_ENTRADA`.
2. **Registrar pesaje de entrada** ⇒ `DESCARGA` (si ENTRADA) / `CARGA` (si SALIDA).
3. **Asignar almacenaje** compatible (y stock disponible en SALIDA) ⇒ `EN_PESAJE_SALIDA`.
4. **Registrar pesaje de salida** ⇒ fija `resultado_operativo` y `equivalente_kg`.
5. **Cierre** por Administración ⇒ `CERRADO` (o `ANULADO`) y `modo_valido` definido (`true/false`).

---

## 6. Compatibilidad Almacenaje × Presentación (v1)

| Almacenaje.tipo | GRANEL | BOLSA\_25 | BOLSA\_50 | BIGBAG\_500 | BIGBAG\_1000 |
| --------------- | :----: | :-------: | :-------: | :---------: | :----------: |
| SILO            |    ✓   |     –     |     –     |      –      |       –      |
| SILO\_BOLSA     |    ✓   |     –     |     –     |      –      |       –      |
| GALPON          |    ✓   |     ✓     |     ✓     |      ✓      |       ✓      |

---

## 7. Notas finales

* Este documento **reemplaza** la versión previa de diseño para reflejar **Cuentas + Agenda** y los **roles operativos asignados dentro del Ticket**.
* Cuando confirmes, integro estos cambios en el **ER Canvas** y preparo un **checklist** para migrar datos iniciales (catálogos y ubicaciones).

