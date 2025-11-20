from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView

from api.views import (
    home, login_page,
    Health,
    VehiculoList, VehiculoCreate, VehiculoDetail, VehiculoUpdateView,
    BitacoraListCreate,
    OtListCreateView, OtDetailUpdateView, OtCambiarEstadoView, 
    OtExportDetailView, OtListExportView, OtHistorialListView,
    TareaListCreateView, TareaDetailUpdateView, 
    TareaIniciarView, TareaPausarView, TareaReanudarView, TareaCerrarView, TareaAnularView,
    MisTareasListView,
    EvidenciaCreateView, TareaRepuestoListCreateView, RepuestoListView,
    TableroView, SalidasReport, ReporteDuracionEtapaView, HorasHombreReport,
    AuditLogListAPIView,
    MiPerfilView, AdminUsuarioListCreateView, AdminUsuarioDetailUpdateView, 
    ChoferContactoCreateView,
    MiVehiculoEstadoView, PublicVehicleStatusView
)

urlpatterns = [
    # --- RUTAS HTML ---
    path("", home, name="home"),           
    path("login/", login_page, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    
    # --- ADMIN ---
    path("admin/", admin.site.urls),

    # --- API ENDPOINTS ---
    
    # Salud
    path("api/v1/health/", Health.as_view(), name="api_health"),

    # Vehículos y Choferes
    path("api/v1/usuarios/contacto-chofer/", ChoferContactoCreateView.as_view(), name="api_chofer_create"),
    path("api/v1/vehiculos/", VehiculoList.as_view(), name="api_vehiculo_list"),
    path("api/v1/vehiculos/crear/", VehiculoCreate.as_view(), name="api_vehiculo_create"),
    path("api/v1/vehiculos/<int:vehiculo_id>/", VehiculoDetail.as_view(), name="api_vehiculo_detail"),
    path("api/v1/vehiculos/<int:vehiculo_id>/editar/", VehiculoUpdateView.as_view(), name="api_vehiculo_update"),

    # Bitácora
    path("api/v1/bitacora/", BitacoraListCreate.as_view(), name="api_bitacora_list"),

    # OTs
    path("api/v1/ot/", OtListCreateView.as_view(), name="api_ot_list"),
    path("api/v1/ot/<int:ot_id>/", OtDetailUpdateView.as_view(), name="api_ot_detail"),
    path("api/v1/ot/<int:ot_id>/cambiar_estado/", OtCambiarEstadoView.as_view(), name="api_ot_cambiar_estado"),
    path("api/v1/ot/<int:ot_id>/exportar/", OtExportDetailView.as_view(), name="api_ot_export"),
    path("api/v1/ot/exportar-lista/", OtListExportView.as_view(), name="api_ot_export_list"),
    path("api/v1/ot/historial/", OtHistorialListView.as_view(), name="api_ot_historial"),

    # Tareas
    path("api/v1/ot/<int:ot_id>/tareas/", TareaListCreateView.as_view(), name="api_tarea_list"),
    path("api/v1/tareas/<int:tarea_id>/", TareaDetailUpdateView.as_view(), name="api_tarea_detail"),
    path("api/v1/tareas/<int:tarea_id>/iniciar/", TareaIniciarView.as_view(), name="api_tarea_iniciar"),
    path("api/v1/tareas/<int:tarea_id>/pausar/", TareaPausarView.as_view(), name="api_tarea_pausar"),
    path("api/v1/tareas/<int:tarea_id>/reanudar/", TareaReanudarView.as_view(), name="api_tarea_reanudar"),
    path("api/v1/tareas/<int:tarea_id>/cerrar/", TareaCerrarView.as_view(), name="api_tarea_cerrar"),
    path("api/v1/tareas/<int:tarea_id>/anular/", TareaAnularView.as_view(), name="api_tarea_anular"),
    path("api/v1/mis-tareas/", MisTareasListView.as_view(), name="api_mis_tareas"),

    # --- CORRECCIÓN AQUÍ: "evidencia" en SINGULAR ---
    path("api/v1/tareas/<int:tarea_id>/evidencia/", EvidenciaCreateView.as_view(), name="api_evidencia_create"),
    
    # Repuestos (lo dejamos en plural si tu front lo pide así, o avísame)
    path("api/v1/tareas/<int:tarea_id>/repuestos/", TareaRepuestoListCreateView.as_view(), name="api_repuesto_tarea_create"),
    path("api/v1/repuestos/", RepuestoListView.as_view(), name="api_repuesto_list"),

    # Reportes y Tablero
    path("api/v1/tablero/", TableroView.as_view(), name="api_tablero"),
    path("api/v1/reportes/entradas-salidas/", SalidasReport.as_view(), name="api_reporte_salidas"),
    path("api/v1/reportes/duracion-etapas/", ReporteDuracionEtapaView.as_view(), name="api_reporte_duracion"),
    path("api/v1/reportes/horas-hombre/", HorasHombreReport.as_view(), name="api_reporte_hh"),
    path("api/v1/auditoria/", AuditLogListAPIView.as_view(), name="api_auditoria"),

    # Usuarios
    path("api/v1/mi-perfil/", MiPerfilView.as_view(), name="api_mi_perfil"),
    path("api/v1/admin/usuarios/", AdminUsuarioListCreateView.as_view(), name="api_admin_usuarios"),
    path("api/v1/admin/usuarios/<int:id>/", AdminUsuarioDetailUpdateView.as_view(), name="api_admin_usuario_detail"),

    # Públicas
    path("api/v1/mi-estado/", MiVehiculoEstadoView.as_view(), name="api_mi_estado"),
    path("api/v1/public/status/<str:patente>/", PublicVehicleStatusView.as_view(), name="api_public_status"),
]