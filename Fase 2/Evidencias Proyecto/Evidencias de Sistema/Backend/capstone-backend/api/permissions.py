# api/permissions.py
from rest_framework import permissions
from .models import Usuario # Importamos el modelo Usuario que mapea apt.usuario

# --- Permisos Base por Rol (Se mantienen iguales) ---

class IsAdminUser(permissions.BasePermission):
    """Permiso: Solo rol 'ADMIN'."""
    message = "Acción restringida a administradores."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol == 'ADMIN'
        except Usuario.DoesNotExist:
            return False

class IsSupervisorUser(permissions.BasePermission):
    """Permiso: Solo rol 'SUPERVISOR'."""
    message = "Acción restringida a supervisores."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol == 'SUPERVISOR'
        except Usuario.DoesNotExist:
            return False

class IsMecanicoUser(permissions.BasePermission):
    """Permiso: Solo rol 'MECANICO'."""
    message = "Acción restringida a mecánicos."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol == 'MECANICO'
        except Usuario.DoesNotExist:
            return False

class IsPorteriaUser(permissions.BasePermission):
    """Permiso: Solo rol 'PORTERIA' o 'GUARDIA'."""
    message = "Acción restringida a personal de portería."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol in ['PORTERIA', 'GUARDIA']
        except Usuario.DoesNotExist:
            return False

class IsChoferUser(permissions.BasePermission):
    """Permiso: Solo rol 'CHOFER'."""
    message = "Acción restringida a usuarios con rol Chofer."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol == 'CHOFER'
        except Usuario.DoesNotExist:
            return False

class IsAnalistaUser(permissions.BasePermission):
    """Permiso: Solo rol 'ANALISTA' (o 'INDICADORES')."""
    message = "Acción restringida a analistas."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol == 'ANALISTA'
        except Usuario.DoesNotExist:
            return False

# --- Combinaciones Comunes de Permisos (Incluyen ADMIN para desarrollo) ---

class IsSupervisorOrAdminUser(permissions.BasePermission):
    """Permiso: 'SUPERVISOR' o 'ADMIN'."""
    message = "Acción restringida a supervisores o administradores."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol in ['SUPERVISOR', 'ADMIN'] # ADMIN ya está aquí
        except Usuario.DoesNotExist:
            return False

class IsMecanicoOrSupervisorUser(permissions.BasePermission):
    """Permiso: 'MECANICO', 'SUPERVISOR' o 'ADMIN' (Modificado)."""
    message = "Acción restringida a mecánicos, supervisores o administradores." # Mensaje actualizado

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            # 🔑 MODIFICACIÓN CLAVE: Añadimos 'ADMIN'
            return perfil.rol in ['MECANICO', 'SUPERVISOR', 'ADMIN']
        except Usuario.DoesNotExist:
            return False

class IsSupervisorOrAdminOrAnalistaUser(permissions.BasePermission):
    """Permiso: 'SUPERVISOR', 'ADMIN' o 'ANALISTA'."""
    message = "Acción restringida a supervisores, administradores o analistas."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            return perfil.rol in ['SUPERVISOR', 'ADMIN', 'ANALISTA'] # ADMIN ya está aquí
        except Usuario.DoesNotExist:
            return False

class IsPorteriaOrSupervisorOrAdminOrAnalista(permissions.BasePermission):
    """Permiso: Cualquiera que necesite ver la lista de bitácora."""
    message = "Acción restringida a roles de Portería, Supervisor, Administrador o Analista."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            perfil = Usuario.objects.get(external_id=request.user.username)
            # Lista todos los roles permitidos para ver (Portería, Supervisor, Admin, Analista, Guardia)
            return perfil.rol in ['PORTERIA', 'GUARDIA', 'SUPERVISOR', 'ADMIN', 'ANALISTA']
        except Usuario.DoesNotExist:
            return False
        


        