<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL

// Estado
const vehicles = ref([])
const isLoading = ref(true)
const searchTerm = ref('')
const showUnassignedOnly = ref(false)
const currentPage = ref(1)
const pageSize = 10

// Carga de datos
const loadVehicles = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_URL}/vehiculos/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (res.ok) {
      vehicles.value = await res.json()
    }
  } catch (error) {
    console.error('Error cargando vehículos:', error)
  } finally {
    // Pequeño delay artificial para que la transición de entrada se aprecie
    setTimeout(() => {
      isLoading.value = false
    }, 400)
  }
}

// Filtrado (Client-side)
const filteredVehicles = computed(() => {
  let filtered = vehicles.value

  if (showUnassignedOnly.value) {
    filtered = filtered.filter((v) => !v.chofer)
  }

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(
      (v) =>
        v.patente.toLowerCase().includes(term) ||
        (v.marca || '').toLowerCase().includes(term) ||
        (v.modelo || '').toLowerCase().includes(term) ||
        (v.chofer?.nombre || '').toLowerCase().includes(term),
    )
  }
  return filtered
})

// Paginación
const totalPages = computed(() => Math.max(1, Math.ceil(filteredVehicles.value.length / pageSize)))

const paginatedVehicles = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredVehicles.value.slice(start, start + pageSize)
})

// Watchers para resetear página al filtrar
watch([searchTerm, showUnassignedOnly], () => {
  currentPage.value = 1
})

// Navegación
const goToDetail = (id) => {
  router.push(`/vehiculo/${id}/editar`)
}

onMounted(() => {
  loadVehicles()
})
</script>

<template>
  <section class="vehicle-list-wrapper">
    <div class="hero-header">
      <div class="hero-content">
        <button class="back-link" @click="router.push({ name: 'SupervisorDashboard' })">
          &larr; Volver al Tablero
        </button>
        <div class="title-stack">
          <p class="eyebrow">FLOTA</p>
          <h1>Gestión de Vehículos</h1>
        </div>
        <p class="hero-desc">Monitoreo, asignación de choferes y control de patentes.</p>

        <div v-if="!isLoading" class="hero-stats">
          <span class="stat-pill">
            <span class="dot"></span> {{ filteredVehicles.length }} vehículos listados
          </span>
        </div>
      </div>

      <button class="cta-button" @click="router.push('/vehiculo/ingresar')">
        <span class="icon">+</span> Nuevo Vehículo
      </button>
    </div>

    <div class="filters-bar glass-panel">
      <div class="search-wrapper">
        <svg
          class="search-icon"
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
          <circle cx="11" cy="11" r="8" />
          <path d="m21 21-4.3-4.3" />
        </svg>
        <input
          v-model="searchTerm"
          placeholder="Buscar patente, marca, chofer..."
          type="text"
          class="search-input"
        />
      </div>

      <label class="toggle-filter" :class="{ active: showUnassignedOnly }">
        <input v-model="showUnassignedOnly" type="checkbox" />
        <span class="toggle-track">
          <span class="toggle-thumb"></span>
        </span>
        <span class="toggle-label">Sin Chofer</span>
      </label>
    </div>

    <Transition name="page-slide" mode="out-in">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner-aurora"></div>
        <p>Cargando flota...</p>
      </div>
      <div v-else class="list-container glass-panel">
        <div v-if="filteredVehicles.length > 0" class="table-header-row">
          <span class="col-head">Patente</span>
          <span class="col-head">Vehículo</span>
          <span class="col-head">Chofer Asignado</span>
          <span class="col-head align-right">Acciones</span>
        </div>

        <Transition name="page-slide" mode="out-in">
          <div :key="currentPage" class="list-content">
            <div
              v-for="v in paginatedVehicles"
              :key="v.id"
              class="vehicle-row"
              @click="goToDetail(v.id)"
            >
              <div class="col patente-col">
                <div class="patente-badge">{{ v.patente }}</div>
              </div>

              <div class="col info-col">
                <p class="model">{{ v.marca }} {{ v.modelo }}</p>
                <p class="date">Reg: {{ new Date(v.creado_en).toLocaleDateString() }}</p>
              </div>

              <div class="col driver-col">
                <div v-if="v.chofer" class="driver-pill assigned">
                  <span class="avatar-dot">{{ v.chofer.nombre.charAt(0) }}</span>
                  <div class="driver-info">
                    <span class="name">{{ v.chofer.nombre.split(' ')[0] }}</span>
                    <span class="rut">{{ v.chofer.rut }}</span>
                  </div>
                </div>
                <div v-else class="driver-pill unassigned">
                  <span class="dot-status"></span> Sin Asignar
                </div>
              </div>

              <div class="col action-col">
                <button class="action-btn" @click.stop="goToDetail(v.id)">Gestionar</button>
              </div>
            </div>

            <div v-if="filteredVehicles.length === 0" class="empty-state">
              <div class="empty-icon">🔍</div>
              <h3>No se encontraron vehículos</h3>
              <p>Intenta cambiar los filtros de búsqueda.</p>
            </div>
          </div>
        </Transition>

        <div v-if="totalPages > 1" class="pagination-footer">
          <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
            &larr; Anterior
          </button>
          <span class="page-info"
            >Página <strong>{{ currentPage }}</strong> de {{ totalPages }}</span
          >
          <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
            Siguiente &rarr;
          </button>
        </div>
      </div>
    </Transition>
  </section>
</template>

<style scoped>
/* --- Layout --- */
.vehicle-list-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
  color: #e2e8f0;
  min-height: 90vh;
}

/* --- 1. Hero Aurora --- */
.hero-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 40px;
  border-radius: 32px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(8, 15, 30, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.15);
  box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.6);
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}
/* Efecto de luz de fondo */
.hero-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.15), transparent 70%);
  filter: blur(60px);
  pointer-events: none;
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
  color: #22d3ee;
  font-weight: 700;
  margin-bottom: 4px;
}
h1 {
  font-size: 2.5rem;
  margin: 0 0 10px 0;
  background: linear-gradient(to right, #fff, #cbd5e1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero-desc {
  color: #94a3b8;
  font-size: 1rem;
  max-width: 500px;
  margin: 0 0 20px 0;
}
.stat-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 99px;
  background: rgba(34, 211, 238, 0.1);
  border: 1px solid rgba(34, 211, 238, 0.2);
  color: #22d3ee;
  font-size: 0.85rem;
  font-weight: 600;
}
.stat-pill .dot {
  width: 6px;
  height: 6px;
  background: currentColor;
  border-radius: 50%;
  box-shadow: 0 0 8px currentColor;
}

.cta-button {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  padding: 14px 28px;
  border-radius: 16px;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}
.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(16, 185, 129, 0.5);
}

/* --- 2. Filtros Glass --- */
.glass-panel {
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.filters-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  margin-bottom: 24px;
  gap: 20px;
  flex-wrap: wrap;
}

.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
}
.search-input {
  width: 100%;
  padding: 12px 12px 12px 44px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  color: #fff;
  font-size: 0.95rem;
  transition: all 0.2s;
}
.search-input:focus {
  outline: none;
  border-color: #38bdf8;
  background: rgba(30, 41, 59, 0.8);
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
}

/* Toggle Switch */
.toggle-filter {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  transition: background 0.2s;
}
.toggle-filter:hover {
  background: rgba(148, 163, 184, 0.1);
}
.toggle-filter input {
  display: none;
}
.toggle-track {
  width: 44px;
  height: 24px;
  background: rgba(148, 163, 184, 0.2);
  border-radius: 99px;
  position: relative;
  transition: background 0.3s;
}
.toggle-thumb {
  width: 18px;
  height: 18px;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
.toggle-filter input:checked + .toggle-track {
  background: #34d399;
}
.toggle-filter input:checked + .toggle-track .toggle-thumb {
  transform: translateX(20px);
}
.toggle-label {
  font-weight: 600;
  color: #cbd5e1;
}

/* --- 3. Lista y Tabla --- */
.list-container {
  padding: 0;
}
.table-header-row {
  display: grid;
  grid-template-columns: 1.2fr 2fr 2fr 1fr;
  padding: 16px 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.3);
}
.col-head {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  font-weight: 700;
}
.align-right {
  text-align: right;
}

.vehicle-row {
  display: grid;
  grid-template-columns: 1.2fr 2fr 2fr 1fr;
  padding: 20px 24px;
  align-items: center;
  border-bottom: 1px solid rgba(148, 163, 184, 0.05);
  transition: all 0.2s ease;
  cursor: pointer;
}
.vehicle-row:hover {
  background: rgba(59, 130, 246, 0.05);
  transform: translateX(4px);
}
.vehicle-row:last-child {
  border-bottom: none;
}

/* Columnas */
.patente-badge {
  display: inline-block;
  font-family: monospace;
  font-size: 1rem;
  font-weight: 700;
  padding: 6px 12px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid #f59e0b;
  color: #f59e0b;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(245, 158, 11, 0.1);
}

.model {
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}
.date {
  font-size: 0.85rem;
  color: #64748b;
  margin: 4px 0 0;
}

.driver-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  border-radius: 99px;
}
.driver-pill.assigned {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.driver-pill.unassigned {
  background: rgba(148, 163, 184, 0.1);
  padding: 6px 12px;
  color: #94a3b8;
  font-size: 0.9rem;
}
.avatar-dot {
  width: 32px;
  height: 32px;
  background: #10b981;
  color: #064e3b;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 0.9rem;
}
.driver-info {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.driver-info .name {
  font-weight: 600;
  color: #d1fae5;
  font-size: 0.9rem;
}
.driver-info .rut {
  font-size: 0.75rem;
  color: #6ee7b7;
}
.dot-status {
  width: 8px;
  height: 8px;
  background: #64748b;
  border-radius: 50%;
  display: inline-block;
  margin-right: 6px;
}

.action-btn {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: #cbd5e1;
  border-radius: 10px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  float: right;
}
.action-btn:hover {
  border-color: #38bdf8;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
}

/* --- Paginación --- */
.pagination-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  gap: 16px;
}
.page-btn {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #e2e8f0;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.page-btn:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-info {
  font-size: 0.9rem;
  color: #94a3b8;
}
.page-info strong {
  color: #f1f5f9;
}

/* --- Estados de Carga y Vacío --- */
.loading-state {
  padding: 80px;
  text-align: center;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 24px;
  border: 1px dashed rgba(148, 163, 184, 0.2);
}
.spinner-aurora {
  width: 50px;
  height: 50px;
  margin: 0 auto 20px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: #34d399;
  border-bottom-color: rgba(59, 130, 246, 0.2);
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(56, 189, 248, 0.2);
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  padding: 60px;
  text-align: center;
  color: #94a3b8;
}
.empty-icon {
  font-size: 3rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

/* --- 🌟 TRANSICIONES VUE 🌟 --- */

/* Fade básico (para loader) */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide de Página (Lista) - El efecto "out-in" suave */
.page-slide-enter-active,
.page-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 1, 0.5, 1);
}

.page-slide-enter-from {
  opacity: 0;
  transform: translateY(15px); /* Entra desde abajo */
}

.page-slide-leave-to {
  opacity: 0;
  transform: translateY(-15px); /* Sale hacia arriba */
}

/* Responsividad */
@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  .cta-button {
    width: 100%;
    justify-content: center;
  }
  .table-header-row {
    display: none;
  }
  .vehicle-row {
    grid-template-columns: 1fr;
    gap: 12px;
    text-align: left;
  }
  .action-btn {
    float: none;
    width: 100%;
    margin-top: 10px;
  }
  .patente-badge {
    align-self: flex-start;
  }
}
</style>
