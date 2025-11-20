# api/models.py
from django.db import models
from django.utils import timezone
import sys  # <--- IMPORTANTE: Necesario para detectar modo Test

# --- Helper para determinar si estamos en modo Test ---
IS_TESTING = 'test' in sys.argv

# --- MODELO USUARIO (PERFIL) ---
class Usuario(models.Model):
    # Mapea apt.usuario
    id = models.BigAutoField(primary_key=True)
    nombre = models.TextField()
    email = models.TextField(null=True, blank=True, unique=True) # Agrega unique=Trueld(null=True, blank=True)
    rut = models.TextField(null=True, blank=True, unique=True) 
    numero_telefonico = models.TextField(null=True, blank=True)
    rol = models.TextField(default='MECANICO')
    external_id = models.UUIDField(null=True, blank=True) 
    creado_en = models.DateTimeField(default=timezone.now) 

    class Meta:
        verbose_name = "Usuario (Perfil)"
        verbose_name_plural = "Usuarios (Perfiles)"
        ordering = ['nombre'] 
        
        if IS_TESTING:
            managed = True
            db_table = 'usuario'
        else:
            managed = False
            db_table = '"apt"."usuario"'

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

# --- MODELO VEHICULO ---
class Vehiculo(models.Model):
    # Mapea apt.vehiculo
    patente = models.CharField(max_length=16, unique=True)
    marca = models.TextField(null=True, blank=True)
    modelo = models.TextField(null=True, blank=True)
    # Agregamos default para que SQLite no falle
    creado_en = models.DateTimeField(default=timezone.now)

    # Relaciona el vehículo con un usuario (el chofer)
    chofer = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        db_column="chofer_id",
        related_name="vehiculos_asignados",
        null=True, blank=True
    )

    class Meta:
        ordering = ['patente']
        if IS_TESTING:
            managed = True
            db_table = 'vehiculo'
        else:
            managed = False
            db_table = '"apt"."vehiculo"'

    def __str__(self):
        return self.patente

# --- MODELO BITACORA ---
class BitacoraPorteria(models.Model):
    # Mapea apt.bitacora_porteria
    TIPO_CHOICES = (("ENTRADA","ENTRADA"),("SALIDA","SALIDA"))
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.RESTRICT, db_column="vehiculo_id",
        related_name="movimientos",
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    # Agregamos default para que SQLite no falle
    fecha_hora = models.DateTimeField(default=timezone.now)
    usuario_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_hora']
        if IS_TESTING:
            managed = True
            db_table = 'bitacora_porteria'
            indexes = [models.Index(fields=["vehiculo", "-fecha_hora"])]
        else:
            managed = False
            db_table = '"apt"."bitacora_porteria"'
            indexes = [models.Index(fields=["vehiculo", "-fecha_hora"])]

    def __str__(self):
        patente = self.vehiculo.patente if self.vehiculo else "N/A"
        fecha_formateada = self.fecha_hora.astimezone(timezone.get_current_timezone()).strftime('%Y-%m-%d %H:%M') if self.fecha_hora else "N/A"
        return f"{self.tipo} - {patente} ({fecha_formateada})"

# --- MODELO ESTADO ---
class Estado(models.Model):
    # Mapea apt.estado
    id = models.BigAutoField(primary_key=True)
    tipo = models.TextField() 
    code = models.TextField() 
    label = models.TextField()
    descripcion = models.TextField(null=True, blank=True)
    orden = models.IntegerField(default=100)
    activo = models.BooleanField(default=True)
    # Agregamos default para que SQLite no falle
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['tipo', 'orden']
        unique_together = ('tipo', 'code')
        if IS_TESTING:
            managed = True
            db_table = 'estado'
        else:
            managed = False
            db_table = '"apt"."estado"'

    def __str__(self):
        activo_str = "" if self.activo else " (Inactivo)"
        return f"[{self.tipo.upper()}] {self.label}{activo_str}"

# --- MODELO OT (ORDEN DE TRABAJO) ---
class Ot(models.Model):
    # Mapea apt.ot
    id = models.BigAutoField(primary_key=True)

    # Relaciones (ForeignKey)
    vehiculo = models.ForeignKey(
        Vehiculo, on_delete=models.RESTRICT, db_column="vehiculo_id",
        related_name="ots"
    )
    estado = models.ForeignKey(
        Estado, on_delete=models.RESTRICT, db_column="estado_id",
        related_name="ots", null=True, blank=True
    )
    creado_por = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="creado_por",
        related_name="ots_creadas", null=True, blank=True
    )

    descripcion = models.TextField(null=True, blank=True)
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    # Agregamos default para que SQLite no falle
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Orden de Trabajo (OT)"
        verbose_name_plural = "Órdenes de Trabajo (OTs)"
        ordering = ['-fecha_apertura']
        if IS_TESTING:
            managed = True
            db_table = 'ot'
        else:
            managed = False
            db_table = '"apt"."ot"'

    def __str__(self):
        patente = self.vehiculo.patente if self.vehiculo else "N/A"
        return f"OT #{self.id} ({patente})"

# --- MODELO TAREA ---
class Tarea(models.Model):
    # Mapea la tabla apt.tarea
    id = models.BigAutoField(primary_key=True)

    ot = models.ForeignKey(
        Ot,
        on_delete=models.CASCADE,
        db_column="ot_id",
        related_name="tareas"
    )
    estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        db_column="estado_id",
        related_name="tareas",
        null=True, blank=True
    )
    responsable = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        db_column="responsable",
        related_name="tareas_asignadas",
        null=True, blank=True
    )

    nombre = models.TextField()
    inicio = models.DateTimeField(null=True, blank=True)
    fin = models.DateTimeField(null=True, blank=True)

    # Agregamos default para que SQLite no falle
    creado_en = models.DateTimeField(default=timezone.now)
    actualizado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['ot', 'creado_en']
        if IS_TESTING:
            managed = True
            db_table = 'tarea'
        else:
            managed = False
            db_table = '"apt"."tarea"'

    def __str__(self):
        estado_label = f" ({self.estado.label})" if self.estado else ""
        return f"Tarea #{self.id}: {self.nombre}{estado_label} (OT: {self.ot_id})"

# --- MODELO PAUSA ---
class Pausa(models.Model):
    # Mapea la tabla apt.pausa
    id = models.BigAutoField(primary_key=True)
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        db_column="tarea_id",
        related_name="pausas"
    )
    motivo = models.TextField()
    # Agregamos default para que SQLite no falle
    inicio = models.DateTimeField(default=timezone.now)
    fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Pausa de Tarea"
        verbose_name_plural = "Pausas de Tareas"
        ordering = ['tarea', '-inicio']
        if IS_TESTING:
            managed = True
            db_table = 'pausa'
        else:
            managed = False
            db_table = '"apt"."pausa"'

    def __str__(self):
        fin_str = f" - Fin: {self.fin.strftime('%H:%M')}" if self.fin else ""
        return f"Pausa Tarea {self.tarea_id}: {self.motivo} (Inicio: {self.inicio.strftime('%H:%M')}{fin_str})"

# --- MODELO EVIDENCIA ---
class Evidencia(models.Model):
    # Mapea la tabla apt.evidencia
    id = models.BigAutoField(primary_key=True)

    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        db_column="tarea_id",
        related_name="evidencias"
    )
    subido_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        db_column="subido_por",
        related_name="evidencias_subidas",
        null=True, blank=True
    )

    path = models.TextField(unique=True)
    mime_type = models.CharField(max_length=255, null=True, blank=True)
    tamano_bytes = models.BigIntegerField(null=True, blank=True)
    
    fecha_subida = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Evidencia"
        verbose_name_plural = "Evidencias"
        ordering = ['tarea', '-fecha_subida']
        if IS_TESTING:
            managed = True
            db_table = 'evidencia'
        else:
            managed = False
            db_table = '"apt"."evidencia"'

    def __str__(self):
        nombre_archivo = self.path.split('/')[-1] if self.path else "N/A"
        return f"Evidencia Tarea {self.tarea_id}: {nombre_archivo}"

# --- MODELO AUDIT LOG ---
class AuditLog(models.Model):
    # Mapea apt.audit_log
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, db_column="usuario_id",
        related_name="logs_generados", null=True, blank=True
    )
    action_type = models.TextField()
    entity_type = models.TextField()
    entity_id = models.BigIntegerField(null=True, blank=True)
    details = models.JSONField(null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-creado_en']
        if IS_TESTING:
            managed = True
            db_table = 'audit_log'
        else:
            managed = False
            db_table = '"apt"."audit_log"'

    def __str__(self):
        return f"[{self.creado_en.strftime('%Y-%m-%d %H:%M')}] {self.action_type} on {self.entity_type} #{self.entity_id}"

# --- MODELO REPUESTO (CATÁLOGO) ---
class Repuesto(models.Model):
    # Mapea apt.repuesto
    id = models.BigAutoField(primary_key=True)
    codigo = models.TextField(unique=True, null=True, blank=True)
    descripcion = models.TextField()
    unidad_medida = models.TextField(default='unidad')
    activo = models.BooleanField(default=True)
    # Agregamos default para que SQLite no falle
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Repuesto"
        verbose_name_plural = "Repuestos"
        ordering = ['descripcion']
        if IS_TESTING:
            managed = True
            db_table = 'repuesto'
        else:
            managed = False
            db_table = '"apt"."repuesto"'

    def __str__(self):
        return f"[{self.codigo}] {self.descripcion}"

# --- MODELO TAREA_REPUESTO (ASIGNACIÓN) ---
class TareaRepuesto(models.Model):
    # Mapea apt.tarea_repuesto
    id = models.BigAutoField(primary_key=True)
    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE, 
        db_column="tarea_id",
        related_name="repuestos_usados"
    )
    repuesto = models.ForeignKey(
        Repuesto,
        on_delete=models.RESTRICT,
        db_column="repuesto_id",
        related_name="usos_en_tareas"
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    observacion = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Repuesto Usado en Tarea"
        verbose_name_plural = "Repuestos Usados en Tareas"
        unique_together = ('tarea', 'repuesto') 
        ordering = ['tarea', 'creado_en']
        if IS_TESTING:
            managed = True
            db_table = 'tarea_repuesto'
        else:
            managed = False
            db_table = '"apt"."tarea_repuesto"'

    def __str__(self):
        return f"{self.cantidad} x {self.repuesto.codigo} en Tarea #{self.tarea_id}"

# --- MODELO HISTORIAL DE PATENTES ---
class VehiculoPatenteHist(models.Model):
    # Mapea apt.vehiculo_patente_hist
    id = models.BigAutoField(primary_key=True)
    
    vehiculo = models.ForeignKey(
        Vehiculo, 
        on_delete=models.CASCADE, 
        db_column="vehiculo_id",
        related_name="historial_patentes"
    )
    patente = models.TextField()
    desde = models.DateTimeField(default=timezone.now) 
    hasta = models.DateTimeField(null=True, blank=True) 

    class Meta:
        verbose_name = "Historial de Patente"
        verbose_name_plural = "Historial de Patentes"
        ordering = ['-desde']
        if IS_TESTING:
            managed = True
            db_table = 'vehiculo_patente_hist'
        else:
            managed = False
            db_table = '"apt"."vehiculo_patente_hist"'

    def __str__(self):
        return f"{self.patente} ({self.vehiculo.id})"