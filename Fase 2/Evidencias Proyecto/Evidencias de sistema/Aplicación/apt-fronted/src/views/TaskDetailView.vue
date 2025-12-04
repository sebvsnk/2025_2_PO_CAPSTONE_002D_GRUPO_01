<script setup>
// --- (El <script setup> sigue exactamente igual que en la respuesta anterior) ---
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const taskId = route.params.taskId
const task = ref(null)
const isLoading = ref(true)
const isProcessing = ref(false)
const errorMsg = ref(null)

const showSuccessCheck = ref(false)
const successCheckText = ref('')

const API_BASE_URL = import.meta.env.VITE_API_URL

const pauseReason = ref('')
const showPauseModal = ref(false)
const showActionConfirm = ref(false)
const actionConfirmConfig = ref({
  title: '',
  message: '',
  confirmText: '',
  variant: 'default',
  action: null,
})

const isMechanic = computed(() => authStore.userRole === 'MECANICO')

const isEditable = computed(() => {
  if (!task.value || !task.value.estado) return false
  return !['HECHA', 'ANULADA'].includes(task.value.estado.code)
})

const attachmentsLocked = computed(() => {
  const status = (task.value?.estado?.code || '').toUpperCase()

  // AGREGAR 'HECHA' A ESTA LISTA
  return ['PAUSADA', 'CERRADA', 'ANULADA', 'NUEVA', 'HECHA'].includes(status)
})

const fetchTaskDetail = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Tarea no encontrada o acceso denegado.`)
    }
    task.value = await response.json()
  } catch (error) {
    console.error('Task Detail API Error:', error)
    errorMsg.value = `Fallo al cargar la Tarea: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const triggerSuccessAnimation = (message) => {
  successCheckText.value = message
  showSuccessCheck.value = true
  setTimeout(() => {
    showSuccessCheck.value = false
    successCheckText.value = ''
  }, 2000)
}

const processAction = async (action, payload = {}) => {
  isProcessing.value = true
  errorMsg.value = null

  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/${action}/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: Object.keys(payload).length ? JSON.stringify(payload) : null,
    })
    const data = await response.json()
    if (!response.ok) {
      errorMsg.value = data.detail || (data.motivo ? data.motivo[0] : 'Error desconocido.')
      throw new Error('Fallo en la acción.')
    }

    if (action === 'pausar') {
      pauseReason.value = ''
    }

    triggerSuccessAnimation(`Tarea ${data.estado.label}`)
    await fetchTaskDetail()
  } catch (error) {
    if (!errorMsg.value) {
      errorMsg.value = error.message || `Fallo al ejecutar la acción ${action}.`
    }
  } finally {
    isProcessing.value = false
  }
}

const actionMap = {
  iniciar: () => processAction('iniciar'),
  reanudar: () => processAction('reanudar'),
  cerrar: () => processAction('cerrar'),
  anular: () => processAction('anular'),
}

const openActionConfirm = (action) => {
  let title = ''
  let message = ''
  let confirmText = ''
  let variant = action

  if (action === 'iniciar') {
    title = '¿Iniciar tarea?'
    message = 'La tarea pasará a estado En proceso.'
    confirmText = 'Sí, iniciar'
  } else if (action === 'reanudar') {
    title = '¿Reanudar tarea?'
    message = 'La tarea volverá a estar activa.'
    confirmText = 'Sí, reanudar'
  } else if (action === 'cerrar') {
    title = '¿Cerrar tarea?'
    message = 'Se marcará como completada y no permitirá más cambios.'
    confirmText = 'Sí, cerrar'
  } else if (action === 'anular') {
    title = '¿Anular tarea?'
    message = 'Esta acción es irreversible y cancelará la tarea.'
    confirmText = 'Sí, anular'
  } else {
    title = 'Confirmar acción'
    message = '¿Deseas continuar con esta acción?'
    confirmText = 'Confirmar'
  }

  actionConfirmConfig.value = {
    title,
    message,
    confirmText,
    variant,
    // eslint-disable-next-line security/detect-object-injection
    action: actionMap[action],
  }
  showActionConfirm.value = true
}

const handleActionClick = (action) => {
  if (action === 'pausar') {
    showPauseModal.value = true
    return
  }
  openActionConfirm(action)
}

const executeActionConfirm = async () => {
  if (actionConfirmConfig.value.action) {
    await actionConfirmConfig.value.action()
  }
  showActionConfirm.value = false
}

const handlePause = async () => {
  if (!pauseReason.value) {
    errorMsg.value = 'Debe ingresar un motivo para pausar la tarea.'
    return
  }
  showPauseModal.value = false
  await processAction('pausar', { motivo: pauseReason.value })
}

onMounted(fetchTaskDetail)

const navigateBackToOt = () => {
  if (isMechanic.value) {
    router.push({ name: 'MechanicTasks' })
    return
  }

  if (task.value && task.value.ot_id) {
    router.push({ name: 'TaskList', params: { otId: task.value.ot_id } })
  } else {
    router.push({ name: 'SupervisorDashboard' })
  }
}

const getVisibleActions = (statusCode) => {
  switch (statusCode) {
    case 'NUEVA':
      return ['iniciar']
    case 'EN_PROCESO':
      return ['pausar', 'cerrar']
    case 'PAUSADA':
      return ['reanudar']
    default:
      return []
  }
}
</script>

<template>
  <div>
    <div class="task-detail-container">
      <h2 v-if="task" class="page-title-internal">
        {{ task.nombre }}
        <span class="patente-title">OT #{{ task.ot_id }}</span>
      </h2>
      <h2 v-else class="page-title-internal">Cargando Tarea...</h2>

      <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>

      <Transition name="fade-content" mode="out-in">
        <div v-if="isLoading" class="kanban-loading-overlay">
          <div class="spinner"></div>
          <span class="loading-text">Cargando tarea...</span>
        </div>

        <div v-else-if="task" class="task-content-grid">
          <div class="layout-column">
            <div class="info-card">
              <h2>Estado y Asignación</h2>
              <div class="info-grid">
                <div class="info-item">
                  <label>Estado Actual:</label>
                  <p>
                    <span :class="['status-tag', task.estado.code.toLowerCase()]">{{
                      task.estado.label
                    }}</span>
                  </p>
                </div>
                <div class="info-item">
                  <label>Responsable:</label>
                  <p>{{ task.responsable?.nombre || 'Sin asignar' }}</p>
                </div>
                <div class="info-item span-2">
                  <label>Vehículo:</label>
                  <p>
                    {{ task.vehiculo?.marca || '' }} {{ task.vehiculo?.modelo || '' }} ({{
                      task.vehiculo?.patente || 'N/A'
                    }})
                  </p>
                </div>
              </div>
              <button class="btn btn-secondary back-button" @click="navigateBackToOt">
                ← Volver al Listado de Tareas
              </button>
            </div>

            <div v-if="isEditable" class="actions-card">
              <h2>Acciones de Tarea</h2>
              <div class="action-buttons-group">
                <button
                  v-for="action in getVisibleActions(task.estado.code)"
                  :key="action"
                  :disabled="isProcessing"
                  :class="['btn', 'btn-action', action]"
                  @click="handleActionClick(action)"
                >
                  <svg
                    v-if="action === 'iniciar' || action === 'reanudar'"
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                  <svg
                    v-if="action === 'pausar'"
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
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
                  <svg
                    v-if="action === 'cerrar'"
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
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
                  {{ action.toUpperCase() }} TAREA
                </button>

                <button
                  :disabled="isProcessing || task?.estado?.code === 'PAUSADA'"
                  class="btn btn-action anular"
                  @click="openActionConfirm('anular')"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  ANULAR TAREA
                </button>
              </div>
            </div>
            <div v-else class="info-card">
              <h2>Tarea Finalizada</h2>
              <p class="description-text">
                Esta tarea ya ha sido marcada como {{ task.estado.label }} y no admite más acciones.
              </p>
            </div>
          </div>

          <div class="layout-column">
            <button
              type="button"
              class="module-card"
              :class="{ disabled: attachmentsLocked }"
              :disabled="attachmentsLocked"
              @click="
                !attachmentsLocked && router.push({ name: 'TaskEvidence', params: { taskId } })
              "
            >
              <span class="module-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path
                    d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"
                  />
                  <circle cx="12" cy="13" r="4" />
                </svg>
              </span>
              <div class="module-text">
                <h3>Evidencia</h3>
                <p>Ver y adjuntar fotos/PDFs ({{ task.evidencias_count || 0 }})</p>
              </div>
              <span class="module-arrow">→</span>
              <span v-if="attachmentsLocked" class="module-lock-note"
                >Disponible cuando la tarea esté activa.</span
              >
            </button>
            <button
              type="button"
              class="module-card"
              :class="{ disabled: attachmentsLocked }"
              :disabled="attachmentsLocked"
              @click="
                !attachmentsLocked && router.push({ name: 'TaskRepuestos', params: { taskId } })
              "
            >
              <span class="module-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M10 2h4l5 5v10l-5 5h-4l-5-5V7z" />
                  <path d="M10 2v20" />
                  <path d="M14 2v20" />
                </svg>
              </span>
              <div class="module-text">
                <h3>Repuestos</h3>
                <p>Ver y asignar repuestos ({{ task.repuestos_count || 0 }})</p>
              </div>
              <span class="module-arrow">→</span>
              <span v-if="attachmentsLocked" class="module-lock-note"
                >No disponible para tareas pausadas o cerradas.</span
              >
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <Transition name="modal-fade">
      <div v-if="showPauseModal" class="modal-overlay" @click.self="showPauseModal = false">
        <div class="confirm-modal">
          <div class="modal-icon PAUSADA">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <rect x="6" y="4" width="4" height="16"></rect>
              <rect x="14" y="4" width="4" height="16"></rect>
            </svg>
          </div>
          <h3>Pausar Tarea: Motivo Obligatorio</h3>
          <p>Indica el motivo de la pausa (Ej: Falta repuesto, Espera de Supervisor).</p>
          <textarea
            v-model="pauseReason"
            rows="4"
            placeholder="Escribe el motivo..."
            class="modal-textarea"
          ></textarea>
          <div class="modal-actions">
            <button type="button" class="modal-btn cancel" @click="showPauseModal = false">
              Cancelar
            </button>
            <button
              type="button"
              class="modal-btn confirm PAUSADA"
              :disabled="isProcessing || !pauseReason"
              @click="handlePause"
            >
              {{ isProcessing ? 'Procesando...' : 'Confirmar Pausa' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="modal-fade">
      <div v-if="showActionConfirm" class="modal-overlay" @click.self="showActionConfirm = false">
        <div class="confirm-modal">
          <div class="modal-icon" :class="actionConfirmConfig.variant">
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
          <h3>{{ actionConfirmConfig.title }}</h3>
          <p>{{ actionConfirmConfig.message }}</p>
          <div class="modal-actions">
            <button type="button" class="modal-btn cancel" @click="showActionConfirm = false">
              Cancelar
            </button>
            <button
              type="button"
              class="modal-btn confirm"
              :class="actionConfirmConfig.variant"
              :disabled="isProcessing"
              @click="executeActionConfirm"
            >
              {{ isProcessing ? 'Procesando...' : actionConfirmConfig.confirmText }}
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
.task-detail-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px;
  background:
    radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.18), transparent 55%),
    radial-gradient(circle at 85% 0%, rgba(16, 185, 129, 0.16), transparent 50%),
    rgba(6, 12, 25, 0.75);
  border-radius: 36px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 45px 90px rgba(2, 6, 23, 0.7);
}
.page-title-internal {
  font-size: 1.7rem;
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 28px;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}
.patente-title {
  font-family: 'Inter', monospace;
  background: rgba(59, 130, 246, 0.2);
  color: #cbd5f5;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 1.1rem;
  margin-left: 10px;
}
.task-content-grid {
  display: grid;
  grid-template-columns: 1.5fr 0.9fr;
  gap: 26px;
}
.layout-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.error-state {
  padding: 12px 15px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-weight: 600;
  border: 1px solid rgba(248, 113, 113, 0.35);
  color: #ffe4e6;
  background-color: rgba(248, 113, 113, 0.2);
}
.info-card,
.module-card,
.actions-card {
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 28px;
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.65);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
}
.info-card::before,
.module-card::before,
.actions-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(59, 130, 246, 0.15);
  pointer-events: none;
}
.info-card h2,
.actions-card h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #f8fafc;
  padding: 22px 24px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}
.description-text {
  padding: 0 24px 20px;
  margin: 0;
  font-size: 0.95rem;
  color: rgba(226, 232, 240, 0.85);
  line-height: 1.6;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px 24px 24px;
}
.info-item.span-2 {
  grid-column: span 2;
}
.info-item label {
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.85);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 5px;
  display: block;
}
.info-item p {
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: #f8fafc;
}
.back-button {
  width: 100%;
  margin: 0 20px 24px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.78);
  color: #e2e8f0;
  border-radius: 999px;
  padding: 10px 0;
  transition:
    border 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}
.back-button:hover {
  background: rgba(59, 130, 246, 0.22);
  border-color: rgba(59, 130, 246, 0.55);
  transform: translateY(-1px);
}
.btn {
  padding: 12px 22px;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.btn-primary {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0c111d;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 24px 48px rgba(14, 165, 233, 0.45);
}
.btn-secondary {
  background: rgba(15, 23, 42, 0.75);
  color: #e2e8f0;
  border: 1px solid rgba(148, 163, 184, 0.35);
}
.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.6);
}
.btn:disabled {
  background-color: rgba(148, 163, 184, 0.25);
  cursor: not-allowed;
  opacity: 0.7;
  box-shadow: none;
}
.action-buttons-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 20px;
}
.btn-action {
  padding: 12px 18px;
  font-size: 0.9rem;
  text-align: center;
  justify-content: center;
  border-radius: 16px;
  border: none;
  box-shadow: 0 18px 35px rgba(0, 0, 0, 0.35);
}
.btn-action svg {
  margin-right: 8px;
}
.btn-action:hover:not(:disabled) {
  transform: translateY(-2px);
}
.btn-action.iniciar,
.btn-action.reanudar {
  background: linear-gradient(120deg, #34d399, #10b981);
  color: #0c111d;
}
.btn-action.pausar {
  background: linear-gradient(120deg, #fde047, #f97316);
  color: #1f2937;
}
.btn-action.cerrar {
  background: linear-gradient(120deg, #22c55e, #16a34a);
  color: #062814;
}
.btn-action.anular {
  background: linear-gradient(120deg, #fb7185, #f472b6);
  color: #fff;
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
  background-color: rgba(148, 163, 184, 0.7);
}
.status-tag.en_proceso {
  background-color: #14b8a6;
}
.status-tag.pausada {
  background-color: #facc15;
  color: #1f2937;
}
.status-tag.hecha {
  background-color: #22c55e;
}
.status-tag.anulada {
  background-color: #f87171;
}
.module-card {
  border: none;
  padding: 22px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
  background: transparent;
}
.module-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 28px 60px rgba(2, 6, 23, 0.65);
}
.module-icon {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: rgba(59, 130, 246, 0.15);
  display: grid;
  place-items: center;
  color: #38bdf8;
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
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #f8fafc;
}
.module-text p {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.82);
}
.module-arrow {
  font-size: 1.4rem;
  color: rgba(148, 163, 184, 0.9);
  margin-left: auto;
  transition:
    transform 0.2s ease,
    color 0.2s ease;
}
.module-card:hover .module-arrow {
  transform: translateX(6px);
  color: #3b82f6;
}
.module-lock-note {
  font-size: 0.78rem;
  color: rgba(248, 250, 252, 0.65);
}
.module-card.disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.module-card.disabled:hover {
  transform: none;
  box-shadow: none;
}
.module-card.disabled .module-arrow {
  color: rgba(148, 163, 184, 0.55);
}
.module-card.disabled .module-icon {
  background: rgba(148, 163, 184, 0.2);
  color: rgba(226, 232, 240, 0.6);
}
.actions-card {
  padding: 28px;
}
.action-buttons-group .btn-action {
  flex: 1;
  min-width: 180px;
}
.kanban-loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.8));
  border-radius: 28px;
  box-shadow: 0 25px 60px rgba(2, 6, 23, 0.6);
  margin-top: 20px;
  border: 1px solid rgba(148, 163, 184, 0.25);
}
.loading-text {
  margin-top: 20px;
  font-size: 1.2rem;
  color: #f8fafc;
  font-weight: 500;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(148, 163, 184, 0.3);
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.fade-content-enter-active,
.fade-content-leave-active {
  transition: opacity 0.2s ease-out;
}
.fade-content-enter-from,
.fade-content-leave-to {
  opacity: 0;
}
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
.confirm-modal h2,
.confirm-modal h3 {
  margin: 0 0 8px;
  color: #f8fafc;
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
.modal-btn.confirm.pausar,
.modal-btn.confirm.PAUSADA {
  background: linear-gradient(120deg, #fde047, #fda92b);
  color: #0f172a;
}
.modal-btn.confirm.reanudar,
.modal-btn.confirm.ACTIVA {
  background: linear-gradient(120deg, #2dd4bf, #34d399);
  color: #042f2e;
}
.modal-btn.confirm.cerrar,
.modal-btn.confirm.CERRADA,
.modal-btn.confirm.anular {
  background: linear-gradient(120deg, #fb7185, #f472b6);
  color: #fff;
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
.modal-textarea {
  width: calc(100% - 48px);
  min-height: 140px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: rgba(11, 18, 32, 0.85);
  color: #f8fafc;
  padding: 12px 16px;
  resize: vertical;
  display: block;
  margin: 0 auto 20px;
}
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
  background: rgba(15, 23, 42, 0.88);
  border-radius: 12px;
  padding: 2.5rem 3rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.success-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0;
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
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}
.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}
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
@media (max-width: 900px) {
  .task-content-grid {
    grid-template-columns: 1fr;
  }
  .task-detail-container {
    padding: 20px;
  }
}
@media (max-width: 500px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
  .action-buttons-group .btn-action {
    min-width: unset;
    width: 100%;
  }
}
</style>
