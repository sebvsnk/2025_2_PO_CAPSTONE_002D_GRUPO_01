<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const logs = ref([])
const isLoading = ref(true)
const errorMsg = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL

// Filtros
const filterEntityType = ref('')
const filterEntityId = ref('')
const filterActionType = ref('')

// Paginación
const pageSize = ref(15)
const totalLogs = ref(0)
const currentPage = ref(1)

const totalPages = computed(() => {
  if (totalLogs.value === 0) return 1
  return Math.ceil(totalLogs.value / pageSize.value)
})

// Listas de Opciones (Actualizadas con lo nuevo)
const entityTypes = ['ot', 'tarea', 'usuario', 'vehiculo', 'tarea_repuesto']

const actionTypes = [
  'OT_CREATE',
  'OT_EDIT',
  'OT_STATUS_CHANGE',
  'TAREA_CREATE',
  'TAREA_START',
  'TAREA_PAUSE',
  'TAREA_RESUME',
  'TAREA_CLOSE',
  'TAREA_ANULAR',
  'TAREA_REPUESTO_ADD',
  'EVIDENCIA_UPLOAD',
  'CHOFER_CONTACT_CREATE', // <--- Nuevo
  'VEHICULO_PATENTE_CHANGE', // <--- Nuevo
  'ADMIN_USER_INVITE',
  'ADMIN_USER_UPDATE',
  'ADMIN_USER_DELETE',
]

// Carga de Datos
const fetchAuditLogs = async () => {
  isLoading.value = true
  errorMsg.value = null

  const params = new URLSearchParams()
  if (filterEntityType.value) params.append('entity_type', filterEntityType.value)
  if (filterEntityId.value) params.append('entity_id', filterEntityId.value)
  if (filterActionType.value) params.append('action_type', filterActionType.value)

  params.append('page', currentPage.value)
  params.append('page_size', pageSize.value)

  try {
    const response = await fetch(`${API_BASE_URL}/auditoria/?${params.toString()}`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`)

    const data = await response.json()
    if (data && data.results) {
      logs.value = data.results
      totalLogs.value = data.count
    } else {
      logs.value = []
      totalLogs.value = 0
    }
  } catch (error) {
    console.error('Audit Error:', error)
    errorMsg.value = `Error cargando datos: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

// Navegación Paginación
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchAuditLogs()
  }
}

const clearFilters = () => {
  filterEntityType.value = ''
  filterEntityId.value = ''
  filterActionType.value = ''
  currentPage.value = 1
}

// Formateo Inteligente de Detalles
const formatPrettyDetails = (log) => {
  if (!log.details || Object.keys(log.details).length === 0) return '---'
  const { details, action_type } = log

  try {
    switch (action_type) {
      case 'OT_STATUS_CHANGE':
        return `Estado: ${details.old_status_code || 'N/A'} ➝ ${details.new_status_code || 'N/A'}`
      case 'OT_EDIT':
        return `Editó '${details.field}': "${details.old_value || ''}" ➝ "${details.new_value || ''}"`
      case 'OT_CREATE':
        return `Creó OT para Vehículo #${details.vehiculo_id}. "${details.descripcion || ''}"`
      case 'TAREA_CREATE':
        return `Creó Tarea: "${details.nombre}"`
      case 'TAREA_PAUSE':
        return `Pausó por: "${details.motivo || 'N/A'}"`
      case 'TAREA_ANULAR':
        return `Anuló tarea (Estado previo: ${details.estado_anterior || '?'})`
      case 'CHOFER_CONTACT_CREATE':
        return `Creó Chofer: ${details.nombre} (RUT: ${details.rut})`
      case 'VEHICULO_PATENTE_CHANGE':
        return `Cambió Patente: ${details.old || '?'} ➝ ${details.new || '?'}`
      case 'ADMIN_USER_INVITE':
        return `Invitó usuario: ${details.email} (${details.rol})`
      default:
        return JSON.stringify(details)
    }
  } catch {
    return JSON.stringify(log.details)
  }
}

// Watchers para recargar al filtrar
const resetAndFetch = () => {
  currentPage.value = 1
  fetchAuditLogs()
}
watch(filterEntityType, resetAndFetch)
watch(filterEntityId, resetAndFetch)
watch(filterActionType, resetAndFetch)

onMounted(() => {
  if (authStore.isAuthenticated) fetchAuditLogs()
  else router.push({ name: 'Login' })
})
</script>

<template>
  <div class="audit-wrapper">
    <div class="hero-header">
      <div class="hero-copy">
        <p class="eyebrow">Seguridad y Trazabilidad</p>
        <h1>Registro de Auditoría</h1>
        <p>Historial completo de acciones y cambios en el sistema.</p>
      </div>
      <button class="btn-aurora back" @click="router.push({ name: 'Dashboard' })">
        &larr; Volver al Inicio
      </button>
    </div>

    <section class="filters-glass">
      <div class="filter-group">
        <label>Tipo de Entidad</label>
        <select v-model="filterEntityType" class="input-aurora select">
          <option value="">Todos</option>
          <option v-for="e in entityTypes" :key="e" :value="e">{{ e.toUpperCase() }}</option>
        </select>
      </div>

      <div class="filter-group">
        <label>ID Entidad</label>
        <input
          v-model.number="filterEntityId"
          type="number"
          placeholder="Ej: 15"
          class="input-aurora"
        />
      </div>

      <div class="filter-group">
        <label>Tipo de Acción</label>
        <select v-model="filterActionType" class="input-aurora select">
          <option value="">Todas</option>
          <option v-for="a in actionTypes" :key="a" :value="a">{{ a }}</option>
        </select>
      </div>

      <button class="btn-aurora secondary" @click="clearFilters">Limpiar</button>
    </section>

    <div v-if="isLoading" class="state-card loading-card">
      <div class="spinner-aurora"></div>
      <p>Analizando registros...</p>
    </div>

    <div v-else-if="errorMsg" class="state-card error-card">{{ errorMsg }}</div>

    <div v-else-if="logs.length > 0" class="table-container panel-aurora">
      <div class="table-scroll scroll-aurora">
        <Transition name="list-fade" mode="out-in" appear>
          <div :key="currentPage" class="anim-wrapper">
            <table class="audit-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Entidad</th>
                  <th>ID</th>
                  <th>Detalles</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in logs" :key="log.id">
                  <td class="date-cell">
                    {{ new Date(log.creado_en).toLocaleString('es-CL') }}
                  </td>
                  <td>
                    <div class="user-cell">
                      <span class="avatar">{{ log.usuario?.nombre?.charAt(0) || 'S' }}</span>
                      <span>{{ log.usuario?.nombre || 'Sistema' }}</span>
                    </div>
                  </td>
                  <td>
                    <span class="tag action">{{ log.action_type }}</span>
                  </td>
                  <td>
                    <span class="tag entity">{{ log.entity_type }}</span>
                  </td>
                  <td class="id-cell">#{{ log.entity_id }}</td>
                  <td class="details-cell">{{ formatPrettyDetails(log) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Transition>
      </div>

      <div class="pagination-bar">
        <span class="page-info">
          Mostrando <strong>{{ logs.length }}</strong> de <strong>{{ totalLogs }}</strong> eventos.
          (Pág {{ currentPage }} de {{ totalPages }})
        </span>
        <div class="nav-buttons">
          <button :disabled="currentPage === 1" class="btn-page" @click="goToPage(currentPage - 1)">
            &lt;
          </button>
          <button
            :disabled="currentPage === totalPages"
            class="btn-page"
            @click="goToPage(currentPage + 1)"
          >
            &gt;
          </button>
        </div>
      </div>
    </div>

    <div v-else class="state-card empty-card">
      <span class="icon">📭</span>
      <p>No se encontraron eventos con estos filtros.</p>
    </div>
  </div>
</template>

<style scoped>
/* --- LAYOUT BASE --- */
.audit-wrapper {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  color: #e2e8f0;
  min-height: 90vh;
}

/* --- HERO HEADER (Aurora) --- */
.hero-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  margin-bottom: 24px;
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(15, 23, 42, 0.85));
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  position: relative;
  overflow: hidden;
}
.hero-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 50%;
  height: 200%;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.15), transparent 60%);
  filter: blur(40px);
  pointer-events: none;
}
.hero-copy {
  z-index: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: #94a3b8;
  margin: 0 0 8px;
}
.hero-header h1 {
  margin: 0;
  font-size: 2.2rem;
  color: #f8fafc;
  letter-spacing: -0.02em;
}
.hero-header p {
  margin: 6px 0 0;
  color: #cbd5e1;
}

/* --- BOTONES AURORA --- */
.btn-aurora {
  padding: 10px 20px;
  border-radius: 99px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid rgba(148, 163, 184, 0.3);
}
.btn-aurora.back {
  background: rgba(15, 23, 42, 0.6);
  color: #cbd5e1;
}
.btn-aurora.back:hover {
  border-color: #38bdf8;
  color: #fff;
  background: rgba(56, 189, 248, 0.15);
}
.btn-aurora.secondary {
  background: rgba(56, 189, 248, 0.1);
  border-color: rgba(56, 189, 248, 0.3);
  color: #38bdf8;
}
.btn-aurora.secondary:hover {
  background: rgba(56, 189, 248, 0.2);
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
}

/* --- BARRA DE FILTROS GLASS --- */
.filters-glass {
  display: flex;
  gap: 20px;
  align-items: flex-end;
  padding: 20px;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 20px;
  backdrop-filter: blur(10px);
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.filter-group label {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 600;
  padding-left: 4px;
}

.input-aurora {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: #f1f5f9;
  padding: 10px 14px;
  border-radius: 10px;
  min-width: 180px;
  outline: none;
  transition: all 0.2s;
}
.input-aurora:focus {
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
}
.input-aurora.select {
  cursor: pointer;
}

/* --- TABLA Y PANEL --- */
.panel-aurora {
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.08), transparent 55%),
    radial-gradient(circle at 80% 80%, rgba(34, 197, 94, 0.08), transparent 50%),
    rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(2, 6, 23, 0.5);
  backdrop-filter: blur(12px);
  overflow: hidden;
}

.table-scroll {
  overflow-x: auto;
}

/* --- Scrollbar Aurora Dark Glass --- */

/* 1. El ancho de la barra */
::-webkit-scrollbar {
  width: 10px; /* Ancho vertical */
  height: 10px; /* Alto horizontal */
}

/* 2. El "carril" o fondo de la barra (Efecto Glass Oscuro) */
::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6); /* Azul oscuro muy transparente */
  border-radius: 8px;
  margin: 4px;
  backdrop-filter: blur(4px); /* Opcional: si el navegador lo soporta en scrollbars */
  border: 1px solid rgba(148, 163, 184, 0.1); /* Borde sutil */
}

/* 3. El "pulgar" o la barra que se mueve (Gradiente Aurora) */
::-webkit-scrollbar-thumb {
  background: linear-gradient(
    180deg,
    rgba(34, 211, 238, 0.6),
    /* Cyan brillante (inicio) */ rgba(59, 130, 246, 0.6),
    /* Azul medio */ rgba(139, 92, 246, 0.6) /* Violeta (final) */
  );
  border-radius: 8px;
  border: 2px solid rgba(15, 23, 42, 0.8); /* Borde oscuro para separarlo del track */
  background-clip: padding-box; /* Truco para que el borde sea transparente real */
  transition: background 0.3s ease;
}

/* 4. Efecto Hover (Al pasar el mouse por la barra) */
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(
    180deg,
    rgba(34, 211, 238, 0.9),
    rgba(59, 130, 246, 0.9),
    rgba(139, 92, 246, 0.9)
  );
  border: 2px solid rgba(15, 23, 42, 1); /* Borde más sólido */
  cursor: pointer;
}

/* 5. Esquina (donde se cruzan scroll vertical y horizontal) */
::-webkit-scrollbar-corner {
  background: rgba(15, 23, 42, 0); /* Transparente */
}

.audit-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 900px;
}
.audit-table th {
  text-align: left;
  padding: 16px 20px;
  color: #94a3b8;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  background: rgba(15, 23, 42, 0.4);
}
.audit-table td {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.05);
  font-size: 0.95rem;
  vertical-align: middle;
}
.audit-table tr:hover {
  background: rgba(59, 130, 246, 0.05);
}

/* Celdas Específicas */
.date-cell {
  color: #cbd5e1;
  font-family: monospace;
  font-size: 0.9rem;
}
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 28px;
  height: 28px;
  background: rgba(56, 189, 248, 0.2);
  color: #38bdf8;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
}
.tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
}
.tag.action {
  background: rgba(16, 185, 129, 0.1);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.tag.entity {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  text-transform: uppercase;
}
.id-cell {
  font-family: monospace;
  color: #64748b;
}
.details-cell {
  color: #e2e8f0;
  max-width: 400px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* --- PAGINACIÓN --- */
.pagination-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-top: 1px solid rgba(148, 163, 184, 0.1);
  background: rgba(15, 23, 42, 0.2);
}
.page-info {
  font-size: 0.9rem;
  color: #94a3b8;
}
.nav-buttons {
  display: flex;
  gap: 8px;
}
.btn-page {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-page:hover:not(:disabled) {
  background: rgba(56, 189, 248, 0.2);
  color: white;
  border-color: #38bdf8;
}
.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* --- SPINNER AURORA --- */
.state-card {
  text-align: center;
  padding: 80px;
  background: rgba(15, 23, 42, 0.4);
  border-radius: 24px;
  border: 1px dashed rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  margin-top: 20px;
}
.spinner-aurora {
  width: 56px;
  height: 56px;
  margin: 0 auto 20px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: rgba(59, 130, 246, 0.5);
  border-bottom-color: rgba(16, 185, 129, 0.2);
  animation: spin 1s linear infinite;
  box-shadow: 0 0 25px rgba(56, 189, 248, 0.2);
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.error-card {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  border-color: rgba(248, 113, 113, 0.3);
}
.empty-card .icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 10px;
  opacity: 0.5;
}

/* --- Estilo del envoltorio para que la tabla no se rompa --- */
.anim-wrapper {
  width: 100%;
  display: block;
}

/* --- ANIMACIÓN DE TRANSICIÓN (Igual a Usuarios) --- */
.list-fade-enter-active,
.list-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-fade-enter-from {
  opacity: 0;
  transform: translateY(15px); /* Entra desde un poco más abajo */
}

.list-fade-leave-to {
  opacity: 0;
  transform: translateY(-15px); /* Sale hacia arriba */
}
@media (max-width: 768px) {
  .hero-header {
    flex-direction: column;
  }
  .filters-glass {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-aurora.secondary {
    width: 100%;
  }
  .pagination-bar {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
