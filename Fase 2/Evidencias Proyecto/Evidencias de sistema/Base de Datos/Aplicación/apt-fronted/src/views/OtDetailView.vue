<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const otId = route.params.id
const otDetail = ref(null)
const isLoading = ref(true)
const errorMsg = ref(null)
const isProcessing = ref(false)

const isEditing = ref(false)
const editDescription = ref('')

const showSuccessCheck = ref(false)
const successCheckText = ref('')

const showConfirmModal = ref(false)
const modalConfig = ref({
  title: '',
  message: '',
  confirmText: '',
  variant: 'default',
  action: null,
})

const canTakeAction = computed(() => {
  return authStore.userRole === 'ADMIN' || authStore.userRole === 'SUPERVISOR'
})

const isEditable = computed(() => {
  if (!otDetail.value) return false
  return !['CERRADA', 'ANULADA'].includes(otDetail.value.estado.code)
})
const isOtRestringida = computed(() => ['CERRADA', 'ANULADA'].includes(otDetail.value?.estado.code))

// Computada para detectar si hay tareas que impiden el cierre
const hasPendingTasks = computed(() => {
  if (!otDetail.value || !otDetail.value.tareas) return false

  // Buscamos si existe alguna tarea que NO esté en estado final
  return otDetail.value.tareas.some((t) => !['HECHA', 'ANULADA'].includes(t.estado.code))
})

const API_BASE_URL = import.meta.env.VITE_API_URL

const fetchOtDetail = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/ot/${otId}/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      throw new Error(`Error ${response.status}: OT no encontrada o acceso denegado.`)
    }
    otDetail.value = await response.json()
  } catch (error) {
    console.error('OT Detail API Error:', error)
    errorMsg.value = `Fallo al cargar la OT: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchOtDetail()
  } else {
    router.push({ name: 'Login' })
  }
})

const triggerSuccessAnimation = (message) => {
  successCheckText.value = message
  showSuccessCheck.value = true
  setTimeout(() => {
    showSuccessCheck.value = false
    successCheckText.value = ''
  }, 2000)
}

const navigateToTasks = () => {
  if (isOtRestringida.value) {
    router.push({ name: 'TaskList', params: { otId: otId } })
  } else {
    router.push({ name: 'TaskList', params: { otId: otId } })
  }
}

const handleChangeOtState = async (newCode, newLabel) => {
  isProcessing.value = true
  errorMsg.value = null

  try {
    const url = `${API_BASE_URL}/ot/${otId}/cambiar_estado/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({ estado_code: newCode }),
    })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || data.pendientes || `Error al cambiar estado.`)
    }
    otDetail.value = data
    triggerSuccessAnimation(`OT movida a "${newLabel}"`)
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isProcessing.value = false
  }
}

const openConfirmationModal = (newCode, newLabel) => {
  let title = ''
  let message = ''
  let confirmText = ''
  let variant = 'default'

  if (newCode === 'PAUSADA') {
    title = '¿Pausar la OT?'
    message = 'Se detendrá temporalmente la ejecución hasta que la reanudes.'
    confirmText = 'Confirmar Pausa'
    variant = 'warning'
  } else if (newCode === 'ACTIVA') {
    title = '¿Reanudar la OT?'
    message = 'La OT volverá al estado activo y podrás continuar con las tareas.'
    confirmText = 'Sí, reanudar'
    variant = 'success'
  } else if (newCode === 'CERRADA') {
    title = '¿Finalizar y cerrar la OT?'
    message = 'Se dará por completada la orden de trabajo y ya no podrás editarla.'
    confirmText = 'Sí, cerrar OT'
    variant = 'danger'
  } else {
    title = `¿Confirmar cambio a ${newLabel}?`
    message = 'Esta acción actualizará el estado de la orden.'
    confirmText = `Confirmar ${newLabel}`
  }

  modalConfig.value = {
    title,
    message,
    confirmText,
    variant,
    action: () => handleChangeOtState(newCode, newLabel),
  }
  showConfirmModal.value = true
}
const executeModalAction = () => {
  if (modalConfig.value.action) {
    modalConfig.value.action()
  }
  showConfirmModal.value = false
}

const startEditing = () => {
  editDescription.value = otDetail.value.descripcion || ''
  isEditing.value = true
}

const saveDescription = async () => {
  if (editDescription.value === (otDetail.value.descripcion || '')) {
    isEditing.value = false
    triggerSuccessAnimation('No se detectaron cambios')
    return
  }

  isProcessing.value = true
  errorMsg.value = null

  try {
    const url = `${API_BASE_URL}/ot/${otId}/`
    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify({ descripcion: editDescription.value }),
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.detail || 'No se pudo guardar la descripción.')

    otDetail.value = data
    isEditing.value = false
    triggerSuccessAnimation('Descripción actualizada')
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isProcessing.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="ot-detail-container">
    <header v-if="otDetail" class="ot-hero">
      <div class="hero-left">
        <button class="back-button pill" @click="router.push({ name: 'SupervisorDashboard' })">
          &larr; Volver al Tablero
        </button>
        <div class="hero-copy">
          <p class="eyebrow">Detalle de Orden de Trabajo</p>
          <h1>OT #{{ otId }}</h1>
          <p class="hero-helper">Gestiona tareas, evidencia y estado de la OT.</p>
        </div>
      </div>
      <div class="hero-meta">
        <div>
          <span class="meta-label">Patente</span>
          <span class="meta-chip">{{ otDetail.vehiculo.patente }}</span>
        </div>
        <div>
          <span class="meta-label">Estado</span>
          <span :class="['meta-status', otDetail.estado.code.toLowerCase()]">
            {{ otDetail.estado.label }}
          </span>
        </div>
      </div>
    </header>
    <header v-else class="ot-detail-header">
      <button class="back-button" @click="router.push({ name: 'SupervisorDashboard' })">
        &larr; Volver al Tablero
      </button>
      <h2 class="page-title-internal">
        {{ isLoading ? 'Cargando OT...' : `OT #${otId}` }}
      </h2>
    </header>

    <Transition name="fade">
      <div v-if="hasPendingTasks && !isOtRestringida" class="warning-banner">
        <div class="warning-content">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span
            ><strong>Atención:</strong> Hay tareas en curso. Debes finalizar o anular todas las
            tareas antes de cerrar esta OT.</span
          >
        </div>
      </div>
    </Transition>
    <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>

    <Transition name="fade-content" mode="out-in">
      <div v-if="isLoading" class="kanban-loading-overlay">
        <div class="spinner-aurora"></div>
        <span class="loading-text">Cargando OT...</span>
      </div>

      <div v-else-if="otDetail" class="ot-content-layout">
        <div class="layout-column">
          <div class="info-card">
            <div class="info-grid">
              <div class="info-item">
                <label>Vehículo</label>
                <p>{{ otDetail.vehiculo.marca }} {{ otDetail.vehiculo.modelo }}</p>
              </div>
              <div class="info-item">
                <label>Patente</label>
                <p class="patente-tag">{{ otDetail.vehiculo.patente }}</p>
              </div>
              <div class="info-item">
                <label>Estado</label>
                <p>
                  <span :class="['status-tag', otDetail.estado.code.toLowerCase()]">{{
                    otDetail.estado.label
                  }}</span>
                </p>
              </div>
              <div class="info-item">
                <label>Creada Por</label>
                <p>{{ otDetail.creado_por?.nombre || 'N/A' }}</p>
              </div>
              <div class="info-item">
                <label>Fecha Apertura</label>
                <p>{{ formatDate(otDetail.fecha_apertura) }}</p>
              </div>
              <div class="info-item">
                <label>Fecha Cierre</label>
                <p>{{ formatDate(otDetail.fecha_cierre) }}</p>
              </div>
            </div>
          </div>

          <div class="description-card">
            <div class="card-header">
              <h2>Descripción / Motivo</h2>
              <button
                v-if="!isEditing && canTakeAction && isEditable"
                class="edit-button"
                @click="startEditing"
              >
                Editar
              </button>
            </div>
            <div v-if="isEditing" class="edit-mode">
              <textarea v-model="editDescription" rows="4" :disabled="isProcessing"></textarea>
              <div class="edit-actions">
                <button class="btn btn-secondary" @click="isEditing = false">Cancelar</button>
                <button :disabled="isProcessing" class="btn btn-primary" @click="saveDescription">
                  {{ isProcessing ? 'Guardando...' : 'Guardar' }}
                </button>
              </div>
            </div>
            <p v-else class="description-text">
              {{ otDetail.descripcion || 'Sin descripcion.' }}
            </p>
          </div>
        </div>

        <div class="layout-column">
          <div class="module-card" :class="{ disabled: isOtRestringida }" @click="navigateToTasks">
            <span class="module-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="m14 4 6 6" />
                <path d="M14.7 6.3a4 4 0 1 0 5 5L15 6.3z" />
                <path d="m11 11-8 8" />
                <path d="m3 19 2 2" />
              </svg>
            </span>
            <div class="module-text">
              <h3>Gestión de Tareas</h3>
              <p>Ver, crear y asignar tareas ({{ otDetail.tareas_count || 0 }})</p>
            </div>
            <span class="module-arrow">✓</span>
          </div>
          <div
            class="module-card"
            @click="router.push({ name: 'OtExport', params: { otId: otId } })"
          >
            <span class="module-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
              </svg>
            </span>
            <div class="module-text">
              <h3>Exportar Reporte</h3>
              <p>Generar un PDF/documento imprimible</p>
            </div>
            <span class="module-arrow">→</span>
          </div>

          <div v-if="canTakeAction && isEditable" class="actions-card">
            <h2>Acciones de OT</h2>
            <div class="action-buttons-group">
              <button
                v-if="otDetail.estado.code === 'ACTIVA'"
                class="action-chip pause"
                :disabled="isProcessing"
                @click="openConfirmationModal('PAUSADA', 'Pausada')"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <rect x="6" y="4" width="4" height="16"></rect>
                  <rect x="14" y="4" width="4" height="16"></rect>
                </svg>
                <span>Pausar OT</span>
              </button>
              <button
                v-if="otDetail.estado.code === 'PAUSADA'"
                class="action-chip resume"
                :disabled="isProcessing"
                @click="openConfirmationModal('ACTIVA', 'Activada')"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
                <span>Reanudar OT</span>
              </button>
              <button
                v-if="otDetail.estado.code === 'ACTIVA' || otDetail.estado.code === 'PAUSADA'"
                class="action-chip close"
                :disabled="isProcessing || hasPendingTasks"
                @click="openConfirmationModal('CERRADA', 'Cerrada')"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                <span>Finalizar y Cerrar OT</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal-fade">
      <div v-if="showConfirmModal" class="modal-overlay" @click.self="showConfirmModal = false">
        <div class="confirm-modal">
          <div class="modal-icon" :class="modalConfig.variant">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M12 9v4" />
              <path d="M12 17h.01" />
              <path d="M7.938 4h8.124L22 12l-5.938 8H7.938L2 12z" />
            </svg>
          </div>
          <h3>{{ modalConfig.title }}</h3>
          <p>{{ modalConfig.message }}</p>
          <div class="modal-actions">
            <button type="button" class="modal-btn cancel" @click="showConfirmModal = false">
              Cancelar
            </button>
            <button
              type="button"
              class="modal-btn confirm"
              :class="modalConfig.variant"
              :disabled="isProcessing"
              @click="executeModalAction"
            >
              {{ isProcessing ? 'Procesando...' : modalConfig.confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showSuccessCheck" class="success-overlay">
        <div class="success-animation-container">
          <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none" />
            <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
          </svg>
          <h3 class="success-title">{{ successCheckText }}</h3>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* --- Layout General, Header, Botón Volver (Sin cambios) --- */
.ot-detail-container {
  max-width: 1360px;
  margin: 0 auto;
  padding: 18px;
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 55%),
    radial-gradient(circle at 80% 0%, rgba(34, 197, 94, 0.12), transparent 50%),
    rgba(8, 15, 32, 0.55);
  border-radius: 32px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 35px 85px rgba(2, 6, 23, 0.7);
}
.ot-detail-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin: 0 0 20px 0;
  padding-bottom: 15px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.35);
}
.back-button {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-strong);
  border: 1px solid rgba(148, 163, 184, 0.35);
  padding: 8px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  flex-shrink: 0;
}
.back-button:hover {
  background: rgba(148, 163, 184, 0.25);
}
.page-title-internal {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-strong);
  margin: 0;
  padding: 0;
  border: none;
  flex-grow: 1;
  text-align: left;
}
.patente-title {
  font-family: monospace;
  background: rgba(59, 130, 246, 0.18);
  color: var(--text-strong);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 1.3rem;
  margin-left: 10px;
  vertical-align: middle;
}
.ot-content-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 25px;
}
.layout-column {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* --- Mensajes de Estado (Sin cambios) --- */
.error-state {
  padding: 12px 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 600;
  border: 1px solid transparent;
  color: #721c24;
  background-color: rgba(248, 113, 113, 0.18);
  border-color: rgba(248, 113, 113, 0.35);
}

/* --- Cards, Info, Description, Módulos, Botones (Sin cambios) --- */
.info-card,
.description-card,
.module-card,
.actions-card {
  background: var(--card-bg);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 20px 15px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}
h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-strong);
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
}
.info-item label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 4px;
  display: block;
}
.info-item p {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-base);
}
.patente-tag {
  background-color: rgba(59, 130, 246, 0.18);
  color: #2563eb;
  padding: 3px 8px;
  border-radius: 6px;
  font-weight: 700;
  font-family: monospace;
  display: inline-block;
}
.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 700;
  color: white;
}
.status-tag.nueva {
  background-color: var(--text-muted);
}
.status-tag.activa,
.status-tag.en_proceso {
  background-color: #14b8a6;
}
.status-tag.pausada {
  background-color: #facc15;
  color: var(--text-base);
}
.status-tag.cerrada {
  background-color: #22c55e;
}
.status-tag.anulada {
  background-color: #f87171;
}
.description-text {
  padding: 20px;
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-base);
  line-height: 1.6;
  white-space: pre-wrap;
}
.edit-button {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-base);
  border: 1px solid rgba(148, 163, 184, 0.35);
  padding: 5px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}
.edit-button:hover {
  background: rgba(148, 163, 184, 0.25);
}
.edit-mode {
  padding: 20px;
}
.edit-mode textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--input-border);
  border-radius: 10px;
  background: var(--input-bg);
  color: var(--text-base);
  box-sizing: border-box;
  font-family: inherit;
  font-size: 0.95rem;
  margin-bottom: 10px;
}
.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn {
  padding: 8px 15px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-primary {
  background-color: #3b82f6;
  color: white;
}
.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  transform: translateY(-1px);
}
.btn-secondary {
  background: rgba(148, 163, 184, 0.15);
  color: var(--text-strong);
  border: 1px solid rgba(148, 163, 184, 0.35);
}
.btn-secondary:hover:not(:disabled) {
  background: rgba(148, 163, 184, 0.25);
}
.btn:disabled {
  background-color: rgba(148, 163, 184, 0.25);
  cursor: not-allowed;
  opacity: 0.7;
}
.btn-danger {
  background-color: #f87171;
  color: white;
}
.btn-danger:hover:not(:disabled) {
  background-color: #c82333;
}
.module-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.2s ease;
  cursor: pointer;
  background: var(--card-bg);
}
.module-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  background-color: rgba(15, 23, 42, 0.88);
}
.module-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
  transform: none;
}
.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  display: grid;
  place-items: center;
  color: var(--text-strong);
}
.module-icon svg {
  width: 26px;
  height: 26px;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
.module-text h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-strong);
}
.module-text p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-muted);
}
.module-arrow {
  font-size: 1.5rem;
  color: #9cb2c9;
  margin-left: auto;
  transition: transform 0.2s ease;
}
.module-card:hover .module-arrow {
  transform: translateX(5px);
  color: #3b82f6;
}
.actions-card {
  padding: 20px;
  background-color: rgba(15, 23, 42, 0.88);
}
.action-buttons-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 15px;
}
.btn-action {
  padding: 12px 18px;
  font-size: 1rem;
  text-align: center;
  justify-content: center;
}
.btn-action svg {
  margin-right: 8px;
}
.btn-action:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}
.btn-action.pause {
  background-color: #facc15;
  color: var(--text-base);
}
.btn-action.pause:hover:not(:disabled) {
  background-color: #e0a800;
}
.btn-action.resume {
  background-color: #14b8a6;
  color: white;
}
.btn-action.resume:hover:not(:disabled) {
  background-color: #138496;
}
.btn-action.close {
  background-color: #f87171;
  color: white;
}
.btn-action.close:hover:not(:disabled) {
  background-color: #c82333;
}

/* --- Spinner de Carga de Página ('kanban-loading-overlay') --- */
.kanban-loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
}
.loading-text {
  margin-top: 20px;
  font-size: 1.2rem;
  color: var(--text-strong);
  font-weight: 500;
}
.spinner-aurora {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #3b82f6; /* Azul principal */
  border-right-color: #22d3ee; /* Cyan brillante */
  border-bottom-color: rgba(59, 130, 246, 0.2); /* Sutil */
  animation: spin 1s linear infinite;
  box-shadow: 0 0 25px rgba(34, 211, 238, 0.25); /* Brillo Aurora */
  margin-bottom: 16px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* En la sección <style scoped> de OtDetailView.vue */

.warning-banner {
  background: rgba(245, 158, 11, 0.15); /* Ámbar translúcido */
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24; /* Texto Ámbar claro */
  padding: 14px 20px;
  border-radius: 16px;
  margin-bottom: 24px;
  animation: slideDown 0.4s ease;
}

.warning-content {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
  font-size: 0.95rem;
}
.warning-content svg {
  flex-shrink: 0;
}

/* --- Transición de Carga de Página ('fade-content') --- */
.fade-content-enter-active,
.fade-content-leave-active {
  transition: opacity 0.2s ease-out;
}
.fade-content-enter-from,
.fade-content-leave-to {
  opacity: 0;
}

/* --- Modal de Confirmación (Sin cambios) --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(6px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1200;
  padding: 16px;
}
.confirm-modal {
  width: min(420px, 92%);
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.82));
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 28px;
  padding: 32px;
  box-shadow: 0 30px 80px rgba(2, 6, 23, 0.75);
  text-align: center;
}
.modal-icon {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(14, 165, 233, 0.4);
  background: rgba(14, 165, 233, 0.15);
  color: #38bdf8;
}
.modal-icon.PAUSADA {
  border-color: rgba(250, 204, 21, 0.45);
  background: rgba(250, 204, 21, 0.18);
  color: #facc15;
}
.modal-icon.ACTIVA {
  border-color: rgba(45, 212, 191, 0.45);
  background: rgba(45, 212, 191, 0.18);
  color: #2dd4bf;
}
.modal-icon.CERRADA {
  border-color: rgba(251, 113, 133, 0.5);
  background: rgba(251, 113, 133, 0.2);
  color: #fb7185;
}
.confirm-modal h3 {
  margin: 0 0 8px;
  color: #f8fafc;
  font-size: 1.35rem;
}
.confirm-modal p {
  margin: 0 0 20px;
  color: rgba(226, 232, 240, 0.85);
  font-size: 0.95rem;
}
.modal-actions {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
}
.modal-btn {
  border: none;
  border-radius: 999px;
  font-weight: 600;
  padding: 12px 26px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.modal-btn.cancel {
  background: rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}
.modal-btn.confirm {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0c111d;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
}
.modal-btn.confirm.PAUSADA {
  background: linear-gradient(120deg, #fde047, #fda92b);
  color: #0f172a;
  box-shadow: 0 18px 35px rgba(250, 204, 21, 0.35);
}
.modal-btn.confirm.ACTIVA {
  background: linear-gradient(120deg, #2dd4bf, #34d399);
  color: #042f2e;
}
.modal-btn.confirm.CERRADA {
  background: linear-gradient(120deg, #fb7185, #f472b6);
  color: #fff;
  box-shadow: 0 18px 35px rgba(251, 113, 133, 0.45);
}
.modal-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  box-shadow: none;
}
.modal-btn:not(:disabled):hover {
  transform: translateY(-2px);
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.28s ease;
}
.modal-fade-enter-active .confirm-modal,
.modal-fade-leave-active .confirm-modal {
  transition:
    transform 0.28s ease,
    opacity 0.28s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .confirm-modal,
.modal-fade-leave-to .confirm-modal {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
}

/* --- Overlay de exito --- */
.success-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}
.success-animation-container {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 2.5rem 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* Eliminamos animation modal-pop... */
}
.success-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-strong);
  margin-bottom: 0px;
}
.success-checkmark {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: block;
  stroke-width: 3;
  stroke: #22c55e;
  stroke-miterlimit: 10;
  margin: 0 auto 20px;
  box-shadow: inset 0px 0px 0px #22c55e;
  animation:
    fill 0.4s ease-in-out 0.4s forwards,
    scale 0.3s ease-in-out 0.9s both;
}
.checkmark-circle {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  stroke-width: 3;
  stroke-miterlimit: 10;
  stroke: #22c55e;
  fill: none;
  animation: stroke 0.6s cubic-bezier(0.65, 0.45, 1) forwards;
}
.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

/* * *** INICIO DE LA CORRECCIÓN DE ANIMACIÓN DE ÉXITO ***
 * Reemplazamos las clases .fade-enter... anteriores
 * y eliminamos @keyframes modal-pop
 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-active .success-animation-container,
.fade-leave-active .success-animation-container {
  transition: all 0.3s ease-out;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.fade-enter-from .success-animation-container,
.fade-leave-to .success-animation-container {
  opacity: 0;
  transform: scale(0.9) translateY(10px);
}
/* *** FIN DE LA CORRECCIÓN *** */

/* Eliminamos @keyframes modal-pop */

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
@keyframes scale {
  0%,
  100% {
    transform: none;
  }
  50% {
    transform: scale3d(1.1, 1.1, 1);
  }
}
@keyframes fill {
  100% {
    box-shadow: inset 0px 0px 0px 40px #22c55e;
  }
}
/* --- New glow styles --- */
.back-button.pill {
  border-radius: 999px;
  padding: 9px 18px;
  border-color: rgba(148, 163, 184, 0.45);
  background: rgba(15, 23, 42, 0.75);
  color: #f8fafc;
}
.ot-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  padding: 18px 22px;
  border-radius: 26px;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.65));
  border: 1px solid rgba(148, 163, 184, 0.3);
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.55);
  margin-bottom: 24px;
}
.hero-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.hero-copy h1 {
  margin: 4px 0;
  color: #f8fafc;
}
.hero-helper {
  margin: 0;
  color: rgba(148, 163, 184, 0.9);
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.72rem;
  color: rgba(148, 163, 184, 0.85);
  margin: 0;
}
.hero-meta {
  display: flex;
  gap: 20px;
  align-items: center;
}
.hero-meta > div {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.meta-label {
  font-size: 0.75rem;
  letter-spacing: 0.15em;
  color: rgba(148, 163, 184, 0.85);
  text-transform: uppercase;
}
.meta-chip,
.meta-status {
  margin-top: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 700;
  color: #f8fbff;
  background: rgba(59, 130, 246, 0.32);
  border: 1px solid rgba(147, 197, 253, 0.8);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.4);
}
.meta-status.pausada {
  background: rgba(250, 204, 21, 0.4);
  border-color: rgba(250, 204, 21, 0.7);
  color: #fffbed;
}
.meta-status.activa {
  background: rgba(16, 185, 129, 0.35);
  border-color: rgba(110, 231, 183, 0.9);
  color: #f0fff4;
}
.meta-status.cerrada,
.meta-status.anulada {
  background: rgba(248, 113, 113, 0.38);
  border-color: rgba(248, 113, 113, 0.7);
  color: #fff;
}
.info-card,
.description-card {
  background: rgba(15, 23, 42, 0.78);
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 20px 45px rgba(2, 6, 23, 0.5);
}
.module-card {
  background: rgba(15, 23, 42, 0.85);
  border-radius: 18px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 20px 40px rgba(2, 6, 23, 0.45);
}
.actions-card {
  background: rgba(15, 23, 42, 0.9);
  border-radius: 20px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 20px 45px rgba(2, 6, 23, 0.5);
}
.action-buttons-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.action-buttons-group .action-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  border: none;
  border-radius: 14px;
  padding: 10px 14px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  color: #f8fafc;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.3);
  animation: action-pop 0.35s ease both;
}
.action-buttons-group .action-chip svg {
  width: 20px;
  height: 20px;
}
.action-buttons-group .action-chip:nth-child(2) {
  animation-delay: 0.08s;
}
.action-buttons-group .action-chip:nth-child(3) {
  animation-delay: 0.16s;
}
.action-buttons-group .action-chip.pause {
  background: linear-gradient(120deg, #fde047, #fda92b);
  color: #0f172a;
  border: 1px solid rgba(248, 240, 137, 0.8);
}
.action-buttons-group .action-chip.resume {
  background: linear-gradient(120deg, #2dd4bf, #34d399);
  border: 1px solid rgba(94, 234, 212, 0.65);
}
.action-buttons-group .action-chip.close {
  background: linear-gradient(120deg, #fb7185, #f472b6);
  border: 1px solid rgba(251, 146, 196, 0.7);
}
.action-buttons-group .action-chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
.action-buttons-group .action-chip:not(:disabled):hover {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
}
@keyframes action-pop {
  from {
    opacity: 0;
    transform: translateY(6px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* --- Responsive --- */
@media (max-width: 900px) {
  .ot-content-layout {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 500px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .hero-meta {
    width: 100%;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
