"""
Validadores personalizados para el módulo de cuentas.
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _


class CUITValidator(BaseValidator):
    """Validador para CUIT argentino."""
    
    message = _('CUIT inválido. Debe tener el formato XX-XXXXXXXX-X')
    code = 'invalid_cuit'
    
    def __init__(self, message=None):
        if message is not None:
            self.message = message
    
    def __call__(self, value):
        """Validar formato y dígito verificador del CUIT."""
        if not value:
            return
        
        # Limpiar formato
        cuit = re.sub(r'[^\d]', '', str(value))
        
        if len(cuit) != 11:
            raise ValidationError(self.message, code=self.code)
        
        # Validar dígito verificador
        if not self._validar_digito_verificador(cuit):
            raise ValidationError(
                _('CUIT inválido. El dígito verificador no es correcto.'),
                code=self.code
            )
    
    def _validar_digito_verificador(self, cuit):
        """Calcular y validar dígito verificador del CUIT."""
        multiplicadores = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(cuit[i]) * multiplicadores[i] for i in range(10))
        resto = suma % 11
        
        if resto < 2:
            digito_calculado = resto
        else:
            digito_calculado = 11 - resto
        
        return int(cuit[10]) == digito_calculado


class DNIValidator(BaseValidator):
    """Validador para DNI argentino."""
    
    message = _('DNI inválido. Debe tener entre 7 y 8 dígitos.')
    code = 'invalid_dni'
    
    def __init__(self, message=None):
        if message is not None:
            self.message = message
    
    def __call__(self, value):
        """Validar formato del DNI."""
        if not value:
            return
        
        # Limpiar formato
        dni = re.sub(r'[^\d]', '', str(value))
        
        if not (7 <= len(dni) <= 8):
            raise ValidationError(self.message, code=self.code)
        
        if not dni.isdigit():
            raise ValidationError(self.message, code=self.code)


class TelefonoArgentinoValidator(BaseValidator):
    """Validador para números de teléfono argentinos."""
    
    message = _('Número de teléfono inválido. Formato: +54 11 1234-5678 o 011 1234-5678')
    code = 'invalid_phone'
    
    def __init__(self, message=None):
        if message is not None:
            self.message = message
    
    def __call__(self, value):
        """Validar formato de teléfono argentino."""
        if not value:
            return
        
        # Patrones aceptados
        patterns = [
            r'^\+54\s?\d{2,4}\s?\d{4}-?\d{4}$',  # +54 11 1234-5678
            r'^0\d{2,4}\s?\d{4}-?\d{4}$',        # 011 1234-5678
            r'^\d{8,10}$',                       # 1112345678
        ]
        
        if not any(re.match(pattern, str(value).strip()) for pattern in patterns):
            raise ValidationError(self.message, code=self.code)


def validar_documento_por_tipo(numero_documento, tipo_documento):
    """
    Validar número de documento según su tipo.
    
    Args:
        numero_documento (str): Número del documento
        tipo_documento (TipoDocumento): Instancia del tipo de documento
    
    Raises:
        ValidationError: Si el documento no es válido para el tipo
    """
    if not numero_documento or not tipo_documento:
        return
    
    tipo_desc = tipo_documento.descripcion.upper()
    
    if 'CUIT' in tipo_desc:
        validator = CUITValidator()
        validator(numero_documento)
    elif 'DNI' in tipo_desc:
        validator = DNIValidator()
        validator(numero_documento)
    elif 'CUIL' in tipo_desc:
        # CUIL tiene el mismo formato que CUIT
        validator = CUITValidator()
        validator(numero_documento)


def validar_email_empresarial(email, razon_social=None):
    """
    Validar si un email parece ser empresarial (opcional).
    
    Args:
        email (str): Email a validar
        razon_social (str): Razón social para validaciones adicionales
    
    Returns:
        bool: True si parece email empresarial
    """
    if not email:
        return False
    
    # Dominios comunes no empresariales
    dominios_personales = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'yahoo.com.ar', 'hotmail.com.ar'
    ]
    
    dominio = email.split('@')[-1].lower()
    return dominio not in dominios_personales


def validar_coherencia_geografica(pais=None, provincia=None, localidad=None):
    """
    Validar coherencia geográfica entre país, provincia y localidad.
    
    Args:
        pais: Instancia de país
        provincia: Instancia de provincia  
        localidad: Instancia de localidad
    
    Raises:
        ValidationError: Si la coherencia geográfica no es correcta
    """
    if localidad and provincia:
        if localidad.provincia_id_provincia != provincia:
            raise ValidationError(
                _('La localidad no pertenece a la provincia seleccionada.')
            )
    
    if provincia and pais:
        if provincia.pais_idpais != pais:
            raise ValidationError(
                _('La provincia no pertenece al país seleccionado.')
            )