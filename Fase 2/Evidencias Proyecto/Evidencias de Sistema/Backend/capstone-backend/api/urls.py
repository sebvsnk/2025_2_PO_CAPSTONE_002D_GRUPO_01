from django.contrib import admin
from django.urls import path
from api.views import Health, VehiculoList, BitacoraCreate

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/health", Health.as_view()),
    path("api/v1/vehiculos", VehiculoList.as_view()),   # GET lista, ?search=
    path("api/v1/bitacora", BitacoraCreate.as_view()),  # POST entrada/salida
]
