from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario


class PerfilInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('tipo_usuario', 'planta', 'telefono', 'activo')


class UserAdminConPerfil(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_tipo', 'get_planta', 'is_active')
    list_select_related = ('perfil',)

    def get_tipo(self, obj):
        try:
            return obj.perfil.get_tipo_usuario_display()
        except PerfilUsuario.DoesNotExist:
            return '-'
    get_tipo.short_description = 'Rol'

    def get_planta(self, obj):
        try:
            return obj.perfil.planta.nombre if obj.perfil.planta else '-'
        except PerfilUsuario.DoesNotExist:
            return '-'
    get_planta.short_description = 'Planta'


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'planta', 'activo')
    list_filter = ('tipo_usuario', 'planta', 'activo')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ('user',)
    autocomplete_fields = ['planta']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'planta')


# Reemplazar el UserAdmin por defecto con el extendido
admin.site.unregister(User)
admin.site.register(User, UserAdminConPerfil)
