<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(true)
const errorMsg = ref(null)
const kanbanData = ref({})

const API_BASE_URL = import.meta.env.VITE_API_URL

// Línea de acento en el header de cada columna
const statusColors = {
  NUEVA: 'var(--text-muted)',
  ACTIVA: '#14b8a6',
  EN_PROCESO: '#14b8a6',
  PAUSADA: '#facc15',
}

const fetchKanbanData = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/tablero/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok)
      throw new Error(`Error ${response.status}: Acceso denegado o datos no disponibles.`)
    kanbanData.value = await response.json()
    if (!kanbanData.value || typeof kanbanData.value !== 'object') kanbanData.value = {}
  } catch (error) {
    console.error('Kanban API Error:', error)
    errorMsg.value = `Fallo al cargar el tablero: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) fetchKanbanData()
  else router.push({ name: 'Login' })
})

// eslint-disable-next-line security/detect-object-injection
const getColumnColor = (status) => statusColors[status] || 'var(--text-muted)'
const formatStatusTitle = (status) =>
  status === 'EN_PROCESO' ? 'EN PROCESO' : status.toUpperCase().replace('_', ' ')
const viewOtDetail = (otId) => router.push({ name: 'OtDetail', params: { id: otId } })
const navigateToCreateOt = () => router.push({ name: 'OtCreate' })
</script>

<template>
  <section class="kanban-wrapper">
    <div class="hero-header">
      <div class="hero-copy">
        <p class="eyebrow">Monitoreo</p>
        <h1>Tablero de Órdenes</h1>
      </div>
      <button class="chip-button" :disabled="isLoading" @click="fetchKanbanData">
        ⟳ Recargar Tablero
      </button>
    </div>

    <div class="actions-bar">
      <button class="ghost-button" @click="router.push({ name: 'OtHistorial' })">
        Ver Historial (Cerradas)
      </button>

      <div class="actions-right">
        <button class="accent-button fleet" @click="router.push('/vehiculos')">
          Listado de vehículos
        </button>

        <button class="accent-button secondary" @click="router.push({ name: 'VehicleCreate' })">
          + Ingresar Vehículo
        </button>

        <button class="accent-button primary" @click="navigateToCreateOt">+ Nueva OT</button>
      </div>
    </div>

    <div v-if="isLoading" class="kanban-loading">
      <span class="spinner"></span>
      <p>Cargando tablero...</p>
    </div>

    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>

    <div v-else class="kanban-board">
      <div v-for="(ots, status) in kanbanData" :key="status" class="kanban-column">
        <header class="column-header" :style="{ '--col-accent': getColumnColor(status) }">
          <div>
            <p class="column-label">{{ formatStatusTitle(status) }}</p>
            <span class="column-count">{{ ots.length }}</span>
          </div>
        </header>
        <div class="column-body">
          <article v-for="ot in ots" :key="ot.id" class="ot-card" @click="viewOtDetail(ot.id)">
            <div class="card-head">
              <span class="pill">OT #{{ ot.id }}</span>
              <span class="pill ghost">{{ ot.vehiculo?.patente || 'N/A' }}</span>
            </div>
            <p class="description">{{ ot.descripcion || 'Sin descripción...' }}</p>
            <div class="card-footer">
              <span>{{ new Date(ot.fecha_apertura).toLocaleDateString('es-CL') }}</span>
              <span class="supervisor-tag">{{ ot.creado_por?.nombre.split(' ')[0] || 'N/A' }}</span>
            </div>
          </article>
          <p v-if="ots.length === 0" class="empty-column">No hay OTs en este estado.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.kanban-wrapper {
  padding: 18px 18px 72px;
  min-height: calc(100vh - 140px);
}

/* --- HERO HEADER --- */
.hero-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  padding: 28px 32px;
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.65);
  margin-bottom: 18px;
}
.hero-copy {
  flex: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 6px;
}
.hero-header h1 {
  margin: 0;
  font-size: 2rem;
  color: #f8fafc;
}
.hero-header p {
  margin: 8px 0 0;
  color: rgba(148, 163, 184, 0.9);
  font-size: 0.97rem;
}

.chip-button {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: rgba(15, 23, 42, 0.85);
  color: #e2e8f0;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.chip-button:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.18);
  border-color: rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}
.chip-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* --- ACTIONS BAR --- */
.actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.2);
  margin-bottom: 24px;
}
.actions-right {
  display: flex;
  gap: 12px;
}

.ghost-button,
.accent-button {
  border-radius: 16px;
  font-weight: 600;
  padding: 10px 18px;
  border: 1px solid transparent;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}

.ghost-button {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}
.ghost-button:hover {
  border-color: rgba(59, 130, 246, 0.45);
  transform: translateY(-1px);
}

.accent-button {
  color: #fff;
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.25);
}
.accent-button.primary {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0f172a;
}
.accent-button.secondary {
  background: linear-gradient(120deg, #60a5fa, #c084fc);
  color: #0f172a;
}

/* 🌟 ESTILO BOTÓN FLOTA (ROJO) 🌟 */
.accent-button.fleet {
  background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
  color: white;
  box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.accent-button:hover {
  transform: translateY(-2px) scale(1.01);
  filter: brightness(1.1);
}

/* --- LOADING & ERRORS --- */
.kanban-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 80px 0;
}
.kanban-loading p {
  margin: 0;
  color: #f8fafc;
}
.error-state {
  color: #f87171;
  text-align: center;
  padding: 40px;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 16px;
}

.spinner {
  display: inline-block;
  width: 66px;
  height: 66px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #22d3ee;
  border-right-color: rgba(59, 130, 246, 0.55);
  animation: spin 0.9s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* --- KANBAN BOARD --- */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  animation: fadeInUp 0.35s ease-out both;
}
.kanban-column {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 22px;
  padding: 18px 16px;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 45px rgba(2, 6, 23, 0.5);
}
.column-header {
  border-bottom: 3px solid var(--col-accent, #38bdf8);
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.column-label {
  margin: 0;
  color: #f8fafc;
  font-weight: 700;
  letter-spacing: 0.08em;
}
.column-count {
  margin-top: 4px;
  display: inline-flex;
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  font-size: 0.85rem;
  font-weight: 700;
}

.column-body {
  flex: 1;
  overflow-y: auto;
  padding-right: 6px;
  max-height: 520px;
  scrollbar-width: thin;
  scrollbar-color: #22d3ee33 transparent;
}
.column-body::-webkit-scrollbar {
  width: 8px;
}
.column-body::-webkit-scrollbar-track {
  background: transparent;
}
.column-body::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.35), rgba(59, 130, 246, 0.4));
  border-radius: 999px;
}

.ot-card {
  border-radius: 18px;
  padding: 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.75));
  box-shadow: 0 15px 30px rgba(2, 6, 23, 0.45);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    border 0.2s ease;
}
.ot-card:hover {
  transform: translateY(-3px);
  border-color: rgba(59, 130, 246, 0.4);
  box-shadow: 0 20px 40px rgba(14, 165, 233, 0.25);
}
.card-head {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  background: rgba(59, 130, 246, 0.25);
  color: #bae6fd;
}
.pill.ghost {
  background: rgba(148, 163, 184, 0.25);
  color: #e2e8f0;
}
.description {
  margin: 0 0 14px;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.95rem;
  line-height: 1.45;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  color: rgba(148, 163, 184, 0.9);
}
.supervisor-tag {
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.15);
  color: #6ee7b7;
  font-weight: 700;
}
.empty-column {
  text-align: center;
  color: rgba(148, 163, 184, 0.8);
  font-size: 0.9rem;
  margin-top: 20px;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 840px) {
  .hero-header,
  .actions-bar {
    flex-direction: column;
    align-items: flex-start;
  }
  .actions-right {
    width: 100%;
    flex-direction: column;
    gap: 10px;
  }
  .ghost-button,
  .accent-button {
    width: 100%;
    text-align: center;
  }
}
</style>
