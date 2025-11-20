import os 
from diagrams import Diagram, Cluster, Node
from diagrams.onprem.client import Client as BrowserClient
from diagrams.programming.framework import Django
from diagrams.onprem.database import Postgresql
from diagrams.onprem.network import Internet

# =================================================================
# CORRECCIÓN CLAVE: Agrega la carpeta 'bin' al PATH del entorno Python.
# Si tu instalación es 'C:\Program Files (x86)\Graphviz', la carpeta 'bin'
# que contiene 'dot.exe' estará dentro de ese directorio.
# =================================================================
# La ruta correcta para Windows suele ser 'C:\Program Files (x86)\Graphviz\bin'
# Usamos r'' para manejar las barras invertidas correctamente.
os.environ["PATH"] += os.pathsep + r'C:\Program Files (x86)\Graphviz\bin' 


# --- Definición de la Arquitectura ---
# Aquí comienza el diagrama
with Diagram("Arquitectura APT PepsiCo - Django/Vue/Supabase", show=False, direction="LR"):
    
    # 1. Capa de Cliente/Frontend
    frontend = BrowserClient("Frontend (Vue.js)")

    # 2. Capa de Backend (Tu Proyecto Django)
    with Cluster("Backend API (capstone-backend)"):
        # Nodo principal de la API
        django_api = Django("Django REST Framework\n(Lógica, Serializers, RBAC)")

    # 3. Capa de Servicios Externos (Supabase BaaS)
    with Cluster("Servicios de Supabase (BaaS)"):
        # Usamos nodos simples con estilo para representar los servicios Supabase
        auth_service = Node("Supabase Auth\n(Tokens JWT)", style="bold", shape="box")
        db_service = Postgresql("PostgreSQL DB")
        storage_service = Node("Supabase Storage\n(Evidencia)", style="bold", shape="box")

    # --- Definición de los Flujos (Líneas de Conexión) ---

    # 1. Flujo de Autenticación (RF-SEC-01)
    frontend >> Internet("Login/Token Request") >> auth_service
    auth_service >> frontend

    # 2. Flujo de Datos API (OTs, Tareas)
    frontend >> Internet("API Request") >> django_api
    django_api >> db_service

    # 3. Flujo de Archivos/Evidencia (RF-EV-01)
    django_api >> storage_service
    storage_service >> db_service