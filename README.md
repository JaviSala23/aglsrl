# Proyecto AGL — Gestión de Tickets y Almacenaje (Versión 1)

## 📌 Descripción

Este proyecto corresponde a la primera versión de **AGL**, un sistema para la **gestión de tickets de entrada y salida de mercadería** y el **almacenaje en plantas y zonas mixtas**.

Su objetivo inicial es **definir modelos y flujos de negocio**, dejando la implementación para etapas posteriores.

---

## 🚀 Alcance de la Versión 1

* Registro de **Ubicaciones** (plantas con encargado y zonas mixtas sin encargado).
* Registro de **Almacenajes** (silos, silos bolsa, galpones) y **Sub‑almacenajes**.
* Catálogo de **Mercaderías** (especies, calidades).
* Registro de **Vehículos, Acoplados, Conjuntos vehiculares, Choferes y Transportistas**.
* Creación y gestión de **Tickets** (Entrada / Salida) con estados y validación.
* Definición de **Roles y Permisos** (Auxiliar, Encargado, Administración).
* **Geolocalización** de ubicaciones y almacenajes con soporte Google Maps.
* Normalización de **Presentaciones y Unidades** con reglas de conversión a KG.

---

## 📂 Estructura de Modelos

* **Ubicación → Almacenaje → Sub‑almacenaje**
* **Mercadería** (catálogo)
* **Vehículos** (tractor, acoplado, conjunto vehicular)
* **Personas** (chofer, transportista)
* **Ticket** (movimiento)
* **Catálogos de apoyo** (presentaciones, unidades, conversiones, compatibilidad)

---

## 🔄 Flujos de Ticket

### Entrada

1. Creación → `EN_PESAJE_ENTRADA`
2. Operación → `DESCARGA`
3. Pesaje salida → resultado `DESCARGADO`
4. Administración → `CERRADO` o `ANULADO` + `modo_valido = true/false`

### Salida

1. Creación → `EN_PESAJE_ENTRADA`
2. Operación → `CARGA`
3. Pesaje salida → resultado `CARGADO`
4. Administración → `CERRADO` o `ANULADO` + `modo_valido = true/false`

---

## 📊 Estados del Ticket

* `EN_PESAJE_ENTRADA`
* `CARGA` (para salida)
* `DESCARGA` (para entrada)
* `EN_PESAJE_SALIDA`
* `CERRADO`
* `ANULADO`

**Modo:** atributo separado `modo_valido = true/false`

* `true` = conforme/documentación correcta
* `false` = **modo DARK** (documentación pendiente u observaciones)

---

## 🗂 Compatibilidad Almacenaje × Presentación

| Almacenaje.tipo | GRANEL | BOLSA\_25 | BOLSA\_50 | BIGBAG\_500 | BIGBAG\_1000 |
| --------------- | :----: | :-------: | :-------: | :---------: | :----------: |
| SILO            |    ✓   |     –     |     –     |      –      |       –      |
| SILO\_BOLSA     |    ✓   |     –     |     –     |      –      |       –      |
| GALPON          |    ✓   |     ✓     |     ✓     |      ✓      |       ✓      |

---

## ✅ Próximos Pasos

* Completar catálogos iniciales (presentaciones, unidades, conversiones).
* Registrar ubicaciones base: Planta Norte, Planta Sur, Galpón del Medio, Galpones alquilados A/B, Campo.
* Armar plantillas de tickets (con QR) y reportes básicos.
* Iniciar implementación con ayuda de Copilot.

---

## 🌐 Visión del Proyecto Integral

El proyecto **AGL** no se limita a la gestión de tickets y almacenaje. La **Versión 1** representa únicamente la base inicial.

En el futuro se prevé incorporar módulos adicionales como:

* Comercialización (ventas, compras, liquidaciones primarias y secundarias).
* Gestión de documentos oficiales (remitos, cartas de porte, retenciones).
* Administración integral (contabilidad, cuentas corrientes, reportes financieros).
* Logística avanzada (seguimiento de transportes, asignación de recursos).
* Integración con sistemas externos (AFIP, ARCA, proveedores y clientes).

El **alcance integral** está en definición y se irá documentando a medida que avance el ciclo de vida del proyecto.

---

## 📖 Licencia

Este proyecto se encuentra en análisis funcional. La licencia de uso se definirá en futuras versiones.
