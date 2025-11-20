# capstone-backend/api/serializers.py
import os # Necesario para leer variables de entorno
from rest_framework import serializers
from django.utils import timezone # Necesaria para asignar fechas
from datetime import timedelta
import re # <--- AÑADIDO: Importar para la validación del RUT
# capstone-backend/api/views.py
# (Asegúrate de que 'get_object_or_404', 'Http404', 'Vehiculo' y 'Ot' estén importados)
from django.shortcuts import get_object_or_404
from django.http import Http404
# --- IMPORTACIONES DE MODELOS ---
# CORREGIDO: Asegúrate que AuditLog esté en esta línea si está en models.py
from .models import Vehiculo, BitacoraPorteria, Estado, Usuario, Ot, Tarea, Pausa, Evidencia, AuditLog, Repuesto, TareaRepuesto

# --- IMPORTACIONES ADICIONALES ---
from rest_framework.serializers import CurrentUserDefault # Para asignar usuario actual

# ==================================
# --- SERIALIZERS PARA VEHICULO ---
# ==================================
class UsuarioSerializer(serializers.ModelSerializer):
    """ Serializer de solo lectura para la información pública de un Usuario. """
    class Meta:
        model = Usuario # Asegúrate de que 'Usuario' esté importado de .models
        fields = ['id', 'nombre', 'rol', 'email', 'rut', 'numero_telefonico']
        read_only_fields = fields
# EN capstone-backend/api/serializers.py

# ... (Dentro de la sección de SERIALIZERS PARA VEHICULO) ...

# 1. ACTUALIZACIÓN DE VEHICULOSERIALIZER (LECTURA)
# 1. PRIMERO DEFINE ESTE (El historial)
class VehiculoPatenteHistSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import VehiculoPatenteHist # Importación local por si acaso
        model = VehiculoPatenteHist
        fields = ['id', 'patente', 'desde', 'hasta']

# 2. DESPUÉS DEFINE ESTE (El vehículo principal)
class VehiculoSerializer(serializers.ModelSerializer):
    """ Serializer de solo lectura para Vehiculo (usado en respuestas GET y anidado) """
    chofer = UsuarioSerializer(read_only=True) 
    
    # Ahora sí funciona porque la clase de arriba ya existe
    historial_patentes = VehiculoPatenteHistSerializer(many=True, read_only=True) 

    class Meta:
        model = Vehiculo
        fields = ["id", "patente", "marca", "modelo", "chofer", "creado_en", "historial_patentes"]
        read_only_fields = fields 



# En capstone-backend/api/serializers.py

class VehiculoCreateSerializer(serializers.ModelSerializer):
    """ (POST) Crea un vehículo. Ahora permite chofer_id NULO. """
    
    chofer_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False,   # <--- AHORA ES OPCIONAL
        allow_null=True,  # <--- ACEPTA 'null'
        write_only=True
    )
    
    class Meta:
        model = Vehiculo
        fields = ["patente", "marca", "modelo", "chofer_id"] 

    def validate_patente(self, v):
        # ... (Tu validación de patente sigue igual) ...
        import re
        # Limpiar y validar
        v_limpia = v.upper().replace("-", "").replace(" ", "")
        if not (re.match(r"^[A-Z]{2}[0-9]{4}$", v_limpia) or
                re.match(r"^[A-Z]{4}[0-9]{2}$", v_limpia)):
            raise serializers.ValidationError("Patente inválida (formato AA1234 o BBBB12).")
        return v_limpia

    def create(self, validated_data):
        # Extraemos el chofer_id de forma segura
        chofer_instance = validated_data.pop('chofer_id', None) # Si no viene, es None
        
        validated_data['chofer'] = chofer_instance 
        
        from django.utils import timezone
        validated_data['creado_en'] = timezone.now()
        
        return Vehiculo.objects.create(**validated_data)
    
class VehiculoUpdateSerializer(serializers.ModelSerializer):
    """ (PUT/PATCH) Actualiza vehículo. Permite chofer_id nulo y valida patentes. """
    
    # Permite desasignar al chofer enviando null
    chofer_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=False,
        allow_null=True, 
        write_only=True
    )
    
    class Meta:
        model = Vehiculo
        fields = ["patente", "marca", "modelo", "chofer_id"]

    # --- 🌟 ESTO ES LO QUE TE FALTA ---
    def validate_patente(self, value):
        """ Limpia y valida el formato antes de guardar. """
        import re
        if not value: return value
        
        # 1. Forzar mayúsculas y limpiar
        patente_limpia = value.upper().replace("-", "").replace(" ", "")
        
        # 2. Validar regex (AA1234 o BBBB12)
        es_vieja = re.match(r"^[A-Z]{2}[0-9]{4}$", patente_limpia)
        es_nueva = re.match(r"^[A-Z]{4}[0-9]{2}$", patente_limpia)
        
        if not (es_vieja or es_nueva):
            raise serializers.ValidationError("Formato inválido. Usa AA1234 o BBBB12.")
            
        return patente_limpia
    # ----------------------------------

    def update(self, instance, validated_data):
        if 'chofer_id' in validated_data:
            chofer_instance = validated_data.pop('chofer_id')
            instance.chofer = chofer_instance
        
        # Aquí validated_data['patente'] ya vendrá limpia y en mayúsculas
        return super().update(instance, validated_data)
# EN capstone-backend/api/serializers.py
# ... (Al final del archivo, antes de la sección de Auditoría) ...

class ChoferContactoCreateSerializer(serializers.ModelSerializer):
    """ Serializer para que el Supervisor cree un Chofer de contacto (sin Auth de Supabase). """
    
    class Meta:
        model = Usuario
        # El rol y external_id se inyectarán en la vista
        
        # --- CORRECCIÓN ---
        # Añade 'id' a la lista de fields para que la respuesta 201 lo devuelva.
        fields = ["id", "nombre", "rut", "numero_telefonico", "email"]
        
        extra_kwargs = {
            'id': {'read_only': True}, # Asegura que el ID sea solo de lectura
            'email': {'required': True, 'allow_null': False},
            'rut': {'required': True, 'allow_blank': False},
        }
        
    def validate_rut(self, value):
        # ... (sin cambios) ...
        import re
        if not value:
            raise serializers.ValidationError("El RUT es obligatorio.")
        rut_clean = re.sub(r'[^0-9kK]', '', value).upper()
        if not re.match(r'^\d{7,8}[0-9K]$', rut_clean):
            raise serializers.ValidationError("Formato de RUT inválido.")
        return f"{rut_clean[:-1]}-{rut_clean[-1]}"

    def validate_numero_telefonico(self, value):
        # ... (sin cambios) ...
        import re
        if not value: return None
        phone_clean = re.sub(r'[\s()-]', '', value)
        # 🌟 NOTA: Has arreglado el número a 9 dígitos ("957750521"), así que esta regla funciona.
        if not re.match(r'^\+?\d{8,15}$', phone_clean):
            raise serializers.ValidationError("Formato de número inválido.")
        return phone_clean

# ====================================
# --- SERIALIZER PARA BITACORA ---
# ====================================

class BitacoraSerializer(serializers.ModelSerializer):
    # --- 1. CAMPO DE LECTURA (GET) ---
    # Muestra el objeto completo del vehículo al leer la bitácora.
    vehiculo = VehiculoSerializer(read_only=True)
    
    # --- 2. CAMPO DE ESCRITURA (POST) ---
    # Acepta solo el ID del vehículo al crear un registro.
    vehiculo_id = serializers.PrimaryKeyRelatedField(
        queryset=Vehiculo.objects.all(),
        write_only=True,
        source='vehiculo' # Mapea este campo al campo 'vehiculo' del modelo
    )
    
    # (usuario_id se mantiene igual)
    usuario_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = BitacoraPorteria
        # --- 3. ACTUALIZA LOS FIELDS ---
        # 'vehiculo' es para la lectura (GET)
        # 'vehiculo_id' es para la escritura (POST)
        fields = ["id", "vehiculo", "vehiculo_id", "tipo", "fecha_hora", "usuario_id"]
        extra_kwargs = {
            'fecha_hora': {'required': False}
        }

    # --- 4. MÉTODO CREATE CORREGIDO ---
    def create(self, validated_data):
        # 'validated_data' ya contiene la instancia de Vehiculo 
        # gracias a 'source="vehiculo"' en el PrimaryKeyRelatedField.
        
        if 'fecha_hora' not in validated_data:
             validated_data['fecha_hora'] = timezone.now()
        
        return BitacoraPorteria.objects.create(**validated_data)

# ==================================
# --- SERIALIZERS PARA ESTADO ---
# ==================================

class EstadoSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo Estado (solo lectura). """
    class Meta:
        model = Estado
        fields = ["id", "tipo", "code", "label"]
        read_only_fields = fields

# ==================================
# --- SERIALIZERS PARA USUARIO ---
# ==================================

class UsuarioSerializer(serializers.ModelSerializer):
    """ Serializer para el modelo Usuario (perfil apt.usuario, solo lectura). """
    class Meta:
        model = Usuario
        # Campo añadido: numero_telefonico
        fields = ["id", "nombre", "rut", "numero_telefonico", "rol"] 
        read_only_fields = fields

# ==================================================
# --- SERIALIZERS PARA ORDEN DE TRABAJO (OT) ---
# ==================================================

class OtCreateSerializer(serializers.ModelSerializer):
    """ Serializer para CREAR una nueva OT (POST /api/v1/ot). """
    vehiculo = serializers.PrimaryKeyRelatedField(queryset=Vehiculo.objects.all())
    creado_por = serializers.HiddenField(default=CurrentUserDefault())
    estado = serializers.PrimaryKeyRelatedField(
        queryset=Estado.objects.filter(tipo='ot', code='ACTIVA'),
        default=lambda: Estado.objects.get(tipo='ot', code='ACTIVA')
    )

    class Meta:
        model = Ot
        fields = ["vehiculo", "descripcion", "creado_por", "estado"]

    def create(self, validated_data):
        validated_data['vehiculo_id'] = validated_data.pop('vehiculo').id
        drf_user = validated_data.pop('creado_por')
        try:
            # Usamos request.user.username que contiene el UUID de Supabase
            perfil_usuario = Usuario.objects.get(external_id=drf_user.username)
            validated_data['creado_por_id'] = perfil_usuario.id
        except Usuario.DoesNotExist:
            validated_data['creado_por_id'] = None # O manejar error si es obligatorio
        validated_data['estado_id'] = validated_data.pop('estado').id
        now = timezone.now()
        validated_data['fecha_apertura'] = now # Forzamos la fecha
        validated_data['actualizado_en'] = now # Forzamos la fecha
        return Ot.objects.create(**validated_data)

class OtSerializer(serializers.ModelSerializer):
    """ Serializer para LEER OTs (GET /api/v1/ot y GET /api/v1/ot/<id>). """
    vehiculo = VehiculoSerializer(read_only=True)
    estado = EstadoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)
    
    # --- 1. AÑADE ESTA LÍNEA ---
    # Este campo se poblará con la anotación de la vista
    tareas_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Ot
        fields = [
            "id", "vehiculo", "estado", "descripcion",
            "fecha_apertura", "fecha_cierre", "creado_por", "actualizado_en",
            "tareas_count", # <-- 2. AÑADE EL CAMPO A LA LISTA
        ]
        read_only_fields = fields

class OtUpdateSerializer(serializers.ModelSerializer):
    """ Serializer para ACTUALIZAR una OT (PUT /api/v1/ot/<id>). """
    class Meta:
        model = Ot
        fields = ["descripcion"] # Solo permitimos editar descripción por ahora
        extra_kwargs = {
            'descripcion': {'required': False, 'allow_null': True},
        }

    def update(self, instance, validated_data):
        validated_data['actualizado_en'] = timezone.now() # Forzamos actualización
        return super().update(instance, validated_data)

class OtCambiarEstadoSerializer(serializers.Serializer):
    """ 
    Serializer para cambiar el estado de una OT.
    """
    estado_code = serializers.CharField(
        required=True,
        help_text="Código del nuevo estado (ej: 'PAUSADA', 'CERRADA')."
    )
    notas = serializers.CharField(required=False, allow_blank=True)

    def validate_estado_code(self, value):
        # CORRECCIÓN: Usamos 'tipo__iexact' para ignorar mayúsculas/minúsculas.
        # Esto soluciona que no encuentre el estado 'ot' cuando envías 'PAUSADA'.
        existe = Estado.objects.filter(tipo__iexact='ot', code=value, activo=True).exists()
        
        if not existe:
            raise serializers.ValidationError(
                f"El estado '{value}' no es válido para una Orden de Trabajo."
            )
        return value
    # motivo = serializers.CharField(required=False, allow_blank=True, max_length=200) # Opcional

    # validate() se puede usar para lógica de transición si es necesario

# =======================================================
# --- SERIALIZERS ESPECÍFICOS (CHOFER Y PÚBLICO) ---
# =======================================================

class OtEstadoChoferSerializer(serializers.ModelSerializer):
    """ Serializer simplificado para la vista del Chofer (GET /api/v1/mi-estado). """
    estado = EstadoSerializer(read_only=True)

    class Meta:
        model = Ot
        fields = ["id", "descripcion", "estado", "fecha_apertura", "actualizado_en"]
        read_only_fields = fields

class PublicOtStatusSerializer(serializers.ModelSerializer):
    """ Serializer simplificado para consulta pública (GET /api/v1/public/status/<patente>). """
    estado = EstadoSerializer(read_only=True)
    patente_vehiculo = serializers.CharField(source='vehiculo.patente', read_only=True)

    class Meta:
        model = Ot
        fields = [
            'id', 'patente_vehiculo', 'descripcion', 'estado',
            'fecha_apertura', 'actualizado_en'
        ]
        read_only_fields = fields

# ===============================
# --- SERIALIZERS PARA TAREA ---
# ===============================

class TareaCreateSerializer(serializers.ModelSerializer):
    """ Serializer para CREAR una nueva Tarea (POST /api/v1/ot/<ot_id>/tareas). """
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        required=True,
        allow_null=False
    )
    estado = serializers.PrimaryKeyRelatedField(
        queryset=Estado.objects.filter(tipo='tarea', code='NUEVA'),
        default=lambda: Estado.objects.get(tipo='tarea', code='NUEVA')
    )

    class Meta:
        model = Tarea
        fields = ['nombre', 'responsable', 'estado']

    # EL MÉTODO "def create" DEBE SER ELIMINADO COMPLETAMENTE.

    

class TareaSerializer(serializers.ModelSerializer):
    """ Serializer para LEER Tareas (GET /api/v1/ot/<ot_id>/tareas). """
    estado = EstadoSerializer(read_only=True)
    responsable = UsuarioSerializer(read_only=True)
    
    # Sigue la relación (task.ot.vehiculo) y usa el serializer de Vehiculo
    vehiculo = VehiculoSerializer(read_only=True, source='ot.vehiculo')
    
    # Contadores existentes
    evidencias_count = serializers.SerializerMethodField()
    repuestos_count = serializers.SerializerMethodField()

    # 🌟 1. NUEVO CAMPO: Motivo de Pausa
    motivo_pausa_actual = serializers.SerializerMethodField()

    class Meta:
        model = Tarea
        fields = [
            'id', 'ot_id', 'nombre', 'estado', 'inicio', 'fin',
            'responsable', 'creado_en', 'actualizado_en',
            'vehiculo',
            'evidencias_count', 'repuestos_count',
            'motivo_pausa_actual', # <-- 🌟 2. AGREGAR A LA LISTA DE CAMPOS
        ]
        read_only_fields = fields

    def get_evidencias_count(self, obj):
        """ Devuelve la cantidad de evidencias asociadas a esta tarea. """
        return obj.evidencias.count()

    def get_repuestos_count(self, obj):
        """ Devuelve la cantidad de repuestos usados en esta tarea. """
        return obj.repuestos_usados.count()

    # 🌟 3. NUEVA LÓGICA: Obtener el motivo
    def get_motivo_pausa_actual(self, obj):
        """
        Si la tarea está PAUSADA, busca la última pausa activa (sin fecha de fin) y devuelve el motivo.
        """
        if obj.estado and obj.estado.code == 'PAUSADA':
            # 'pausas' es el related_name definido en tu modelo Pausa
            pausa_activa = obj.pausas.filter(fin__isnull=True).order_by('-inicio').first()
            if pausa_activa:
                return pausa_activa.motivo
        return None

class TareaPausarSerializer(serializers.Serializer):
    """
    Serializer para recibir el motivo al pausar una Tarea (RF-TAR-03).
    Espera un JSON como: { "motivo": "Falta repuesto X" }
    """
    motivo = serializers.CharField(
        required=True,
        allow_blank=False, # No permitir motivo vacío
        max_length=200, # Límite razonable
        help_text="Motivo obligatorio por el cual se pausa la tarea."
    )

class TareaUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para ACTUALIZAR (PUT/PATCH) una Tarea (RF-TAR-07).
    Permite modificar 'nombre' y reasignar 'responsable'.
    """
    responsable = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(), # Busca en todos los perfiles de apt.usuario
        required=False, # Hacemos opcional para PATCH
        allow_null=True # Podríamos permitir desasignar (poner null) si la BD lo permite
    )

    class Meta:
        model = Tarea
        fields = ['nombre', 'responsable']
        extra_kwargs = {
            'nombre': {'required': False},
            'responsable': {'required': False},
        }

    def validate_responsable(self, value):
        # Opcional: Validar rol del responsable
        # if value and value.rol not in ['MECANICO', 'SUPERVISOR']:
        #     raise serializers.ValidationError("El responsable debe tener rol Mecánico o Supervisor.")
        return value

    def update(self, instance, validated_data):
        if 'responsable' in validated_data:
            responsable_instance = validated_data.pop('responsable')
            validated_data['responsable_id'] = responsable_instance.id if responsable_instance else None
        validated_data['actualizado_en'] = timezone.now()
        return super().update(instance, validated_data)

# ===================================
# --- SERIALIZERS PARA EVIDENCIA ---
# ===================================

class EvidenciaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Evidencia.
    Se usa para leer datos (GET) y añade la URL de descarga (RF-EV-03).
    """
    subido_por = UsuarioSerializer(read_only=True)
    tarea = serializers.PrimaryKeyRelatedField(read_only=True)
    url_descarga = serializers.SerializerMethodField()

    class Meta:
        model = Evidencia
        fields = [
            'id', 'tarea', 'path', 'mime_type', 'tamano_bytes',
            'subido_por', 'fecha_subida', 'url_descarga', # Incluimos el nuevo campo
        ]
        read_only_fields = fields

    def get_url_descarga(self, obj):
        supabase_url = os.environ.get("SUPABASE_URL")
        bucket_name = "apt-evidencias" # El nombre de tu bucket

        if supabase_url and obj.path:
            # Construcción de la URL de acceso público:
            # Forma: [SUPABASE_URL]/storage/v1/object/public/[BUCKET_NAME]/[PATH]
            return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{obj.path}"
        return None

# =================================
# --- SERIALIZERS PARA REPORTES ---
# =================================

class ReporteHorasHombreSerializer(serializers.Serializer):
    """
    Serializer para el resultado del reporte de Horas-Hombre.
    Espera datos de un .values() agrupado.
    """
    responsable_id = serializers.IntegerField(source='responsable')
    responsable_nombre = serializers.CharField(source='responsable__nombre')
    responsable_rol = serializers.CharField(source='responsable__rol')
    segundos_totales_trabajados = serializers.SerializerMethodField()
    tareas_completadas = serializers.IntegerField(source='conteo_tareas')

    def get_segundos_totales_trabajados(self, obj):
        duracion = obj.get('duracion_total_efectiva')
        if duracion:
            return round(duracion.total_seconds())
        return 0


# 1. CREA ESTE SERIALIZER NUEVO (Justo antes de TableroOtSerializer)
class VehiculoTableroSerializer(serializers.ModelSerializer):
    """ 
    Serializer ultra-ligero para el tablero. 
    ALERTA: No incluye 'chofer' ni 'historial' para evitar consultas lentas.
    """
    class Meta:
        model = Vehiculo
        fields = ['id', 'patente', 'marca', 'modelo']

# 2. MODIFICA ESTE SERIALIZER (Para que use el ligero)
# --- 2. MODIFICAR TABLEROOTSERIALIZER PARA USAR EL LIGERO ---
class TableroOtSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para las OTs que se mostrarán en el tablero Kanban.
    """
    # AQUÍ ESTÁ LA CLAVE: Usamos el serializer ligero
    vehiculo = VehiculoTableroSerializer(read_only=True) 
    
    estado = EstadoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)

    class Meta:
        model = Ot
        fields = [
            'id', 'vehiculo', 'estado', 'descripcion',
            'fecha_apertura', 'actualizado_en', 'creado_por',
        ]
        read_only_fields = fields

class BitacoraConTotalesSerializer(serializers.Serializer):
    """
    Serializer para la respuesta GET de la bitácora, incluyendo
    la lista de registros y los totales calculados.
    """
    totales = serializers.SerializerMethodField()
    registros = BitacoraSerializer(many=True, read_only=True, source='*')

    def get_totales(self, obj):
        # Los totales se pasarán en el 'context' desde la vista.
        return self.context.get('totales', {})

class ReporteDuracionEtapaSerializer(serializers.Serializer):
    """
    Serializer para el resultado del reporte de Duración por Etapa/Pausa.
    Muestra duraciones promedio en segundos.
    """
    estado_code = serializers.CharField()
    estado_label = serializers.CharField()
    duracion_promedio_segundos = serializers.SerializerMethodField()
    cantidad_tareas_consideradas = serializers.IntegerField()

    def get_duracion_promedio_segundos(self, obj):
        duracion_avg = obj.get('duracion_promedio')
        if isinstance(duracion_avg, timedelta):
            return round(duracion_avg.total_seconds())
        return 0

# --- SERIALIZERS PARA ADMINISTRACIÓN DE USUARIOS ---


class AdminUsuarioSerializer(serializers.ModelSerializer):
    """ Serializer para LEER perfiles de Usuario (apt.usuario) en Admin. """
    class Meta:
        model = Usuario
        # Campo añadido: numero_telefonico
        fields = ["id", "nombre", "email", "rut", "numero_telefonico", "rol", "external_id", "creado_en"] 
        read_only_fields = fields 

class AdminUsuarioCreateSerializer(serializers.Serializer):
    """ Serializer para CREAR (invitar) un nuevo Usuario vía Admin. """
    email = serializers.EmailField(required=True)
    nombre = serializers.CharField(required=True, max_length=100)
    rut = serializers.CharField(required=False, allow_blank=True, max_length=12) 
    numero_telefonico = serializers.CharField(required=False, allow_blank=True, max_length=20) # <-- NUEVO CAMPO
    rol = serializers.CharField(required=True, max_length=50)

    def validate_rut(self, value): 
        if not value:
            return None
        
        # Limpia el RUT de puntos y guiones, lo pasa a mayúsculas
        rut_clean = re.sub(r'[^0-9kK]', '', value).upper()
        
        # Validación básica del formato (ej: 7 u 8 dígitos + dígito verificador)
        if not re.match(r'^\d{7,8}[0-9K]$', rut_clean):
            raise serializers.ValidationError("Formato de RUT inválido. Debe contener 7 u 8 dígitos y el dígito verificador (ej: 12345678-K).")
            
        # Devuelve el formato estandarizado (ej: "12345678-K")
        return f"{rut_clean[:-1]}-{rut_clean[-1]}"

    def validate_numero_telefonico(self, value): # <-- LÓGICA DE VALIDACIÓN DEL TELÉFONO
        if not value:
            return None
        # Limpia el número de paréntesis, espacios, y guiones
        phone_clean = re.sub(r'[\s()-]', '', value)
        
        # Validación básica: debe ser numérico y tener entre 8 y 15 dígitos
        if not re.match(r'^\+?\d{8,15}$', phone_clean):
            raise serializers.ValidationError("Formato de número inválido. Debe contener solo números, opcionalmente el '+' inicial, y tener entre 8 y 15 dígitos.")
        
        # Guarda el número limpio
        return phone_clean 
    
    def validate_rol(self, value):
        roles_permitidos = ['MECANICO', 'SUPERVISOR', 'PORTERIA', 'ADMIN', 'ANALISTA', 'CHOFER', 'GUARDIA']
        if value.upper() not in roles_permitidos:
            raise serializers.ValidationError(f"Rol inválido. Roles permitidos: {', '.join(roles_permitidos)}")
        return value.upper() 

class AdminUsuarioUpdateSerializer(serializers.ModelSerializer):
    """ Serializer para ACTUALIZAR (PUT/PATCH) un perfil de Usuario vía Admin. """
    nombre = serializers.CharField(required=False, max_length=100)
    email = serializers.EmailField(required=False)
    rut = serializers.CharField(required=False, allow_blank=True, max_length=12) 
    numero_telefonico = serializers.CharField(required=False, allow_blank=True, max_length=20) # <-- NUEVO CAMPO
    rol = serializers.CharField(required=False, max_length=50)

    class Meta:
        model = Usuario
        # Campos de edición: añadimos numero_telefonico
        fields = ["nombre", "email", "rut", "numero_telefonico", "rol"] 

    def validate_rut(self, value): 
        if not value:
            return None
        
        rut_clean = re.sub(r'[^0-9kK]', '', value).upper()
        
        if not re.match(r'^\d{7,8}[0-9K]$', rut_clean):
            raise serializers.ValidationError("Formato de RUT inválido. Debe contener 7 u 8 dígitos y el dígito verificador (ej: 12345678-K).")
            
        return f"{rut_clean[:-1]}-{rut_clean[-1]}"

    def validate_numero_telefonico(self, value): # <-- LÓGICA DE VALIDACIÓN DEL TELÉFONO
        if not value:
            return None
        phone_clean = re.sub(r'[\s()-]', '', value)
        
        if not re.match(r'^\+?\d{8,15}$', phone_clean):
            raise serializers.ValidationError("Formato de número inválido. Debe contener solo números, opcionalmente el '+' inicial, y tener entre 8 y 15 dígitos.")
        
        return phone_clean
        
    def validate_rol(self, value):
        roles_permitidos = ['MECANICO', 'SUPERVISOR', 'PORTERIA', 'ADMIN', 'ANALISTA', 'CHOFER', 'GUARDIA']
        if value.upper() not in roles_permitidos:
            raise serializers.ValidationError(f"Rol inválido. Roles permitidos: {', '.join(roles_permitidos)}")
        return value.upper()

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


# =================================
# --- SERIALIZERS PARA AUDITORÍA ---
# =================================

class AuditLogSerializer(serializers.ModelSerializer):
    """ Serializer de solo lectura para los registros de auditoría. """
    usuario = UsuarioSerializer(read_only=True) # Muestra quién hizo la acción

    class Meta:
        model = AuditLog
        fields = [
            'id', 'usuario', 'action_type', 'entity_type', 'entity_id',
            'details', 'creado_en'
        ]
        read_only_fields = fields

# capstone-backend/api/serializers.py

# ... (después de los serializers de TareaUpdateSerializer)

# ==================================
# --- SERIALIZERS PARA REPUESTO ---
# ==================================

class RepuestoSerializer(serializers.ModelSerializer):
    """ Serializer de solo lectura para el catálogo de Repuestos. """
    class Meta:
        model = Repuesto
        fields = ["id", "codigo", "descripcion", "unidad_medida", "activo"]
        read_only_fields = fields

# =========================================
# --- SERIALIZERS PARA TAREA_REPUESTO ---
# =========================================

class TareaRepuestoSerializer(serializers.ModelSerializer):
    """ Serializer de lectura/lista para Repuestos usados en una Tarea. """
    # Incluimos el serializer del repuesto para ver su descripción
    repuesto = RepuestoSerializer(read_only=True)
    
    class Meta:
        model = TareaRepuesto
        fields = ["id", "tarea_id", "repuesto", "cantidad", "observacion", "creado_en"]
        read_only_fields = fields

class TareaRepuestoCreateSerializer(serializers.ModelSerializer):
    """ Serializer de escritura para añadir un Repuesto a una Tarea. """
    # Usamos PrimaryKeyRelatedField para que el usuario envíe solo el ID del repuesto
    repuesto = serializers.PrimaryKeyRelatedField(
        queryset=Repuesto.objects.filter(activo=True),
        # CORRECCIÓN: Se elimina 'source='repuesto''
        write_only=True    # No se muestra al leer
    )
    # Este campo aún es útil para mostrar el ID del repuesto en la respuesta POST
    repuesto_id = serializers.IntegerField(source='repuesto.id', read_only=True) 

    class Meta:
        model = TareaRepuesto
        # Excluimos 'tarea' porque se inyectará desde la vista
        fields = ["repuesto", "repuesto_id", "cantidad", "observacion"]
        
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value
    
    # La validación de unicidad (repuesto por tarea) se maneja en el perform_create de la vista
    # ya que necesitamos el contexto del `tarea_id` y del `repuesto`.

    # EN api/serializers.py (AÑADIR AL FINAL)

# Reutilizamos TareaSerializer, pero si solo queremos la lista de IDs,
# podríamos usar PrimaryKeyRelatedField o un SerializerMethodField.
# Usaremos TareaSerializer para obtener todo el detalle.

class TareaExportSerializer(serializers.ModelSerializer):
    """
    Serializer completo para Tarea, incluyendo su evidencia, repuestos y pausas.
    """
    # --- 1. AÑADE ESTA LÍNEA (para incluir el objeto "estado") ---
    estado = EstadoSerializer(read_only=True) 
    responsable = UsuarioSerializer(read_only=True)
    evidencias = EvidenciaSerializer(many=True, read_only=True) 
    repuestos_usados = TareaRepuestoSerializer(many=True, read_only=True) # Incluye cantidad y detalle del repuesto
    # Las pausas se pueden incluir con un SerializerMethodField si se requiere detalle,
    # o simplemente con una lista de PausaSerializer



    class Meta:
        model = Tarea
        fields = [
            'id', 'nombre', 'estado', 'inicio', 'fin', 
            'responsable', 'evidencias', 'repuestos_usados'
        ]

class OtExportSerializer(serializers.ModelSerializer):
    """
    Serializer Raíz para la exportación de una OT completa.
    Anida todas las relaciones One-to-Many.
    """
    # --- 2. AÑADE ESTA LÍNEA (para incluir el objeto "estado") ---
    estado = EstadoSerializer(read_only=True) 
    vehiculo = VehiculoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)
    # ✅ CLAVE: Anidar la lista de tareas
    tareas = TareaExportSerializer(many=True, read_only=True) 


    class Meta:
        model = Ot
        fields = [
            'id', 'descripcion', 'estado', 'fecha_apertura', 
            'fecha_cierre', 'actualizado_en',
            'vehiculo', 'creado_por',
            'tareas' # <--- ESTA ES LA LISTA DE TAREAS ANIDADAS
        ]


# capstone-backend/api/serializers.py

# ... (todos tus serializers anteriores, como UsuarioSerializer, VehiculoSerializer, EstadoSerializer, etc.) ...


# --- 1. AÑADE ESTA NUEVA CLASE (ANTES DE OtDetailSerializer) ---
# (La insertas alrededor de la línea 141 de tu archivo)

class TareaSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para Tareas, usado en la vista pública de estado.
    Utiliza el EstadoSerializer existente.
    """
    # Usamos el EstadoSerializer que SÍ existe en tu archivo
    estado = EstadoSerializer(read_only=True) 
    
    class Meta:
        model = Tarea
        fields = ['id', 'nombre', 'estado']


# --- Tarea Simple (Necesaria para la lista anidada) ---
class TareaSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simple para Tareas.
    """
    # Usamos el EstadoSerializer que SÍ existe en su archivo
    estado = EstadoSerializer(read_only=True) 
    
    class Meta:
        model = Tarea
        fields = ['id', 'nombre', 'estado']


# --- Ot Detail (Corregido) ---
# (Este es el que se usa en /api/v1/ot/<id>/)
class OtDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado para una OT, usado en la vista de detalle.
    """
    vehiculo = VehiculoSerializer(read_only=True)
    creado_por = UsuarioSerializer(read_only=True)
    estado = EstadoSerializer(read_only=True)
    tareas_count = serializers.SerializerMethodField()
    horas_pausa = serializers.SerializerMethodField()
    
    # 🌟 Incluye la lista de tareas
    tareas = TareaSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Ot
        fields = [
            'id', 'vehiculo', 'estado', 'descripcion',  # <-- 'codigo_ot' ELIMINADO
            'creado_por', 'fecha_apertura', 'fecha_cierre', 'tareas_count', 
            'horas_pausa',
            'tareas'
        ]
        read_only_fields = [
            'id', 'vehiculo', 'estado', 'creado_por',  # <-- 'codigo_ot' ELIMINADO
            'fecha_apertura', 'fecha_cierre', 'tareas_count', 'horas_pausa',
            'tareas'
        ]

    def get_tareas_count(self, obj):
        return obj.tareas.count()
    
    def get_horas_pausa(self, obj):
        total_pausa_segundos = 0
        pausas = Pausa.objects.filter(tarea__ot=obj, fin__isnull=False)
        for pausa in pausas:
            duracion = pausa.fin - pausa.inicio
            total_pausa_segundos += duracion.total_seconds()
        
        total_minutos = total_pausa_segundos / 60
        return round(total_minutos, 2)

# --- PublicOtStatusSerializer (Corregido y ahora incluye tareas para el frontend) ---
# (Este es el que se usa en /api/v1/public/status/<patente>/)
class PublicOtStatusSerializer(serializers.ModelSerializer):
    """ Serializer simplificado para consulta pública. """
    estado = EstadoSerializer(read_only=True)
    # 🌟 Arreglo de anidamiento de vehículo
    vehiculo = VehiculoSerializer(read_only=True)
    # 🌟 Lista de tareas para el frontend
    tareas = TareaSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Ot
        fields = [
            'id', 
            'vehiculo',       
            'descripcion', 
            'estado',
            'fecha_apertura',
            'fecha_cierre',   
            'actualizado_en',
            'tareas'          
        ]
        read_only_fields = fields


class AdminUsuarioSerializer(serializers.ModelSerializer):
    """ Serializer para LEER perfiles de usuario en Admin. """
    # Nuevo campo calculado
    vehiculo_actual = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        # Agregamos 'vehiculo_actual' a la lista de campos
        fields = ["id", "nombre", "email", "rut", "numero_telefonico", "rol", "external_id", "creado_en", "vehiculo_actual"] 
        read_only_fields = fields 

    def get_vehiculo_actual(self, obj):
        # Busca si el usuario tiene vehículos asignados (relación inversa definida en models.py)
        vehiculo = obj.vehiculos_asignados.first() 
        if vehiculo:
            return {"id": vehiculo.id, "patente": vehiculo.patente}
        return None
    
from rest_framework import serializers
from .models import Ot

# En api/serializers.py

from rest_framework import serializers
from .models import Ot

class OtEstadoChoferSerializer(serializers.ModelSerializer):
    """ Serializer simplificado para la vista del Chofer (GET /api/v1/mi-estado). """
    estado = EstadoSerializer(read_only=True)
    # 🌟 AGREGAMOS ESTO: Para poder dibujar la línea de tiempo
    tareas = TareaSimpleSerializer(many=True, read_only=True)
    vehiculo = VehiculoSerializer(read_only=True) # Opcional: para mostrar patente y marca

    class Meta:
        model = Ot
        fields = ["id", "vehiculo", "descripcion", "estado", "fecha_apertura", "actualizado_en", "tareas"]
        read_only_fields = fields

