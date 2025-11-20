from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Tiempo de espera entre acciones (simula a un humano pensando 1 a 5 seg)
    wait_time = between(1, 5)

    # El token que usaremos para todas las peticiones falsas
    # ¡PEGA TU TOKEN REAL AQUÍ ABAJO!
    token = 'eyJhbGciOiJIUzI1NiIsImtpZCI6ImQyNWgyc2ZBZmp3dEMxYjciLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2tyZ2FnemRudW12aWpsa3lkdnVnLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiJkNTg5OGE2OC04ZWVkLTQ0NGMtYTdhMy0zN2RjYWMxZGI2ZTkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzYzNDQzOTY2LCJpYXQiOjE3NjM0NDAzNjYsImVtYWlsIjoiYWQuc2FudGFtYXJ0YUBvdXRsb29rLmVzIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnsicHJvdmlkZXIiOiJlbWFpbCIsInByb3ZpZGVycyI6WyJlbWFpbCJdfSwidXNlcl9tZXRhZGF0YSI6eyJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0sInJvbGUiOiJhdXRoZW50aWNhdGVkIiwiYWFsIjoiYWFsMSIsImFtciI6W3sibWV0aG9kIjoicGFzc3dvcmQiLCJ0aW1lc3RhbXAiOjE3NjM0NDAzNjZ9XSwic2Vzc2lvbl9pZCI6IjFmMjQ4NGM1LTdiMjMtNDVmYS1hOGRmLTg4YTg2YWU2MTZkNiIsImlzX2Fub255bW91cyI6ZmFsc2V9.hVpRoDCY_lawz3uWRdjugShx4LYuNuM7Qz3n32SQLbo'

    def on_start(self):
        """Se ejecuta al iniciar cada usuario virtual."""
        self.client.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task(2) # El (2) significa que esta tarea se hace el doble de veces que las otras
    def ver_tablero(self):
        # Prueba el endpoint del Tablero (carga pesada)
        self.client.get("/api/v1/tablero/")

    @task(1)
    def listar_vehiculos(self):
        # Prueba el listado de vehículos
        self.client.get("/api/v1/vehiculos/")

    @task(1)
    def ver_perfil(self):
        # Prueba carga de perfil
        self.client.get("/api/v1/mi-perfil/")