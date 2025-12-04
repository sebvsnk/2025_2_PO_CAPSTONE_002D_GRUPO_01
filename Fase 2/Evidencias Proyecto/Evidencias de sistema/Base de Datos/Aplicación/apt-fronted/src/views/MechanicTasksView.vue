<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const tasks = ref([])
const isLoading = ref(true)
const errorMsg = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL

const fetchMyTasks = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const response = await fetch(`${API_BASE_URL}/mis-tareas/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      throw new Error(`Error ${response.status}: No se pudieron cargar tus tareas.`)
    }
    tasks.value = await response.json()
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchMyTasks()
  } else {
    router.push({ name: 'Login' })
  }
})

const viewTaskDetail = (taskId) => {
  router.push({ name: 'TaskDetail', params: { taskId } })
}
</script>

<template>
  <div class="tasks-list-container">
    <header class="tasks-list-header">
      <div class="header-copy">
        <p class="eyebrow">Área mecánica</p>
        <h1>Mis Tareas Pendientes</h1>
        <p>Revisa y ejecuta las tareas asignadas para las distintas OT activas.</p>
      </div>
      <button class="back-button" @click="router.push({ name: 'Dashboard' })">← Volver al Inicio</button>
    </header>

    <div v-if="isLoading" class="loading-state">
      <span class="spinner" />
      <p>Cargando tus tareas...</p>
    </div>
    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>

    <section v-else class="task-list-section">
      <div v-if="tasks.length > 0" class="section-heading">
        <h2>Listado de Tareas ({{ tasks.length }} activas)</h2>
        <p>Haz clic en cualquier tarjeta para abrir el detalle y gestionar la actividad.</p>
      </div>

      <TransitionGroup v-if="tasks.length > 0" name="task-card" tag="div" class="task-card-grid">
        <article v-for="task in tasks" :key="task.id" class="task-card" @click="viewTaskDetail(task.id)">
          <div class="task-card-header">
            <span class="task-id">Tarea #{{ task.id }}</span>
            <span :class="['status-tag', task.estado.code.toLowerCase()]">{{ task.estado.label }}</span>
          </div>
          <div class="task-card-body">
            <h3>{{ task.nombre }}</h3>
            <p class="vehicle-tag">
              <svg viewBox="0 0 24 24">
                <path d="M3 16V8h11l4 5v3" />
                <path d="M7 16v2" />
                <path d="M17 16v2" />
                <circle cx="7" cy="19" r="2" />
                <circle cx="17" cy="19" r="2" />
              </svg>
              OT #{{ task.ot_id }} · {{ task.vehiculo?.patente || 'Sin patente' }}
            </p>
            <p class="meta">
              Última actualización:
              {{
                task.updated_at
                  ? new Date(task.updated_at).toLocaleString()
                  : 'Sin actualización'
              }}
            </p>
          </div>
          <div class="task-card-footer">
            <span class="cta-hint">Ver detalle</span>
            <button class="detail-button">Gestionar</button>
          </div>
        </article>
      </TransitionGroup>

      <div v-else class="empty-state">
        <h3>Sin pendientes 🎉</h3>
        <p>No tienes tareas activas (Nuevas, En Proceso o Pausadas) asignadas a tu nombre.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.tasks-list-container {
  max-width: 1200px;
  margin: 30px auto 80px;
  padding: 24px;
}
.tasks-list-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding: 18px 20px;
  margin-bottom: 32px;
  background: linear-gradient(135deg, rgba(12, 18, 36, 0.9), rgba(9, 14, 28, 0.82));
  border: 1px solid rgba(120, 172, 255, 0.28);
  border-radius: 18px;
  box-shadow:
    0 18px 40px rgba(0, 0, 0, 0.45),
    0 0 40px rgba(34, 211, 238, 0.12);
  backdrop-filter: blur(12px);
}
.header-copy {
  max-width: 720px;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.25em;
  color: rgba(148, 196, 255, 0.8);
  margin: 0 0 4px 0;
}
.header-copy h1 {
  margin: 0;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  color: var(--text-strong);
}
.header-copy p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.back-button {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(34, 211, 238, 0.18));
  border: 1px solid rgba(120, 172, 255, 0.35);
  padding: 10px 18px;
  border-radius: 999px;
  cursor: pointer;
  color: #dbeafe;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
}
.back-button:hover {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.25), rgba(34, 211, 238, 0.25));
  border-color: rgba(120, 172, 255, 0.55);
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(34, 211, 238, 0.25);
}
.section-heading h2 {
  margin: 0;
  color: var(--text-strong);
}
.section-heading p {
  margin: 6px 0 18px;
  color: var(--text-muted);
}
.task-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}
.task-card {
  background: linear-gradient(145deg, rgba(10, 15, 28, 0.92), rgba(8, 13, 24, 0.86));
  border-radius: 18px;
  border: 1px solid rgba(120, 172, 255, 0.24);
  box-shadow:
    0 20px 45px rgba(2, 6, 23, 0.6),
    0 0 30px rgba(34, 211, 238, 0.08);
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
}
.task-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 25px 50px rgba(2, 6, 23, 0.7),
    0 0 40px rgba(34, 211, 238, 0.14);
  border-color: rgba(94, 155, 255, 0.45);
}
.task-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 8px;
}
.task-id {
  font-weight: 700;
  color: #a5f3fc;
  letter-spacing: 0.03em;
}
.task-card-body {
  padding: 0 20px 20px;
}
.task-card-body h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  color: var(--text-strong);
}
.vehicle-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0 0 6px;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.vehicle-tag svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
  stroke-width: 1.6;
  fill: none;
}
.meta {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(148, 163, 184, 0.7);
}
.task-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(148, 163, 184, 0.06);
  border-bottom-left-radius: 18px;
  border-bottom-right-radius: 18px;
}
.cta-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.detail-button {
  background: linear-gradient(135deg, #1e3a8a, #2563eb 45%, #22d3ee 100%);
  border: none;
  color: #f8fafc;
  font-weight: 700;
  border-radius: 999px;
  padding: 6px 18px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.detail-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(34, 197, 235, 0.25);
}
.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  color: white;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}
.status-tag.nueva {
  background-color: rgba(148, 163, 184, 0.4);
}
.status-tag.en_proceso {
  background-color: #14b8a6;
}
.status-tag.pausada {
  background-color: #facc15;
  color: var(--surface-muted);
}
.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 60px 40px;
  font-size: 18px;
  color: var(--text-base);
  border: 1px solid rgba(120, 172, 255, 0.22);
  border-radius: 18px;
  background: linear-gradient(145deg, rgba(10, 15, 28, 0.9), rgba(8, 13, 24, 0.82));
  box-shadow:
    0 22px 50px rgba(0, 0, 0, 0.45),
    0 0 40px rgba(34, 211, 238, 0.12);
  backdrop-filter: blur(12px);
  position: relative;
  overflow: hidden;
}
.loading-state::before,
.empty-state::before,
.error-state::before {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  top: -60px;
  right: -40px;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.22), transparent 65%);
  filter: blur(28px);
  opacity: 0.9;
  pointer-events: none;
}
.loading-state .spinner {
  position: relative;
  display: inline-block;
  box-sizing: border-box;
  width: 66px;
  height: 66px;
  margin: 0 auto 18px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #22d3ee;
  border-right-color: rgba(59, 130, 246, 0.55);
  border-left-color: rgba(59, 130, 246, 0.18);
  border-bottom-color: rgba(34, 211, 238, 0.12);
  animation: aurora-spin 0.9s linear infinite, pulseGlow 2s ease-in-out infinite;
  box-shadow:
    0 0 18px rgba(34, 211, 238, 0.35),
    0 0 32px rgba(59, 130, 246, 0.22);
}
.loading-state .spinner::after {
  content: '';
  position: absolute;
  inset: 14px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0));
  filter: blur(2px);
}
.error-state {
  color: #f87171;
}
.empty-state h3 {
  margin-bottom: 8px;
  color: var(--text-strong);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
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

.task-card-enter-from,
.task-card-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
.task-card-enter-active,
.task-card-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
</style>
