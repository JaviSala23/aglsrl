"""
Excepciones personalizadas para el módulo de cuentas.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError


class CuentaException(Exception):
    """Excepción base para el módulo de cuentas."""
    pass


class DocumentoDuplicadoError(CuentaException):
    """Error cuando se intenta crear una cuenta con documento duplicado."""
    pass


class DireccionPrincipalError(CuentaException):
    """Error relacionado con direcciones principales."""
    pass


class ContactoSinMediosError(CuentaException):
    """Error cuando un contacto no tiene medios de comunicación."""
    pass


def custom_exception_handler(exc, context):
    """
    Manejador personalizado de excepciones para la API.
    """
    # Llamar al manejador por defecto de DRF
    response = exception_handler(exc, context)
    
    # Si DRF no maneja la excepción, manejarla nosotros
    if response is None:
        custom_response_data = {}
        
        if isinstance(exc, IntegrityError):
            custom_response_data['error'] = 'Error de integridad en la base de datos'
            custom_response_data['detail'] = str(exc)
            custom_response_data['type'] = 'integrity_error'
            
            # Detectar errores específicos
            if 'uq_cuenta_doc' in str(exc):
                custom_response_data['error'] = 'Ya existe una cuenta con este tipo y número de documento'
                custom_response_data['field'] = 'numero_documento'
            elif 'uq_direccion_principal_por_cuenta' in str(exc):
                custom_response_data['error'] = 'Ya existe una dirección principal para esta cuenta'
                custom_response_data['field'] = 'es_principal'
            
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, ValidationError):
            custom_response_data['error'] = 'Error de validación'
            custom_response_data['detail'] = exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            custom_response_data['type'] = 'validation_error'
            
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, DocumentoDuplicadoError):
            custom_response_data['error'] = str(exc)
            custom_response_data['type'] = 'documento_duplicado'
            custom_response_data['field'] = 'numero_documento'
            
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, DireccionPrincipalError):
            custom_response_data['error'] = str(exc)
            custom_response_data['type'] = 'direccion_principal'
            custom_response_data['field'] = 'es_principal'
            
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, ContactoSinMediosError):
            custom_response_data['error'] = str(exc)
            custom_response_data['type'] = 'contacto_sin_medios'
            custom_response_data['fields'] = ['email', 'telefono', 'celular']
            
            return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Personalizar respuesta de DRF si es necesario
    if response is not None:
        custom_response_data = {
            'error': 'Error en la solicitud',
            'type': 'api_error',
            'status_code': response.status_code,
            'detail': response.data
        }
        
        # Mejorar mensajes de errores comunes
        if response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['error'] = 'Recurso no encontrado'
            custom_response_data['type'] = 'not_found'
        
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['error'] = 'No tienes permisos para realizar esta acción'
            custom_response_data['type'] = 'permission_denied'
        
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['error'] = 'Autenticación requerida'
            custom_response_data['type'] = 'unauthorized'
        
        response.data = custom_response_data
    
    return response