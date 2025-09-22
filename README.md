# Proyecto AGL — Versión 1 (Diseño General)

## 🎯 Objetivo

El proyecto **AGL** busca convertirse en un sistema **integral** para la gestión de plantas procesadoras y almacenadoras de granos.
La **Versión 1** constituye el primer paso, enfocado en establecer la **base funcional mínima** que permita:

* Controlar **ingresos y egresos de mercadería** mediante tickets.
* Registrar y administrar **almacenajes** en plantas, galpones, silos y zonas mixtas.
* Gestionar **vehículos, choferes y transportistas**.
* Asociar **mercaderías** a cada movimiento.
* Dejar las bases listas para futuras integraciones comerciales y administrativas.

---

## 🚀 Alcance de la Versión 1

### Núcleo de Datos

* **Ubicaciones**: Plantas (con encargado) y Zonas Mixtas (sin encargado) con geolocalización.
* **Almacenajes**: Silos, Silo bolsa, Galpones.
* **Sub‑almacenajes**: Granel, bolsas (25/50), bigbags (500/1000).
* **Mercaderías**: Catálogo de especies y calidades.
* **Vehículos**: Tractor/camión, acoplado/semi, conjunto vehicular (con soporte de bitrén).
* **Personas**: Choferes y transportistas.
* **Documentación**: Opcional, con posibilidad de registrar RTO, VTV, CNRT, seguros, licencias.

### Tickets

* **Tipos**: Entrada / Salida.
* **Estados automáticos**: `EN_PESAJE_ENTRADA`, `CARGA` (si salida), `DESCARGA` (si entrada), `EN_PESAJE_SALIDA`, `CERRADO`, `ANULADO`.
* **Modo**: atributo separado `modo_valido = true/false` (true = conforme, false = **modo DARK**).
* **Movimientos**: Presentación registrada (granel/bolsas/bigbags), unidad, cantidad, peso unitario opcional, condición de acondicionamiento.
* **Pesajes**: Bruto, tara y neto.

### Reglas Clave

* Compatibilidad **Almacenaje × Presentación**.
* Consolidación de stock en **KG** (independientemente de cómo ingresa/sale).
* Estados avanzan automáticamente según acciones (pesajes, operaciones). El usuario no los actualiza a mano.
* Administración define `modo_valido` y realiza el cierre o anulación de tickets.

---

## 📊 Reportes Iniciales

* **Stock** por ubicación/almacenaje/sub‑almacenaje.
* **Movimientos** de entrada y salida (tickets).
* **Padrón vehicular** (estado operativo, documentación).
* **Alertas de vencimientos** (vehículos y choferes).
* **Consumo/producción** por presentaciones (bolsas/bigbags movidas).

---

## 👥 Roles y Permisos

* **Auxiliar**: crea tickets, registra pesajes.
* **Encargado**: asigna almacenajes, edita y valida operaciones.
* **Administración**: cierra/anula tickets, define `modo_valido`, gestiona documentación.

---

## 🌐 Visión Integral

Aunque esta versión se centra en tickets y almacenajes, el sistema crecerá hacia:

* Comercialización y liquidaciones primarias/ secundarias.
* Emisión de remitos y cartas de porte.
* Gestión de cuentas corrientes y reportes financieros.
* Administración logística y trazabilidad completa.

---

## ✅ Próximos Pasos (dentro de v1)

1. Completar catálogos iniciales (presentaciones, unidades, conversiones, compatibilidad).
2. Registrar ubicaciones base (Planta Norte, Planta Sur, Galpón del Medio, Galpones alquilados, Campo).
3. Modelar almacenajes reales con sectores y tramos.
4. Definir plantillas de tickets (con QR) y reportes de stock/movimientos.
5. Preparar implementación técnica (BD, APIs, interfaz).

---

## 📖 Estado del Proyecto

Actualmente en **fase de análisis y diseño funcional**.
La implementación se realizará en próximas iteraciones, con ayuda de Copilot para el código.
