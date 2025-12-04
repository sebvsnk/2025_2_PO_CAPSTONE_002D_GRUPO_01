<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const closedOts = ref([])
const isLoading = ref(true)
const errorMsg = ref(null)
const pageSize = ref(10)
const totalOts = ref(0)
const currentPage = ref(1)

// Filtros
const searchPatente = ref('')
const searchOtId = ref('')
const searchFechaCierre = ref('')

const API_BASE_URL = import.meta.env.VITE_API_URL

// 1. Cargar Historial (Paginado desde el Backend)
const fetchHistory = async () => {
  isLoading.value = true
  errorMsg.value = null

  // Construir URL con filtros
  const params = new URLSearchParams({
    page: currentPage.value,
    page_size: pageSize.value,
  })

  // Nota: Para que el filtro funcione 100% real en backend, tu API debe soportarlo.
  // Si tu API actual solo pagina y no filtra, estos params se ignoran y filtrará el front.
  // Asumiremos filtrado local para la demo si el backend no tiene filtros configurados aún.

  const url = `${API_BASE_URL}/ot/historial/?${params.toString()}`

  try {
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    if (!response.ok) {
      throw new Error(`Error ${response.status}: No se pudo cargar el historial.`)
    }

    const data = await response.json()

    if (data && Array.isArray(data.results)) {
      closedOts.value = data.results
      totalOts.value = data.count
    } else {
      closedOts.value = []
      totalOts.value = 0
    }
  } catch (error) {
    errorMsg.value = error.message
    closedOts.value = []
    totalOts.value = 0
  } finally {
    // Pequeño delay para suavizar la transición
    setTimeout(() => {
      isLoading.value = false
    }, 300)
  }
}

// 2. Filtrado en Cliente (Si el backend solo pagina "todo")
// Esto combina los resultados de la página actual con los filtros visuales.
const filteredOts = computed(() => {
  return closedOts.value.filter((ot) => {
    const matchPatente =
      !searchPatente.value ||
      (ot.vehiculo?.patente || '').toLowerCase().includes(searchPatente.value.toLowerCase())

    const matchId = !searchOtId.value || String(ot.id || '').includes(searchOtId.value)

    const matchFecha =
      !searchFechaCierre.value || (ot.fecha_cierre || '').startsWith(searchFechaCierre.value)

    return matchPatente && matchId && matchFecha
  })
})

const totalPages = computed(() => {
  if (totalOts.value === 0) return 1
  return Math.ceil(totalOts.value / pageSize.value)
})

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value && page !== currentPage.value) {
    currentPage.value = page
    fetchHistory()
  }
}

// Resetear página al cambiar filtros (si estuviera conectado a backend filtering)
watch([searchPatente, searchOtId, searchFechaCierre], () => {
  // Si el filtro es local, no necesitamos recargar la API, pero si fuera backend sí.
})

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchHistory()
  } else {
    router.push({ name: 'Login' })
  }
})

const viewOtDetail = (otId) => {
  router.push({ name: 'OtDetail', params: { id: otId } })
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('es-CL', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <div class="historial-wrapper">
    <header class="page-header">
      <button class="back-link" @click="router.push({ name: 'SupervisorDashboard' })">
        &larr; Volver al Tablero
      </button>
      <div class="header-content">
        <p class="eyebrow">ARCHIVO</p>
        <h1>Historial de OTs</h1>
      </div>
      <p class="hero-desc">Consulta y auditoría de órdenes cerradas o anuladas.</p>
    </header>

    <div class="glass-panel">
      <div class="toolbar">
        <div class="filters-row">
          <div class="search-input-group">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              class="icon"
            >
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
            <input v-model="searchPatente" placeholder="Buscar patente..." />
          </div>
          <div class="search-input-group small">
            <span class="prefix">#</span>
            <input v-model="searchOtId" placeholder="N° OT" type="number" />
          </div>
          <div class="search-input-group date">
            <input v-model="searchFechaCierre" type="date" />
          </div>
        </div>

        <div v-if="!isLoading" class="pagination-compact">
          <button :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">&lt;</button>
          <span>{{ currentPage }} / {{ totalPages }}</span>
          <button :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
            &gt;
          </button>
        </div>
      </div>

      <Transition name="fade">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner-aurora"></div>
          <p>Recuperando archivo...</p>
        </div>
      </Transition>

      <div v-if="errorMsg" class="state-card error-card">
        {{ errorMsg }}
      </div>

      <Transition name="list-slide" mode="out-in">
        <div v-if="!isLoading && filteredOts.length > 0" :key="currentPage">
          <div class="history-scroll aurora-scroll">
            <div class="cards-grid">
              <article
                v-for="ot in filteredOts"
                :key="ot.id"
                class="history-card"
                @click="viewOtDetail(ot.id)"
              >
                <div class="card-status-line" :class="ot.estado.code.toLowerCase()"></div>

                <div class="card-main">
                  <div class="card-header">
                    <div class="ot-meta">
                      <span class="ot-badge">OT #{{ ot.id }}</span>
                      <span class="patente">{{ ot.vehiculo?.patente || 'N/A' }}</span>
                    </div>
                    <span class="status-pill" :class="ot.estado.code.toLowerCase()">
                      {{ ot.estado.label }}
                    </span>
                  </div>

                  <h3 class="card-desc">
                    {{ ot.descripcion || 'Sin descripción disponible.' }}
                  </h3>

                  <div class="card-footer">
                    <div class="footer-item">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                        <line x1="16" y1="2" x2="16" y2="6" />
                        <line x1="8" y1="2" x2="8" y2="6" />
                        <line x1="3" y1="10" x2="21" y2="10" />
                      </svg>
                      <span>Cierre: {{ formatDate(ot.fecha_cierre) }}</span>
                    </div>
                    <div class="footer-item">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M9 11l3 3L22 4" />
                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                      </svg>
                      <span>{{ ot.tareas_count }} Tareas</span>
                    </div>

                    <button class="action-link">Ver Detalle →</button>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div v-else-if="!isLoading" class="empty-state">
          <div class="empty-icon">🗄️</div>
          <h3>Sin registros</h3>
          <p>No se encontraron órdenes cerradas o anuladas con los filtros actuales.</p>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
/* Layout */
.historial-wrapper {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  color: #e2e8f0;
  min-height: 90vh;
}

/* Hero Header */
.page-header {
  margin-bottom: 24px;
  padding-left: 10px;
}
/* --- Botón Volver Estilo Aurora Glass --- */
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  margin-bottom: 16px;

  /* Estilo Glass Base */
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 99px; /* Forma de píldora */

  /* Texto */
  color: #cbd5e1;
  font-size: 0.9rem;
  font-weight: 600;
  letter-spacing: 0.02em;

  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Efecto Hover (Brillo Aurora) */
.back-link:hover {
  background: rgba(56, 189, 248, 0.15); /* Fondo azul suave */
  border-color: #38bdf8; /* Borde Cyan brillante */
  color: #fff; /* Texto blanco */
  transform: translateX(-4px); /* Pequeño desplazamiento a la izquierda */
  box-shadow:
    0 0 15px rgba(56, 189, 248, 0.25),
    /* Resplandor externo */ inset 0 0 10px rgba(56, 189, 248, 0.05); /* Resplandor interno */
}

/* Efecto Click */
.back-link:active {
  transform: translateX(-2px) scale(0.98);
}

.eyebrow {
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: #38bdf8;
  font-weight: 700;
  margin-bottom: 4px;
}
h1 {
  font-size: 2.2rem;
  margin: 0 0 6px;
  color: #f8fafc;
}
.hero-desc {
  color: #94a3b8;
  font-size: 1rem;
  margin: 0;
}

/* Glass Panel Container */
.glass-panel {
  background: rgba(15, 23, 42, 0.65);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  min-height: 500px;
  display: flex;
  flex-direction: column;
}

/* Toolbar (Filtros + Paginación) */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  padding-bottom: 20px;
}

.filters-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.search-input-group {
  display: flex;
  align-items: center;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 10px;
  padding: 8px 12px;
  transition: all 0.2s;
}
.search-input-group:focus-within {
  border-color: #38bdf8;
  background: rgba(30, 41, 59, 0.9);
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
}
.search-input-group .icon,
.search-input-group .prefix {
  color: #64748b;
  margin-right: 8px;
}
.search-input-group input {
  background: transparent;
  border: none;
  color: #f1f5f9;
  outline: none;
  font-size: 0.9rem;
  width: 140px;
}
.search-input-group.small input {
  width: 60px;
}
.search-input-group.date input {
  width: auto;
  color-scheme: dark;
}

.pagination-compact {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(15, 23, 42, 0.4);
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.15);
}
.pagination-compact button {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: #cbd5e1;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 700;
}
.pagination-compact button:hover:not(:disabled) {
  background: #38bdf8;
  color: #0f172a;
}
.pagination-compact button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.pagination-compact span {
  font-size: 0.85rem;
  color: #94a3b8;
  font-family: monospace;
}

/* Cards Grid */
.cards-grid {
  display: grid;
  gap: 16px;
}

/* Tarjeta Individual */
.history-card {
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.6));
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
}
.history-card:hover {
  transform: translateY(-2px);
  background: rgba(30, 41, 59, 0.7);
  border-color: rgba(56, 189, 248, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.card-status-line {
  width: 4px;
  height: 100%;
  background: #64748b;
}
.card-status-line.cerrada {
  background: #10b981;
} /* Verde */
.card-status-line.anulada {
  background: #f43f5e;
} /* Rojo */

.card-main {
  flex: 1;
  padding: 16px 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.ot-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}
.ot-badge {
  font-family: monospace;
  font-weight: 700;
  color: #38bdf8;
  font-size: 0.95rem;
}
.patente {
  background: rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #e2e8f0;
  font-weight: 600;
}

.status-pill {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 99px;
  letter-spacing: 0.05em;
}
.status-pill.cerrada {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.status-pill.anulada {
  background: rgba(244, 63, 94, 0.15);
  color: #fb7185;
  border: 1px solid rgba(244, 63, 94, 0.3);
}

.card-desc {
  margin: 0 0 16px 0;
  font-size: 0.95rem;
  color: #cbd5e1;
  font-weight: 400;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 0.85rem;
  color: #64748b;
}
.footer-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.action-link {
  margin-left: auto;
  background: none;
  border: none;
  color: #38bdf8;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}
.history-card:hover .action-link {
  text-decoration: underline;
}

/* States */
.loading-state {
  padding: 60px;
  text-align: center;
}
.spinner-aurora {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: #22d3ee;
  border-bottom-color: rgba(59, 130, 246, 0.2);
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #64748b;
}
.empty-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.list-slide-enter-active {
  transition: all 0.4s ease-out;
}
.list-slide-leave-active {
  transition: all 0.3s ease-in;
}
.list-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}
.list-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* --- Área de Scroll --- */
.history-scroll {
  max-height: 600px; /* Altura máxima antes de hacer scroll */
  overflow-y: auto; /* Activar scroll vertical */
  padding-right: 8px; /* Espacio para que el contenido no toque la barra */
  margin-right: -4px; /* Ajuste visual */
}

/* --- Estilo Aurora Scrollbar --- */
.aurora-scroll::-webkit-scrollbar {
  width: 8px;
}

.aurora-scroll::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.3); /* Fondo oscuro sutil */
  border-radius: 4px;
}

.aurora-scroll::-webkit-scrollbar-thumb {
  /* Gradiente Vertical: Cyan -> Azul -> Violeta */
  background: linear-gradient(to bottom, #22d3ee, #3b82f6, #8b5cf6);
  border-radius: 10px;
  border: 2px solid rgba(15, 23, 42, 0.8); /* Borde oscuro para efecto 'flotante' */
  background-clip: padding-box;
}

.aurora-scroll::-webkit-scrollbar-thumb:hover {
  border: 1px solid rgba(15, 23, 42, 0.8); /* Se hace un poco más grueso al pasar el mouse */
  background: linear-gradient(to bottom, #67e8f9, #60a5fa, #a78bfa); /* Colores más brillantes */
}
@media (max-width: 600px) {
  .toolbar {
    flex-direction: column;
    align-items: flex-start;
  }
  .filters-row {
    flex-direction: column;
    width: 100%;
  }
  .search-input-group {
    width: 100%;
  }
  .search-input-group input {
    width: 100%;
  }
  .pagination-compact {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
