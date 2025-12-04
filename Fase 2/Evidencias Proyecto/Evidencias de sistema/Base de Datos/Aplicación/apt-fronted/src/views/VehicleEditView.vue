<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const vehicleId = route.params.id
const isLoading = ref(true)
const isSaving = ref(false)
const mensaje = ref({ text: '', type: '' })
const allUsers = ref([])
const historial = ref([])
const API_URL = import.meta.env.VITE_API_URL

const form = ref({
  patente: '',
  marca: '',
  modelo: '',
  chofer_id: null,
})

// --- VALIDACIÓN VISUAL DE PATENTE ---
const esPatenteValida = computed(() => {
  if (!form.value.patente) return false
  const p = form.value.patente.toUpperCase().replace(/[^A-Z0-9]/g, '')
  return /^[A-Z]{2}\d{4}$/.test(p) || /^[A-Z]{4}\d{2}$/.test(p)
})

const loadVehicle = async () => {
  const res = await fetch(`${API_URL}/vehiculos/${vehicleId}/`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  if (!res.ok) throw new Error('Error al cargar vehículo')
  const data = await res.json()
  form.value.patente = data.patente
  form.value.marca = data.marca
  form.value.modelo = data.modelo
  form.value.chofer_id = data.chofer ? data.chofer.id : null
  historial.value = data.historial_patentes || []
}

const loadUsers = async () => {
  const res = await fetch(`${API_URL}/admin/usuarios/`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  if (res.ok) allUsers.value = await res.json()
}

const choferesDisponibles = computed(() => {
  return allUsers.value.filter((user) => {
    if (user.rol !== 'CHOFER') return false
    const estaLibre = !user.vehiculo_actual
    const esElActual = user.id === form.value.chofer_id
    return estaLibre || esElActual
  })
})

const saveChanges = async () => {
  if (!esPatenteValida.value) {
    mensaje.value = { text: '⚠️ Formato de patente inválido.', type: 'error' }
    return
  }
  isSaving.value = true
  mensaje.value = { text: '', type: '' }

  try {
    const res = await fetch(`${API_URL}/vehiculos/${vehicleId}/editar/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(form.value),
    })

    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.detail || 'Error al actualizar')
    }
    mensaje.value = { text: '✅ Vehículo actualizado con éxito.', type: 'success' }
    await initData()
  } catch (error) {
    mensaje.value = { text: error.message, type: 'error' }
  } finally {
    isSaving.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'Presente'
  return new Date(dateString).toLocaleString('es-CL')
}

const initData = async () => {
  try {
    isLoading.value = true
    await Promise.all([loadVehicle(), loadUsers()])
  } catch (e) {
    console.error(e)
    mensaje.value = { text: 'Error cargando datos.', type: 'error' }
  } finally {
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  }
}

onMounted(() => {
  initData()
})
</script>

<template>
  <div class="edit-container">
    <div class="header-actions">
      <button class="back-button" @click="router.back()">← Volver</button>
      <h2 class="page-title">
        Gestión de Vehículo <span class="highlight">#{{ vehicleId }}</span>
      </h2>
    </div>

    <Transition name="fade" mode="out-in">
      <div v-if="isLoading" key="loading" class="loading-wrapper">
        <div class="spinner-aurora"></div>
        <p>Cargando datos...</p>
      </div>

      <div v-else key="content" class="content-grid">
        <div class="panel-aurora form-card">
          <h3 class="section-title">📝 Editar Información</h3>

          <div class="form-group highlight-group">
            <label for="select-chofer">👤 Chofer Asignado</label>
            <div class="select-wrapper">
              <select id="select-chofer" v-model="form.chofer_id" class="input-aurora select">
                <option :value="null">-- Sin Asignar --</option>
                <option v-for="chofer in choferesDisponibles" :key="chofer.id" :value="chofer.id">
                  {{ chofer.nombre }} (RUT: {{ chofer.rut || 'S/R' }})
                </option>
              </select>
            </div>
            <p class="hint-text">Selecciona un chofer libre para asignar el vehículo.</p>
          </div>

          <div class="divider"></div>

          <div class="vehicle-form-body">
            <div class="patente-section">
              <div class="form-group">
                <label for="input-patente">Patente</label>
                <div class="input-wrapper">
                  <input
                    id="input-patente"
                    v-model="form.patente"
                    type="text"
                    class="input-aurora patente"
                    :class="{ valid: esPatenteValida, invalid: form.patente && !esPatenteValida }"
                    autocomplete="off"
                    placeholder="AAAA12"
                  />
                  <span v-if="form.patente && esPatenteValida" class="validation-icon">✓</span>
                </div>
                <span v-if="form.patente && !esPatenteValida" class="hint-error"
                  >Formato inválido (AA1234 o BBBB12)</span
                >
              </div>
            </div>

            <div class="details-grid">
              <div class="form-group">
                <label for="input-marca">Marca</label>
                <input
                  id="input-marca"
                  v-model="form.marca"
                  type="text"
                  class="input-aurora"
                  placeholder="Ej: Scania"
                />
              </div>

              <div class="form-group">
                <label for="input-modelo">Modelo</label>
                <input
                  id="input-modelo"
                  v-model="form.modelo"
                  type="text"
                  class="input-aurora"
                  placeholder="Ej: R500"
                />
              </div>
            </div>
          </div>

          <div class="actions center-actions">
            <button
              :disabled="isSaving || !esPatenteValida"
              class="btn-aurora save compact"
              @click="saveChanges"
            >
              {{ isSaving ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>

          <div v-if="mensaje.text" :class="['alert', mensaje.type]">
            {{ mensaje.text }}
          </div>
        </div>

        <div class="panel-aurora history-card">
          <h3 class="section-title">📜 Historial de Patentes</h3>

          <div v-if="historial.length === 0" class="empty-history">
            <span class="icon">∅</span>
            <p>No hay cambios registrados.</p>
          </div>

          <div v-else class="history-scroll scroll-aurora">
            <table class="history-table">
              <thead>
                <tr>
                  <th>Patente Antigua</th>
                  <th>Fecha Cambio</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in historial" :key="item.id">
                  <td class="old-plate">{{ item.patente }}</td>
                  <td class="date">{{ formatDate(item.desde) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* --- TRANSICIONES --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* --- LAYOUT BASE --- */
.edit-container {
  padding: 30px;
  max-width: 1100px;
  margin: 0 auto;
  color: #e2e8f0;
  min-height: 85vh;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}
.page-title {
  margin: 0;
  font-size: 1.8rem;
  color: #f8fafc;
  font-weight: 700;
}
.page-title .highlight {
  color: #38bdf8;
  font-family: monospace;
}

.back-button {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: #cbd5e1;
  padding: 8px 16px;
  border-radius: 99px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(4px);
}
.back-button:hover {
  border-color: #38bdf8;
  color: #fff;
  transform: translateX(-3px);
  background: rgba(56, 189, 248, 0.15);
}

/* --- PANELES AURORA --- */
.content-grid {
  display: grid;
  grid-template-columns: 1.3fr 0.9fr;
  gap: 28px;
}

.panel-aurora {
  background:
    radial-gradient(circle at 10% 10%, rgba(59, 130, 246, 0.08), transparent 40%),
    radial-gradient(circle at 90% 90%, rgba(16, 185, 129, 0.05), transparent 40%),
    rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(12px);
}

.section-title {
  margin: 0 0 24px;
  font-size: 1.2rem;
  color: #e2e8f0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  padding-bottom: 12px;
}

/* --- 🌟 GRILLA DE INPUTS (AQUÍ ESTÁ LA MEJORA) 🌟 --- */
.vehicle-form-body {
  display: flex;
  flex-direction: column;
  gap: 32px; /* Espacio grande entre bloques */
}

.patente-section {
  margin-bottom: 10px; /* Espacio extra debajo de la patente */
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* Fuerza 2 columnas iguales */
  gap: 24px; /* Espacio horizontal entre Marca y Modelo */
  align-items: start;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px; /* Espacio entre Label e Input */
}

.form-group label {
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin-left: 4px;
}

/* --- INPUTS ESTILIZADOS --- */
.input-wrapper {
  position: relative;
  width: 100%;
}
.input-aurora {
  width: 100%;
  /* 🌟 PADDING GENEROSO PARA QUE NO SE VEAN APLASTADOS */
  padding: 14px 16px;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 1rem;
  transition: all 0.2s ease;
  /* Asegura que ocupen el espacio correcto */
  box-sizing: border-box;
  height: 52px; /* Altura fija para consistencia */
}
.input-aurora:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
  outline: none;
  background: rgba(30, 41, 59, 0.8);
}

.input-aurora.patente {
  font-family: monospace;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
  font-size: 1.2rem; /* Patente más grande */
}
.input-aurora.patente.valid {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}
.input-aurora.patente.invalid {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.validation-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #10b981;
  font-weight: bold;
  font-size: 1.2rem;
}
.hint-error {
  color: #ef4444;
  font-size: 0.8rem;
  margin-top: 6px;
  margin-left: 4px;
}

/* Select Especial */
.highlight-group {
  background: rgba(56, 189, 248, 0.05);
  padding: 20px;
  border-radius: 16px;
  border: 1px dashed rgba(56, 189, 248, 0.3);
  margin-bottom: 28px; /* Más espacio abajo */
}
.input-aurora.select {
  appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 16px;
  padding-right: 40px;
}
.hint-text {
  font-size: 0.8rem;
  color: #64748b;
  margin-top: 8px;
}

.divider {
  height: 1px;
  background: rgba(148, 163, 184, 0.15);
  margin: 32px 0;
}

/* --- BOTÓN CORTO Y CENTRADO --- */
.actions {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.btn-aurora.save.compact {
  /* 🌟 TAMAÑO COMPACTO */
  width: auto;
  min-width: 180px;
  padding: 12px 30px;
  border: none;
  border-radius: 99px; /* Forma de píldora */
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.4);
}
.btn-aurora.save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.5);
}
.btn-aurora:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  filter: grayscale(0.8);
}

/* Feedback */
.alert {
  margin-top: 24px;
  padding: 14px;
  border-radius: 12px;
  text-align: center;
  font-size: 0.95rem;
  font-weight: 500;
}
.alert.success {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.alert.error {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* --- HISTORIAL Y SCROLL AURORA --- */
.history-scroll {
  max-height: 350px;
  overflow-y: auto;
  padding-right: 10px;
}

/* Scrollbar Aurora (Verde) */
.scroll-aurora::-webkit-scrollbar {
  width: 8px;
}
.scroll-aurora::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3);
  border-radius: 4px;
}
.scroll-aurora::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(52, 211, 153, 0.4), rgba(16, 185, 129, 0.4)); /* Verde */
  border-radius: 4px;
  border: 1px solid rgba(15, 23, 42, 0.5);
}
.scroll-aurora::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(52, 211, 153, 0.6), rgba(16, 185, 129, 0.6));
}

.history-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;
}
.history-table th {
  text-align: left;
  color: #94a3b8;
  padding: 0 12px 8px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.history-table tr {
  background: rgba(30, 41, 59, 0.4);
  transition: background 0.2s;
}
.history-table tr:hover {
  background: rgba(30, 41, 59, 0.7);
}
.history-table td {
  padding: 14px 12px;
}
.history-table td:first-child {
  border-radius: 8px 0 0 8px;
}
.history-table td:last-child {
  border-radius: 0 8px 8px 0;
}

.old-plate {
  color: #ef4444;
  font-family: monospace;
  font-weight: 700;
  font-size: 1rem;
}
.date {
  color: #cbd5e1;
  font-size: 0.9rem;
}

.empty-history {
  text-align: center;
  padding: 60px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-history .icon {
  font-size: 2.5rem;
  opacity: 0.5;
}

/* Spinner */
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 0;
  color: #94a3b8;
  gap: 16px;
}
.spinner-aurora {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: rgba(59, 130, 246, 0.5);
  border-bottom-color: rgba(16, 185, 129, 0.2);
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .details-grid {
    grid-template-columns: 1fr; /* En móvil, una columna */
  }
}
</style>
