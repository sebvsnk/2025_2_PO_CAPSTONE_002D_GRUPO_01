<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const API_BASE_URL = import.meta.env.VITE_API_URL

// --- Estado de la Bitácora (Dashboard) ---
const bitacora = ref([])
const totales = ref({ entradas: 0, salidas: 0 })
const isLoading = ref(true)

// --- Estado del Check-in (Flujo) ---
const patenteInput = ref('')
const selectedVehicle = ref(null) // Guarda el vehículo encontrado
const isSearching = ref(false)
const isSubmitting = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)
const currentPage = ref(1)
const pageSize = 10
const showConfirmModal = ref(false)
const confirmTipo = ref(null)

// --- Estado del vehiculo en base a la bitacora ---
const ultimoMovimiento = computed(() => {
  if (!selectedVehicle.value || !bitacora.value?.length) return null
  const registrosVehiculo = bitacora.value.filter(
    (log) => log.vehiculo?.id === selectedVehicle.value.id,
  )
  if (!registrosVehiculo.length) return null

  return registrosVehiculo.reduce((ultimo, logActual) => {
    if (!ultimo) return logActual
    const fechaUltimo = new Date(ultimo.fecha_hora)
    const fechaActual = new Date(logActual.fecha_hora)
    return fechaActual > fechaUltimo ? logActual : ultimo
  }, null)
})
const vehiculoDentro = computed(() => ultimoMovimiento.value?.tipo === 'ENTRADA')
const vehiculoFuera = computed(() => ultimoMovimiento.value?.tipo === 'SALIDA')
const esPrimeraVez = computed(() => selectedVehicle.value && !ultimoMovimiento.value)
const totalPaginas = computed(() => Math.max(1, Math.ceil(bitacora.value.length / pageSize)))
const bitacoraPaginada = computed(() => {
  const inicio = (currentPage.value - 1) * pageSize
  return bitacora.value.slice(inicio, inicio + pageSize)
})

// 1. Cargar la Bitácora y Totales (RF-BIT-01, RF-BIT-03)
const fetchBitacora = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/bitacora/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error al cargar la bitácora.')

    const data = await response.json()
    // La API devuelve un objeto { totales: {...}, registros: [...] }
    bitacora.value = data.registros
    totales.value = data.totales
    currentPage.value = 1
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isLoading.value = false
  }
}

// 2. Buscar Patente (Mockup pág 4-5)
const searchPatente = async () => {
  if (!patenteInput.value) {
    errorMsg.value = 'Debe ingresar una patente para buscar.'
    return
  }
  isSearching.value = true
  errorMsg.value = null
  selectedVehicle.value = null // Limpia la selección anterior

  try {
    // Usamos la API de Vehiculos con el filtro 'search'
    const url = `${API_BASE_URL}/vehiculos/?search=${patenteInput.value}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error del servidor al buscar vehículo.')

    const data = await response.json()

    if (data.length === 0) {
      throw new Error(`Patente "${patenteInput.value}" no encontrada en el sistema.`)
    }

    // Éxito: Carga el primer resultado (debería ser único)
    selectedVehicle.value = data[0]
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isSearching.value = false
  }
}

const solicitarMovimiento = (tipoMovimiento) => {
  errorMsg.value = null
  successMsg.value = null

  if (!selectedVehicle.value) {
    errorMsg.value = 'Error: No hay un vehiculo seleccionado.'
    return
  }
  if (esPrimeraVez.value && tipoMovimiento === 'SALIDA') {
    errorMsg.value = 'Es la primera vez de este vehiculo. Registre ENTRADA primero.'
    return
  }
  if (ultimoMovimiento.value?.tipo === tipoMovimiento) {
    errorMsg.value =
      tipoMovimiento === 'ENTRADA'
        ? 'El vehiculo ya registra una ENTRADA vigente. Debe marcar SALIDA antes de otro ingreso.'
        : 'El vehiculo ya registra una SALIDA. Debe marcar ENTRADA antes de una nueva SALIDA.'
    return
  }

  confirmTipo.value = tipoMovimiento
  showConfirmModal.value = true
}

const cancelarConfirmacion = () => {
  confirmTipo.value = null
  showConfirmModal.value = false
}

const confirmarMovimiento = async () => {
  if (!confirmTipo.value) return
  await handleRegister(confirmTipo.value)
  confirmTipo.value = null
  showConfirmModal.value = false
}

// 3. Registrar ENTRADA o SALIDA (Mockup pog 6)
const handleRegister = async (tipoMovimiento) => {
  if (!selectedVehicle.value) {
    errorMsg.value = 'Error: No hay un vehiculo seleccionado.'
    return
  }
  if (esPrimeraVez.value && tipoMovimiento === 'SALIDA') {
    errorMsg.value = 'Es la primera vez de este vehiculo. Registre ENTRADA primero.'
    return
  }
  if (ultimoMovimiento.value?.tipo === tipoMovimiento) {
    errorMsg.value =
      tipoMovimiento === 'ENTRADA'
        ? 'El vehiculo ya registra una ENTRADA vigente. Debe marcar SALIDA antes de otro ingreso.'
        : 'El vehiculo ya registra una SALIDA. Debe marcar ENTRADA antes de una nueva SALIDA.'
    return
  }

  isSubmitting.value = true
  errorMsg.value = null
  successMsg.value = null

  const payload = {
    vehiculo_id: selectedVehicle.value.id, // El API espera el ID del vehículo
    tipo: tipoMovimiento, // 'ENTRADA' o 'SALIDA'
    usuario_id: authStore.user?.id, // ID del perfil de portería (opcional)
  }

  try {
    const url = `${API_BASE_URL}/bitacora/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Error al registrar el movimiento.')
    }

    successMsg.value = `✅ ${tipoMovimiento} registrada para ${selectedVehicle.value.patente}.`

    // Limpiar y recargar
    patenteInput.value = ''
    selectedVehicle.value = null
    await fetchBitacora() // Actualiza la lista y los totales
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

// Carga inicial al montar
onMounted(fetchBitacora)
</script>

<template>
  <div class="checkin-wrapper">
    <div class="porteria-container">
      <header class="porteria-header">
        <button class="back-button" @click="router.push({ name: 'Dashboard' })">
          Volver al Inicio
        </button>
        <h1>Bitácora de Portería</h1>
      </header>

      <div class="porteria-grid">
        <section class="register-card">
          <h2>Registrar Entrada / Salida</h2>

          <form class="search-form" @submit.prevent="searchPatente">
            <label for="patente">Buscar Patente:</label>
            <input
              id="patente"
              v-model="patenteInput"
              type="text"
              placeholder="Escribe patente (ej: CJHD92)"
              :disabled="isSearching"
            />
            <button type="submit" :disabled="isSearching">
              {{ isSearching ? 'Buscando...' : 'Siguiente' }}
            </button>
          </form>

          <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>
          <div v-if="successMsg" class="success-message">{{ successMsg }}</div>

          <div v-if="selectedVehicle" class="vehicle-details">
            <hr />
            <h3>Veh??culo Encontrado</h3>
            <div class="data-group">
              <label>Patente:</label>
              <p>{{ selectedVehicle.patente }}</p>
            </div>
            <div class="data-group">
              <label>Veh??culo:</label>
              <p>{{ selectedVehicle.marca }} {{ selectedVehicle.modelo }}</p>
            </div>
            <div class="data-group">
              <label>Datos Contacto (Chofer):</label>
              <p>{{ selectedVehicle.chofer?.nombre || 'No asignado' }}</p>
              <p class="sub-detail">{{ selectedVehicle.chofer?.rut || 'Sin RUT' }}</p>
              <p class="sub-detail">
                {{ selectedVehicle.chofer?.numero_telefonico || 'Sin tel?fono' }}
              </p>
            </div>

            <div v-if="ultimoMovimiento" class="data-group">
              <label>Ultimo movimiento:</label>
              <p>
                {{ ultimoMovimiento.tipo }} -
                {{ new Date(ultimoMovimiento.fecha_hora).toLocaleString('es-CL') }}
              </p>
            </div>
            <div v-else class="data-group">
              <label>Ultimo movimiento:</label>
              <p>Sin registros anteriores</p>
            </div>
            <div v-if="vehiculoDentro" class="info-state">
              Este vehiculo ya esta marcado como dentro. Registre SALIDA antes de volver a marcar
              ENTRADA.
            </div>
            <div v-else-if="vehiculoFuera" class="info-state">
              Este vehiculo ya esta marcado como fuera. Registre ENTRADA antes de otra SALIDA.
            </div>
            <div v-else-if="esPrimeraVez" class="info-state neutral">
              Primera visita de este vehiculo. Solo puede marcar ENTRADA.
            </div>

            <div class="action-buttons">
              <button
                :disabled="isSubmitting || vehiculoDentro"
                class="btn-entrada"
                @click="solicitarMovimiento('ENTRADA')"
              >
                Marcar ENTRADA
              </button>
              <button
                :disabled="isSubmitting || vehiculoFuera || esPrimeraVez"
                class="btn-salida"
                @click="solicitarMovimiento('SALIDA')"
              >
                Marcar SALIDA
              </button>
            </div>
          </div>
        </section>

        <section class="log-card">
          <h2>Resumen de Entradas y salidas</h2>
          <div class="totals-grid">
            <div class="total-box entradas">
              <span>{{ totales.entradas }}</span>
              <label>Entradas</label>
            </div>
            <div class="total-box salidas">
              <span>{{ totales.salidas }}</span>
              <label>Salidas</label>
            </div>
          </div>

          <h3>últimas Entradas y Salidas</h3>
          <div v-if="isLoading" class="loading-state">
            <div class="spinner-aurora"></div>
            <span>Cargando bitacora...</span>
          </div>
          <table v-else class="log-table glass-table">
            <thead>
              <tr>
                <th>Patente</th>
                <th>Entrada / Salida</th>
                <th>Fecha / Hora</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in bitacoraPaginada" :key="log.id">
                <td>{{ log.vehiculo?.patente || 'N/A' }}</td>
                <td>
                  <span :class="['tipo-tag', log.tipo.toLowerCase()]">{{ log.tipo }}</span>
                </td>
                <td>{{ new Date(log.fecha_hora).toLocaleString('es-CL') }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="!isLoading && bitacora.length > pageSize" class="pagination">
            <button :disabled="currentPage === 1" @click="currentPage--">Anterior</button>
            <span>Pagina {{ currentPage }} de {{ totalPaginas }}</span>
            <button :disabled="currentPage === totalPaginas" @click="currentPage++">
              Siguiente
            </button>
          </div>
        </section>
      </div>
    </div>
    <div v-if="showConfirmModal" class="modal-backdrop">
      <div class="modal-card glass-card">
        <h4>Confirmar {{ confirmTipo }}</h4>
        <p>
          Estas seguro de marcar {{ confirmTipo }} para
          {{ selectedVehicle?.patente || 'este vehiculo' }}?
        </p>
        <div class="modal-actions">
          <button class="btn-secondary" :disabled="isSubmitting" @click="cancelarConfirmacion">
            Cancelar
          </button>
          <button class="btn-primary" :disabled="isSubmitting" @click="confirmarMovimiento">
            {{ isSubmitting ? 'Procesando...' : 'Confirmar' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.porteria-container {
  max-width: 1400px;
  margin: 30px auto;
  padding: 0 20px;
}
.porteria-header {
  display: flex;
  align-items: center;
  border-bottom: 2px solid #ff6700; /* Color Portería */
  padding-bottom: 15px;
  margin-bottom: 25px;
}
.porteria-header h1 {
  font-size: 28px;
  flex-grow: 1;
  text-align: center;
}
.back-button {
  padding: 10px 18px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.3), rgba(45, 212, 191, 0.3));
  color: #e2e8f0;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow:
    0 12px 26px rgba(15, 23, 42, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.back-button:hover {
  transform: translateY(-1px);
  box-shadow:
    0 16px 34px rgba(15, 23, 42, 0.55),
    0 0 18px rgba(59, 130, 246, 0.22);
}
.porteria-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 30px;
}
.register-card,
.log-card {
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 55%),
    radial-gradient(circle at 80% 0%, rgba(34, 197, 94, 0.12), transparent 50%),
    rgba(8, 15, 32, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 16px;
  box-shadow: 0 35px 85px rgba(2, 6, 23, 0.65);
  position: relative;
  overflow: hidden;
  max-height: 720px;
  overflow-y: auto;
  transition:
    transform 0.2s ease,
    box-shadow 0.25s ease,
    border-color 0.2s ease;
}
.register-card h2,
.log-card h2 {
  margin-top: 0;
}
.search-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.search-form label {
  font-weight: 600;
}
.search-form input {
  padding: 10px;
  border: 1px solid var(--input-border);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text-base);
}
.search-form button {
  padding: 10px;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: bold;
}
.vehicle-details {
  margin-top: 20px;
}
.data-group label {
  font-weight: bold;
  color: var(--text-muted);
}
.data-group p {
  margin: 2px 0;
}
.data-group .sub-detail {
  font-size: 0.9em;
  color: var(--text-muted);
}
.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
}
.action-buttons button {
  padding: 12px;
  border: none;
  border-radius: 999px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition:
    transform 0.15s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow:
    0 12px 26px rgba(15, 23, 42, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.btn-entrada {
  background-color: #22c55e;
}
.btn-salida {
  background-color: #f87171;
}
.action-buttons button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 16px 34px rgba(15, 23, 42, 0.55),
    0 0 18px rgba(59, 130, 246, 0.22);
}
.action-buttons button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.1);
}
.totals-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 20px;
}
.total-box {
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}
.total-box span {
  font-size: 2.5rem;
  font-weight: bold;
  display: block;
}
.total-box label {
  font-size: 1rem;
  font-weight: 600;
}
.total-box.entradas {
  background-color: rgba(34, 197, 94, 0.18);
  color: #bbf7d0;
}
.total-box.salidas {
  background-color: rgba(248, 113, 113, 0.18);
  color: #fecaca;
}
.log-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 10px;
}
.log-table th,
.log-table td {
  padding: 8px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  text-align: left;
  transition:
    background-color 0.2s ease,
    transform 0.15s ease;
}
.tipo-tag {
  padding: 3px 8px;
  border-radius: 4px;
  color: white;
  font-weight: 600;
}
.tipo-tag.entrada {
  background-color: #22c55e;
}
.tipo-tag.salida {
  background-color: #f87171;
}
.log-table tbody tr:hover {
  background-color: rgba(59, 130, 246, 0.08);
  transform: translateY(-1px);
}
.glass-table {
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(8px);
}
.error-state,
.success-message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.error-state {
  color: #f87171;
  background-color: rgba(248, 113, 113, 0.18);
}
.success-message {
  color: #155724;
  background-color: rgba(34, 197, 94, 0.18);
}
.info-state.neutral {
  color: #e0f2fe;
  background-color: rgba(59, 130, 246, 0.14);
}
.loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
}
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  gap: 10px;
}
.pagination button {
  background: rgba(59, 130, 246, 0.9);
  color: #fff;
  border: none;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
}
.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 40;
}
.modal-card {
  max-width: 420px;
  width: 92%;
  padding: 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.18), rgba(16, 185, 129, 0.14));
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}
.btn-primary,
.btn-secondary {
  border: none;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
}
.btn-primary {
  background: #22c55e;
  color: #0b1b2b;
}
.btn-secondary {
  background: rgba(255, 255, 255, 0.12);
  color: #e2e8f0;
}
.glass-card {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.glass-table::-webkit-scrollbar,
.log-card::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.glass-table::-webkit-scrollbar-thumb,
.log-card::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 10px;
}
.register-card:hover,
.log-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 40px 95px rgba(2, 6, 23, 0.75);
  border-color: rgba(255, 255, 255, 0.28);
}
.success-message,
.error-state {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
}
.modal-backdrop {
  animation: fadeIn 0.18s ease;
}
.modal-card {
  animation: popIn 0.22s ease;
}
.spinner-aurora {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #22d3ee;
  border-right-color: rgba(59, 130, 246, 0.55);
  border-left-color: rgba(59, 130, 246, 0.18);
  border-bottom-color: rgba(34, 211, 238, 0.12);
  animation:
    aurora-spin 0.9s linear infinite,
    pulseGlow 2s ease-in-out infinite;
  box-shadow:
    0 0 18px rgba(34, 211, 238, 0.35),
    0 0 32px rgba(59, 130, 246, 0.22);
}
.spinner-aurora::after {
  content: '';
  position: absolute;
  inset: 14px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0));
  filter: blur(2px);
}
@keyframes aurora-spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes pulseGlow {
  0% {
    box-shadow:
      0 0 18px rgba(34, 211, 238, 0.35),
      0 0 32px rgba(59, 130, 246, 0.22);
    opacity: 0.95;
  }
  50% {
    box-shadow:
      0 0 24px rgba(34, 211, 238, 0.5),
      0 0 40px rgba(59, 130, 246, 0.3);
    opacity: 1;
  }
  100% {
    box-shadow:
      0 0 18px rgba(34, 211, 238, 0.35),
      0 0 32px rgba(59, 130, 246, 0.22);
    opacity: 0.95;
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
@keyframes popIn {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
.info-state {
  color: #0b5ed7;
  background-color: rgba(59, 130, 246, 0.12);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  border: 1px solid rgba(59, 130, 246, 0.4);
}
</style>
