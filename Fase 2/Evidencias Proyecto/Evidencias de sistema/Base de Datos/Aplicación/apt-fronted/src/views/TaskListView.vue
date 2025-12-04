<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const otId = route.params.otId
const tasks = ref([])
const responsables = ref([])
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMsg = ref(null)

// --- 1. Refs para Animación de Éxito ---
const showSuccessCheck = ref(false)
const successCheckText = ref('')

const newTaskForm = ref({
  nombre: '',
  responsable: null,
})

const API_BASE_URL = import.meta.env.VITE_API_URL

// --- 2. Función para Animación de Éxito ---
const triggerSuccessAnimation = (message) => {
  successCheckText.value = message
  showSuccessCheck.value = true
  setTimeout(() => {
    showSuccessCheck.value = false
    successCheckText.value = ''
  }, 2000)
}

// --- FUNCIONES DE CARGA ---
const fetchTasks = async () => {
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/ot/${otId}/tareas/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Fallo al cargar tareas.`)
    }
    tasks.value = await response.json()
  } catch (error) {
    errorMsg.value = `Fallo al cargar las tareas: ${error.message}`
  }
}

const fetchResponsables = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/admin/usuarios/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (response.ok) {
      const allUsers = await response.json()
      responsables.value = allUsers.filter((u) => u.rol === 'MECANICO')
    }
  } catch (error) {
    console.error('Error cargando responsables:', error)
  }
}

const handleCreateTask = async () => {
  isSubmitting.value = true
  errorMsg.value = null

  if (!newTaskForm.value.nombre || !newTaskForm.value.responsable) {
    errorMsg.value = 'Debe asignar un nombre y un responsable a la tarea.'
    isSubmitting.value = false
    return
  }

  const payload = {
    nombre: newTaskForm.value.nombre,
    responsable: newTaskForm.value.responsable,
  }

  try {
    const url = `${API_BASE_URL}/ot/${otId}/tareas/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()
    if (!response.ok) {
      errorMsg.value = data.detail || 'Fallo al crear la tarea.'
      throw new Error('Fallo al crear tarea.')
    }

    triggerSuccessAnimation(`Tarea #${data.id} creada`)
    newTaskForm.value.nombre = ''
    newTaskForm.value.responsable = null

    await fetchTasks()
  } catch (error) {
    if (!errorMsg.value) {
      errorMsg.value = `Error: ${error.message}`
    }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login' })
    return
  }
  isLoading.value = true
  await Promise.all([fetchTasks(), fetchResponsables()])
  isLoading.value = false
})

const viewTaskDetail = (taskId) => {
  router.push({ name: 'TaskDetail', params: { taskId: taskId } })
}

const goBackToOtDetail = () => {
  if (otId) {
    router.push({ name: 'OtDetail', params: { id: otId } })
  } else {
    router.back()
  }
}
</script>

<template>
  <div class="tasks-list-container">
    <div class="tasks-header">
      <button class="back-button" @click="goBackToOtDetail">← Volver a la OT</button>
      <div class="header-copy">
        <h1>Gestión de Tareas</h1>
        <p>Asigna nuevas tareas o revisa el avance de la OT seleccionada.</p>
      </div>
    </div>

    <form class="quick-create-form card" @submit.prevent="handleCreateTask">
      <h2>Asignar Nueva Tarea</h2>
      <div class="form-grid">
        <div class="form-group">
          <label for="task-name">Nombre de la Tarea</label>
          <input
            id="task-name"
            v-model="newTaskForm.nombre"
            type="text"
            placeholder="Ej: Cambio de Frenos Delanteros"
            required
            :disabled="isSubmitting"
          />
        </div>
        <div class="form-group">
          <label for="task-responsable">Asignar a Mecánico</label>
          <select
            id="task-responsable"
            v-model="newTaskForm.responsable"
            required
            :disabled="isSubmitting"
          >
            <option :value="null" disabled>Selecciona un mecánico...</option>
            <option v-for="r in responsables" :key="r.id" :value="r.id">
              {{ r.nombre }}
            </option>
          </select>
        </div>
        <button type="submit" class="btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? 'Asignando...' : 'Asignar Tarea' }}
        </button>
      </div>
      <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
    </form>

    <div v-if="isLoading" class="kanban-loading-overlay">
      <div class="spinner"></div>
      <span class="loading-text">Cargando tareas y responsables...</span>
    </div>

    <div v-else class="task-list-section">
      <h2 class="section-title">Listado de Tareas ({{ tasks.length }})</h2>

      <TransitionGroup v-if="tasks.length > 0" name="card-fade" tag="div" class="task-grid">
        <article
          v-for="task in tasks"
          :key="task.id"
          class="task-card card"
          @click="viewTaskDetail(task.id)"
        >
          <div class="task-card-header">
            <span class="task-id">Tarea #{{ task.id }}</span>
            <span :class="['status-tag', task.estado.code.toLowerCase()]">{{
              task.estado.label
            }}</span>
          </div>
          <div class="task-card-body">
            <h3>{{ task.nombre }}</h3>
            <p>
              <strong>Mecánico:</strong>
              {{ task.responsable ? task.responsable.nombre : 'Sin asignar' }}
            </p>

            <div v-if="task.motivo_pausa_actual" class="pause-info">
              <span class="icon">⏸</span>
              <span> <strong>Pausada:</strong> "{{ task.motivo_pausa_actual }}" </span>
            </div>
          </div>
          <div class="task-card-footer">
            <button class="detail-button">Administrar Tarea</button>
          </div>
        </article>
      </TransitionGroup>

      <div v-else class="empty-state">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <h3>No hay tareas</h3>
        <p>Aún no se han asignado tareas para esta Orden de Trabajo.</p>
      </div>
    </div>

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
/* --- (Estilos sin cambios) --- */
.tasks-list-container {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  padding: 6px;
}

.tasks-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.header-copy h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #f8fafc;
}
.header-copy p {
  margin: 4px 0 0;
  color: rgba(148, 163, 184, 0.9);
}
.back-button {
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
  padding: 10px 18px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition:
    border 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}
.back-button:hover {
  background: rgba(59, 130, 246, 0.18);
  border-color: rgba(59, 130, 246, 0.65);
  transform: translateY(-1px);
}

.card {
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.82));
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 26px;
  box-shadow: 0 25px 60px rgba(2, 6, 23, 0.65);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
}
.card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(59, 130, 246, 0.12);
  pointer-events: none;
}
.quick-create-form {
  padding: 28px 32px;
  margin-bottom: 34px;
}
.quick-create-form h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-strong);
  margin-top: 0;
  margin-bottom: 20px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 15px;
  align-items: flex-end;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.form-group label {
  font-weight: 600;
  font-size: 0.85rem;
  margin-bottom: 5px;
  color: var(--text-base);
}
.form-group input,
.form-group select {
  padding: 12px 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 14px;
  font-size: 0.95rem;
  background-color: rgba(9, 15, 28, 0.9);
  color: #f8fafc;
  transition:
    border 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}
.form-group input:focus,
.form-group select:focus {
  border-color: rgba(56, 189, 248, 0.9);
  box-shadow: 0 12px 24px rgba(14, 165, 233, 0.25);
  outline: none;
  transform: translateY(-1px);
}
.btn-primary {
  padding: 12px 26px;
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0c111d;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 24px 48px rgba(14, 165, 233, 0.45);
}
.btn-primary:disabled {
  background-color: rgba(148, 163, 184, 0.25);
  cursor: not-allowed;
}
.section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-base);
  margin-bottom: 20px;
}
.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}
.task-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  border-radius: 24px;
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.78));
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 22px 50px rgba(2, 6, 23, 0.55);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
  transition:
    transform 0.25s ease,
    box-shadow 0.25s ease;
}
.task-card::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.22), transparent 65%);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.task-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 28px 65px rgba(2, 6, 23, 0.7);
}
.task-card:hover::after {
  opacity: 1;
}
.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}
.task-id {
  font-size: 0.9rem;
  font-weight: 600;
  color: rgba(148, 163, 184, 0.85);
}
.task-card-body {
  padding: 20px;
  flex-grow: 1;
}
.task-card-body h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: #f8fafc;
  margin: 0 0 10px 0;
}
.task-card-body p {
  margin: 0;
  color: rgba(226, 232, 240, 0.9);
}
.task-card-footer {
  padding: 14px 20px;
  background-color: rgba(12, 19, 33, 0.8);
  border-top: 1px solid rgba(148, 163, 184, 0.25);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.detail-button {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0c111d;
  border: none;
  padding: 8px 16px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.85rem;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.35);
}
.detail-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.45);
}
.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 700;
  color: white;
}
.status-tag.nueva {
  background-color: var(--text-muted);
}
.status-tag.en_proceso {
  background-color: #14b8a6;
}
.status-tag.pausada {
  background-color: #facc15;
  color: var(--text-base);
}
.status-tag.hecha {
  background-color: #22c55e;
}
.status-tag.anulada {
  background-color: #f87171;
}
.error-message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
  font-weight: 600;
  color: #721c24;
  background-color: rgba(248, 113, 113, 0.18);
}
.empty-state {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: rgba(226, 232, 240, 0.85);
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.75));
  border: 1px dashed rgba(148, 163, 184, 0.4);
  border-radius: 20px;
  margin-top: 20px;
}

/* --- Círculo de Carga (Spinner) --- */
.kanban-loading-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px; /* Altura mínima para centrar el spinner */
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.8));
  border-radius: 28px;
  box-shadow: 0 25px 60px rgba(2, 6, 23, 0.6);
  margin-top: 20px;
  border: 1px solid rgba(148, 163, 184, 0.25);
}
.loading-text {
  margin-top: 20px;
  font-size: 1.2rem;
  color: var(--text-strong);
  font-weight: 500;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #e0e0e0;
  border-top-color: #3b82f6; /* Color primario */
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
/* Ocultamos el esqueleto anterior si aún existe el CSS */
.skeleton-loader {
  display: none;
}

/* --- Overlay de Éxito (Checkmark animado) --- */
.success-overlay {
  position: fixed; /* O fixed */
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
  animation: modal-pop 0.3s ease-out;
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
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@keyframes modal-pop {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
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

.pause-info {
  margin-top: 12px;
  background: rgba(250, 204, 21, 0.15); /* Fondo amarillo translúcido */
  border: 1px solid rgba(250, 204, 21, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
  color: #fef08a; /* Texto amarillo claro */
  font-size: 0.9rem;
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.pause-info .icon {
  font-size: 1.1rem;
}

.pause-info strong {
  color: #facc15; /* Amarillo más intenso para el título */
  font-weight: 700;
}
</style>
