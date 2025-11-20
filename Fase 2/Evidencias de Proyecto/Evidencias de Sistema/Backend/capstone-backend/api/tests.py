import uuid
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Vehiculo, Usuario, Estado, Ot, Tarea, Evidencia 
from django.utils import timezone 
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile # <--- NUEVO IMPORT

class VehiculoIntegrationTests(APITestCase):
    
    def setUp(self):
        """Configuración inicial: Crea todos los objetos base necesarios para las pruebas."""
        User = get_user_model()
        
        # 1. USUARIOS Y PERFILES
        self.supabase_uid_admin = str(uuid.uuid4()) 
        self.supabase_uid_mecanico = str(uuid.uuid4())

        self.user_admin = User.objects.create_user(
            username=self.supabase_uid_admin,
            email="admin@pepsico.com", 
            password="password123"
        )
        self.perfil_admin = Usuario.objects.create(
            external_id=self.supabase_uid_admin,
            nombre="Administrador Test",
            email="admin@pepsico.com",
            rol="ADMIN",
            creado_en=timezone.now()
        )
        
        self.user_mecanico = User.objects.create_user(
            username=self.supabase_uid_mecanico,
            email="mecanico@pepsico.com", 
            password="password123"
        )
        self.perfil_mecanico = Usuario.objects.create(
            external_id=self.supabase_uid_mecanico,
            nombre="Mecánico Test",
            email="mecanico@pepsico.com",
            rol="MECANICO",
            creado_en=timezone.now()
        )

        # 2. Vehículo base
        self.vehiculo = Vehiculo.objects.create(
            patente="TEST99",
            marca="Toyota",
            modelo="Hilux",
            creado_en=timezone.now()
        )

        # 3. ESTADOS REQUERIDOS
        self.estado_nueva_ot = Estado.objects.create(tipo='ot', code='NUEVA', label='Nueva OT', orden=1, creado_en=timezone.now())
        self.estado_activa_ot = Estado.objects.create(tipo='ot', code='ACTIVA', label='OT Activa', orden=2, creado_en=timezone.now())
        
        self.estado_nueva_tarea = Estado.objects.create(tipo='tarea', code='NUEVA', label='Nueva Tarea', orden=0, creado_en=timezone.now())
        self.estado_en_proceso = Estado.objects.create(tipo='tarea', code='EN_PROCESO', label='En Proceso', orden=3, creado_en=timezone.now())
        self.estado_pausada = Estado.objects.create(tipo='tarea', code='PAUSADA', label='Pausada', orden=5, creado_en=timezone.now())
        self.estado_cerrada = Estado.objects.create(tipo='tarea', code='CERRADA', label='Cerrada', orden=10, creado_en=timezone.now())
        self.estado_hecha = Estado.objects.create(tipo='tarea', code='HECHA', label='Tarea Hecha (Final)', orden=9, creado_en=timezone.now())

        # 4. Autenticación (Por defecto, usamos el ADMIN)
        self.client.force_authenticate(user=self.user_admin)

    # ==========================================================
    # TESTS DE VEHÍCULOS Y CREACIÓN DE OT
    # ==========================================================

    def test_listar_vehiculos(self):
        """Prueba que la API devuelve la lista de vehículos (GET /vehiculos/)"""
        url = '/api/v1/vehiculos/' 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        print("\n✅ [TEST] Listar Vehículos: PASÓ")

    def test_modificar_vehiculo(self):
        """Prueba editar la marca de un vehículo existente (PATCH /vehiculos/ID/editar/)"""
        url = f'/api/v1/vehiculos/{self.vehiculo.id}/editar/' 
        nuevos_datos = {"marca": "Nissan"} 
        response = self.client.patch(url, nuevos_datos, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vehiculo.refresh_from_db()
        self.assertEqual(self.vehiculo.marca, "Nissan")
        print("\n✅ [TEST] Modificar Vehículo: PASÓ")

    def test_validacion_regex_patente(self):
        """Prueba que el sistema rechaza patentes inválidas (POST /vehiculos/crear/)"""
        url = '/api/v1/vehiculos/crear/'
        datos_malos = {"patente": "ESTO_NO_ES_UNA_PATENTE", "marca": "Ford", "modelo": "Ranger"}
        response = self.client.post(url, datos_malos, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print("\n✅ [TEST] Validación Regex: PASÓ")

    def test_crear_ot_para_vehiculo(self):
        """Prueba crear una Orden de Trabajo (POST /ot/)"""
        url = '/api/v1/ot/' 
        datos_ot = {
            "vehiculo": self.vehiculo.id,
            "estado_id": self.estado_nueva_ot.id,
            "descripcion": "Cambio de aceite y filtros"
        }
        response = self.client.post(url, datos_ot, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ot_creada = Ot.objects.first()
        self.assertEqual(ot_creada.vehiculo.patente, "TEST99")
        print("\n✅ [TEST] Crear OT: PASÓ")

    # ==========================================================
    # TESTS AVANZADOS (SEGURIDAD Y VALIDACIÓN FK)
    # ==========================================================
    
    def test_seguridad_acceso_admin_denegado(self):
        """
        Prueba 1: Asegura que un usuario MECANICO reciba 403 Forbidden 
        al intentar acceder a la ruta de administración.
        """
        url = '/api/v1/admin/usuarios/'
        
        self.client.force_authenticate(user=None)
        self.client.force_authenticate(user=self.user_mecanico)
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print("\n✅ [TEST] Seguridad (MECANICO): PASÓ (Acceso denegado con 403)")
        
        self.client.force_authenticate(user=self.user_admin)


    def test_validacion_vehiculo_inexistente_ot(self):
        """
        Prueba 2: Asegura que el Serializer devuelva 400 Bad Request 
        al intentar crear una OT con un ID de vehículo inexistente (9999).
        """
        url = '/api/v1/ot/'
        datos_malos = {
            "vehiculo": 9999, 
            "estado_id": self.estado_nueva_ot.id,
            "descripcion": "Intento de OT con ID falso"
        }
        
        response = self.client.post(url, datos_malos, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('vehiculo', str(response.content)) 
        print("\n✅ [TEST] Validación (FK): PASÓ (Rechazó ID de vehículo inexistente)")


    def test_flujo_completo_extendido(self):
        """
        Prueba 3: Ciclo de vida completo de la Tarea (Crear OT -> Tarea -> Iniciar -> Pausar -> Evidencia -> Cerrar).
        """
        
        # 1. CREAR OT
        datos_ot = {"vehiculo": self.vehiculo.id, "estado_id": self.estado_nueva_ot.id, "descripcion": "Flujo Extendido"}
        response_ot = self.client.post('/api/v1/ot/', datos_ot, format='json')
        ot_id = Ot.objects.get(vehiculo_id=self.vehiculo.id, descripcion="Flujo Extendido").id

        # 2. CREAR TAREA
        url_tarea_create = reverse("api_tarea_list", kwargs={'ot_id': ot_id})
        response_tarea = self.client.post(url_tarea_create, {
            "nombre": "Flujo Completo",
            "estado_id": self.estado_en_proceso.id, 
            "responsable": self.perfil_admin.id
        }, format='json')
        tarea_id = response_tarea.data['id']

        # 3. INICIAR TAREA
        self.client.post(f'/api/v1/tareas/{tarea_id}/iniciar/')
        
        # 4. PAUSAR TAREA
        self.client.post(f'/api/v1/tareas/{tarea_id}/pausar/', {"motivo": "Falta material"})
        
        # 5. CREAR EVIDENCIA 🔥 SOLUCIÓN FINAL: Añadir dummy file object para pasar validación multipart
        url_evidencia = f'/api/v1/tareas/{tarea_id}/evidencia/'
        
        # Creamos un archivo simulado
        dummy_file = SimpleUploadedFile("test_file.jpg", b"file_content", content_type="image/jpeg")
        
        response_evidencia = self.client.post(url_evidencia, {
            "tarea": tarea_id,
            "subido_por": self.perfil_admin.id,
            "path": f"tareas/{tarea_id}/foto_freno.jpg",
            "mime_type": "image/jpeg",
            "tamano_bytes": 102400,
            # Campo que el serializador necesita para la validación:
            "file": dummy_file, 
        }, format='multipart')
        
        self.assertEqual(response_evidencia.status_code, status.HTTP_201_CREATED)
        
        # 6. REANUDAR Y CERRAR
        self.client.post(f'/api/v1/tareas/{tarea_id}/reanudar/')
        response_cerrar = self.client.post(f'/api/v1/tareas/{tarea_id}/cerrar/')
        
        # 7. VERIFICACIÓN FINAL
        self.assertEqual(response_cerrar.status_code, status.HTTP_200_OK)
        tarea_final = Tarea.objects.get(id=tarea_id)
        self.assertEqual(tarea_final.estado.code, 'HECHA')
        self.assertEqual(Evidencia.objects.count(), 1)

        print("\n✅ [TEST] Flujo Extendido (Pausa/Evidencia): PASÓ")