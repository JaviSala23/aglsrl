"""
Utilidad para parsear Cartas de Porte Electrónicas (CPE) de ARCA/AFIP.
Soporta archivos PDF nativos.
Para imágenes (fotos/scan) se requiere instalar: pillow + pytesseract + tesseract-ocr.
"""
import re
import io
from typing import Optional


# ─────────────────────────────────────────────
# PARSER PRINCIPAL
# ─────────────────────────────────────────────

def parsear_cpe_pdf(archivo) -> dict:
    """
    Recibe un objeto file-like o ruta a un PDF de CPE.
    Retorna un dict con los campos extraídos.
    Los valores son None si no se encontraron.
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("Instalar pdfplumber: pip install pdfplumber")

    with pdfplumber.open(archivo) as pdf:
        texto = "\n".join(p.extract_text() or "" for p in pdf.pages)

    return _extraer_campos(texto)


def parsear_cpe_imagen(archivo) -> dict:
    """
    Recibe un objeto file-like o ruta a una imagen (jpg, png, tiff, webp).
    Usa OCR con pytesseract. Requiere tesseract instalado en el sistema.
    """
    try:
        from PIL import Image
        import pytesseract
    except ImportError:
        raise ImportError(
            "Para OCR instalar: pip install pillow pytesseract\n"
            "Y el binario: sudo apt install tesseract-ocr tesseract-ocr-spa"
        )

    img = Image.open(archivo)
    texto = pytesseract.image_to_string(img, lang='spa')
    return _extraer_campos(texto)


def parsear_cpe_auto(archivo, nombre_archivo: str) -> dict:
    """
    Detecta automáticamente si es PDF o imagen y llama al método correcto.
    """
    nombre = nombre_archivo.lower()
    if nombre.endswith('.pdf'):
        return parsear_cpe_pdf(archivo)
    elif any(nombre.endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.tiff', '.tif', '.webp', '.bmp')):
        return parsear_cpe_imagen(archivo)
    else:
        raise ValueError(f"Formato no soportado: {nombre_archivo}. Use PDF o imagen (jpg, png, tiff).")


# ─────────────────────────────────────────────
# EXTRACCIÓN DE CAMPOS CON REGEX
# ─────────────────────────────────────────────

def _extraer_campos(texto: str) -> dict:
    """Extrae todos los campos relevantes de la CPE a partir del texto completo."""

    def buscar(patron: str, flags: int = 0) -> Optional[str]:
        m = re.search(patron, texto, re.IGNORECASE | flags)
        return m.group(1).strip() if m else None

    def buscar_interviniente(campo: str) -> Optional[dict]:
        """Extrae el par CUIT - Nombre de un campo de interviniente."""
        m = re.search(
            rf'{re.escape(campo)}[:\s]*\n?([\d]{{11}}\s*[-–]\s*[^\n]+)',
            texto,
            re.IGNORECASE,
        )
        if not m:
            return None
        raw = m.group(1).strip()
        partes = re.split(r'\s*[-–]\s*', raw, maxsplit=1)
        return {
            'cuit': partes[0].strip().replace('.', '').replace('-', ''),
            'nombre': partes[1].strip() if len(partes) > 1 else '',
        }

    # ── Identificación del documento ──
    nro_cpe = buscar(r'N°\s*CPE[:\s]*\n?([\d\-]+)')
    ctg = buscar(r'CTG[:\s]*([\d]+)')

    # ── Dominios / patentes ──
    dominios_raw = buscar(r'Dominios?[:\s]*([\w]+(?:\s*[-–]\s*[\w]+)*)')
    patentes = [p.strip() for p in re.split(r'\s*[-–]\s*', dominios_raw)] if dominios_raw else []

    # ── Grano/especie ──
    grano_raw = buscar(r'Tipo[:\s]+([^\n\(]+)')
    grano = grano_raw.strip() if grano_raw else None

    # ── Pesos declarados en la CPE ──
    peso_bruto_cpe = buscar(r'Peso Bruto\s*\n?([\d]+)')
    peso_neto_cpe = buscar(r'Peso Neto\s*\n?([\d]+)')
    peso_tara_cpe = buscar(r'Peso Tara\s*\n?([\d]+)')

    # ── Campaña ──
    campana = buscar(r'Campa[ñn]a[:\s]*([\d]+)')

    # ── Intervinientes ──
    titular = buscar_interviniente('Titular Carta de Porte')
    destinatario = buscar_interviniente('Destinatario')
    transportista = buscar_interviniente('Empresa Transportista')
    chofer = buscar_interviniente('Chofer') or buscar_interviniente('Intermediario de flete')

    # ── Procedencia (sección C, acotada hasta la D) ──
    seccion_c = re.search(r'C - PROCEDENCIA(.*?)(?:D - DESTINO|E - DATOS)', texto, re.DOTALL | re.IGNORECASE)
    bloque_c = seccion_c.group(1) if seccion_c else ''
    # Localidad y Provincia pueden estar en la misma línea (layout columnar del PDF)
    loc_prov_c = re.search(
        r'Localidad[:\s]*\n?([A-Za-záéíóúüñÁÉÍÓÚÜÑ][^\n]*?)\s+Provincia[:\s]*([A-Za-záéíóúüñÁÉÍÓÚÜÑ][^\n]+)',
        bloque_c, re.IGNORECASE
    )
    # Fallback: solo localidad si no se encontró el patrón combinado
    if loc_prov_c:
        localidad_origen = loc_prov_c.group(1).strip()
        provincia_origen = loc_prov_c.group(2).strip()
    else:
        m_loc = re.search(r'Localidad[:\s]*\n?([^\n]+)', bloque_c, re.IGNORECASE)
        localidad_origen = m_loc.group(1).strip() if m_loc else None
        provincia_origen = None

    # ── Destino (sección D, acotada hasta la E) ──
    seccion_d = re.search(r'D - DESTINO(.*?)(?:E - DATOS|F - CONTINGENCIAS)', texto, re.DOTALL | re.IGNORECASE)
    bloque_d = seccion_d.group(1) if seccion_d else ''
    loc_prov_d = re.search(
        r'Localidad[:\s]*\n?([A-Za-záéíóúüñÁÉÍÓÚÜÑ][^\n]*?)\s+Provincia[:\s]*([A-Za-záéíóúüñÁÉÍÓÚÜÑ][^\n]+)',
        bloque_d, re.IGNORECASE
    )
    if loc_prov_d:
        localidad_destino = loc_prov_d.group(1).strip()
        provincia_destino = loc_prov_d.group(2).strip()
    else:
        m_loc_d = re.search(r'Localidad[:\s]*\n?([^\n]+)', bloque_d, re.IGNORECASE)
        localidad_destino = m_loc_d.group(1).strip() if m_loc_d else None
        provincia_destino = None

    # ── Fecha y vencimiento ──
    fecha_emision = buscar(r'Fecha[:\s]*([\d]{2}/[\d]{2}/[\d]{4})')
    vencimiento = buscar(r'Vencimiento[:\s]*\n?([\d]{2}/[\d]{2}/[\d]{4})')

    return {
        # Documento
        'nro_cpe': nro_cpe,
        'ctg': ctg,
        'fecha_emision': fecha_emision,
        'vencimiento': vencimiento,
        'campana': campana,

        # Transporte
        'patente_camion': patentes[0] if patentes else '',
        'patente_acoplado_1': patentes[1] if len(patentes) > 1 else '',
        'patente_acoplado_2': patentes[2] if len(patentes) > 2 else '',

        # Grano
        'grano_nombre': grano,

        # Pesos declarados (referencia, no son los de la balanza)
        'peso_bruto_cpe': int(peso_bruto_cpe) if peso_bruto_cpe else None,
        'peso_neto_cpe': int(peso_neto_cpe) if peso_neto_cpe else None,
        'peso_tara_cpe': int(peso_tara_cpe) if peso_tara_cpe else None,

        # Intervinientes
        'titular': titular,
        'destinatario': destinatario,
        'transportista': transportista,
        'chofer': chofer,

        # Procedencia → Destino
        'localidad_origen': localidad_origen,
        'provincia_origen': provincia_origen,
        'localidad_destino': localidad_destino,
        'provincia_destino': provincia_destino,
    }


# ─────────────────────────────────────────────
# MATCHING CON BASE DE DATOS DJANGO
# ─────────────────────────────────────────────

def buscar_o_sugerir_en_bd(datos_cpe: dict) -> dict:
    """
    Intenta cruzar los datos extraídos de la CPE con registros existentes en la BD.
    Retorna el dict con campos adicionales _id e _display cuando encuentra coincidencias.
    """
    from cuentas.models import cuenta as Cuenta
    from mercaderias.models import Grano
    from transportes.models import Chofer, Camion

    resultado = dict(datos_cpe)

    # ── Buscar cuenta del remitente (titular/origen) ──
    titular = datos_cpe.get('titular')
    if titular and titular.get('cuit'):
        cuit_limpio = re.sub(r'[^0-9]', '', titular['cuit'])
        try:
            c = Cuenta.objects.filter(numero_documento=cuit_limpio).first()
            resultado['cuenta_origen_id'] = c.pk if c else None
            resultado['cuenta_origen_display'] = str(c) if c else f"{titular['nombre']} (CUIT: {cuit_limpio} — no registrado)"
        except Exception:
            resultado['cuenta_origen_id'] = None
            resultado['cuenta_origen_display'] = titular.get('nombre', '')

    # ── Buscar cuenta del transportista ──
    transportista = datos_cpe.get('transportista')
    if transportista and transportista.get('cuit'):
        cuit_limpio = re.sub(r'[^0-9]', '', transportista['cuit'])
        try:
            c = Cuenta.objects.filter(numero_documento=cuit_limpio).first()
            resultado['cuenta_transporte_id'] = c.pk if c else None
            resultado['cuenta_transporte_display'] = str(c) if c else f"{transportista['nombre']} (no registrado)"
        except Exception:
            resultado['cuenta_transporte_id'] = None
            resultado['cuenta_transporte_display'] = transportista.get('nombre', '')

    # ── Buscar chofer ──
    chofer = datos_cpe.get('chofer')
    if chofer and chofer.get('cuit'):
        cuit_limpio = re.sub(r'[^0-9]', '', chofer['cuit'])
        try:
            ch = Chofer.objects.filter(cuit__contains=cuit_limpio).first()
            resultado['chofer_id'] = ch.pk if ch else None
            resultado['chofer_display'] = str(ch) if ch else f"{chofer['nombre']} (no registrado)"
        except Exception:
            resultado['chofer_id'] = None
            resultado['chofer_display'] = chofer.get('nombre', '')

    # ── Buscar grano ──
    grano_nombre = datos_cpe.get('grano_nombre')
    if grano_nombre:
        # Buscar por nombre aproximado (ej: "POROTO COLORADO" → busca "poroto")
        palabras = grano_nombre.upper().split()
        grano_obj = None
        for palabra in palabras:
            if len(palabra) > 3:
                grano_obj = Grano.objects.filter(nombre__icontains=palabra).first()
                if grano_obj:
                    break
        resultado['grano_id'] = grano_obj.pk if grano_obj else None
        resultado['grano_display'] = str(grano_obj) if grano_obj else f"{grano_nombre} (no registrado)"

    return resultado
