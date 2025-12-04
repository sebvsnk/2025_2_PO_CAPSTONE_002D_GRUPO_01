<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(true)
const errorMsg = ref(null)
const selectedReport = ref('horas-hombre')
const reportData = ref(null)

const timeFilter = ref('30')
const endpoint = ref('reportes/horas-hombre/')
const isDownloading = ref(false)
const API_BASE_URL = import.meta.env.VITE_API_URL

// --- FUNCIÓN CORREGIDA (Para evitar el error 404 anterior) ---
const fetchReport = async (reportType) => {
  isLoading.value = true
  errorMsg.value = null
  reportData.value = null

  let newEndpoint = ''
  switch (reportType) {
    case 'horas-hombre':
      newEndpoint = 'reportes/horas-hombre/'
      break
    case 'duracion-etapa':
      newEndpoint = 'reportes/duracion-etapas/' // Plural correcto
      break
    case 'salidas':
      newEndpoint = 'reportes/entradas-salidas/' // Nombre completo correcto
      break
    default:
      newEndpoint = ''
      break
  }
  endpoint.value = newEndpoint

  try {
    const url = `${API_BASE_URL}/${endpoint.value}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      throw new Error(`Error ${response.status}: Acceso denegado o datos no disponibles.`)
    }
    reportData.value = await response.json()
  } catch (error) {
    console.error('Report API Error:', error)
    errorMsg.value = `Fallo al cargar el reporte: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const downloadReport = async (format) => {
  isDownloading.value = true
  errorMsg.value = null

  try {
    const url = `${API_BASE_URL}/${endpoint.value}?exportar=${format}`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) {
      try {
        const errData = await response.json()
        throw new Error(errData.detail || `Error ${response.status}`)
      } catch {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }
    }
    const blob = await response.blob()
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `reporte.${format}`
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="(.+)"/)
      if (filenameMatch && filenameMatch.length > 1) {
        filename = filenameMatch[1]
      }
    }
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(downloadUrl)
  } catch (error) {
    console.error('Download Error:', error)
    errorMsg.value = `Fallo al descargar el reporte: ${error.message}`
  } finally {
    isDownloading.value = false
  }
}

const applyTimeFilter = (range) => {
  timeFilter.value = range
  fetchReport(selectedReport.value)
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchReport(selectedReport.value)
  } else {
    router.push({ name: 'Login' })
  }
})

const chartData = computed(() => {
  if (!reportData.value || reportData.value.length === 0) return null

  const filtered = filterByTime(reportData.value, selectedReport.value, timeFilter.value)

  switch (selectedReport.value) {
    case 'horas-hombre':
      return {
        labels: filtered.map((item) => item.responsable_nombre),
        datasets: [
          {
            label: 'Segundos Totales Trabajados',
            backgroundColor: '#22c55e',
            data: filtered.map((item) => item.segundos_totales_trabajados),
          },
        ],
      }
    case 'duracion-etapa':
      return {
        labels: filtered.map((item) => item.estado_label),
        datasets: [
          {
            label: 'Duración Promedio (Segundos)',
            backgroundColor: '#facc15',
            data: filtered.map((item) => item.duracion_promedio_segundos),
          },
        ],
      }
    case 'salidas': {
      const data = [...filtered].slice(0, 15).reverse()
      return {
        labels: data.map((item) => new Date(item.label).toLocaleDateString('es-CL')),
        datasets: [
          {
            label: 'Entradas',
            backgroundColor: '#22c55e',
            data: data.map((item) => item.entradas),
          },
          { label: 'Salidas', backgroundColor: '#f87171', data: data.map((item) => item.salidas) },
        ],
      }
    }
    default:
      return null
  }
})

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 900, easing: 'easeOutQuart' },
  plugins: {
    legend: { position: 'top' },
    title: { display: true, text: 'Visualización del Reporte' },
  },
})

const filterByTime = (data, reportType, windowValue) => {
  if (windowValue === 'all') return data
  const days = Number(windowValue)
  if (Number.isNaN(days)) return data
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - days)

  const parseDate = (item) => {
    if (reportType === 'salidas') return item.label ? new Date(item.label) : null
    return item.fecha || item.date ? new Date(item.fecha || item.date) : null
  }

  return data.filter((item) => {
    const d = parseDate(item)
    if (!d || isNaN(d)) return true
    return d >= cutoff
  })
}
</script>

<template>
  <div class="reports-container">
    <header class="report-header">
      <button class="back-button" @click="router.push({ name: 'Dashboard' })">
        ↩ Volver al Inicio
      </button>
      <div class="title-stack">
        <p class="eyebrow">Reportes y Métricas</p>
        <h1>Módulo de Reportes</h1>
      </div>
      <div class="report-selector-group">
        <label for="report-select">Seleccionar Reporte:</label>
        <select id="report-select" v-model="selectedReport" @change="fetchReport(selectedReport)">
          <option value="horas-hombre">Horas-Hombre (Efectivas)</option>
          <option value="duracion-etapa">Duración por Etapa (Promedio)</option>
          <option value="salidas">Entradas vs. Salidas</option>
        </select>
      </div>
    </header>

    <div class="filters-panel">
      <div class="filters-left">
        <h3>Rango temporal</h3>
        <div class="chip-group">
          <button
            :class="['chip', { active: timeFilter === '7' }]"
            @click="applyTimeFilter('7')"
          >
            Últimos 7 días
          </button>

          <button
            :class="['chip', { active: timeFilter === '30' }]"
            @click="applyTimeFilter('30')"
          >
            Últimos 30 días
          </button>

          <button
            :class="['chip', { active: timeFilter === '90' }]"
            @click="applyTimeFilter('90')"
          >
            Últimos 90 días
          </button>

          <button
            :class="['chip', { active: timeFilter === 'all' }]"
            @click="applyTimeFilter('all')"
          >
            Todo
          </button>
        </div>
      </div>
      <div class="filters-right">
        <p class="meta">
          {{ reportData?.length || 0 }} registros ·
          {{
            timeFilter === 'all'
              ? 'Sin límite de tiempo'
              : 'Filtro: últimos ' + timeFilter + ' días'
          }}
        </p>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="skeleton-wrapper">
        <div class="skeleton-line short shimmer"></div>
        <div class="skeleton-line shimmer"></div>
        <div class="skeleton-chart shimmer"></div>
      </div>
      <p>Cargando datos del reporte {{ selectedReport }}...</p>
    </div>

    <div v-if="errorMsg" class="error-state">
      {{ errorMsg }}
    </div>

    <div v-else-if="chartData && reportData.length > 0" class="report-content">
      <div class="chart-shell">
        <div class="chart-header">
          <div>
            <p class="eyebrow">Visualización</p>
            <h2>
              {{
                selectedReport === 'horas-hombre'
                  ? 'Horas-Hombre'
                  : selectedReport === 'duracion-etapa'
                    ? 'Duración por etapa'
                    : 'Entradas vs. salidas'
              }}
            </h2>
          </div>
        </div>
        <Transition name="fade-scale" mode="out-in">
          <div :key="selectedReport + timeFilter" class="chart-container">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </Transition>
      </div>

      <div class="export-links">
        <button :disabled="isDownloading" class="export-button csv" @click="downloadReport('csv')">
          {{ isDownloading ? 'Descargando...' : 'Exportar a CSV' }}
        </button>
        <button
          :disabled="isDownloading"
          class="export-button xlsx"
          @click="downloadReport('xlsx')"
        >
          {{ isDownloading ? 'Descargando...' : 'Exportar a XLSX' }}
        </button>
      </div>
    </div>
    <div v-else-if="!isLoading && !errorMsg" class="empty-state">
      No hay datos disponibles para este reporte con los filtros actuales.
    </div>
  </div>
</template>

<style scoped>
.reports-container {
  max-width: 1300px;
  margin: 24px auto 40px;
  padding: 0 16px 24px;
  background:
    radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.12), transparent 45%),
    radial-gradient(circle at 80% 0%, rgba(34, 197, 94, 0.12), transparent 55%),
    rgba(8, 15, 32, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 22px;
  box-shadow: 0 35px 85px rgba(2, 6, 23, 0.7);
  backdrop-filter: blur(12px);
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 18px 12px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.28);
}
.title-stack {
  flex: 1;
}
.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(226, 232, 240, 0.7);
}
.report-header h1 {
  margin: 4px 0 0;
  font-size: 28px;
  color: #e2e8f0;
}
.back-button {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(45, 212, 191, 0.35));
  border: 1px solid rgba(148, 163, 184, 0.45);
  padding: 10px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: #e2e8f0;
  font-weight: 700;
  letter-spacing: 0.01em;
  transition: all 0.25s ease;
  box-shadow:
    0 12px 26px rgba(15, 23, 42, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
}
.back-button:hover {
  transform: translateY(-1px);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.45), rgba(45, 212, 191, 0.5));
  border-color: rgba(148, 163, 184, 0.62);
  box-shadow:
    0 16px 34px rgba(15, 23, 42, 0.6),
    0 0 18px rgba(59, 130, 246, 0.25);
}
.back-button:active {
  transform: translateY(0);
}

.report-selector-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.report-selector-group label {
  font-weight: 600;
  color: rgba(226, 232, 240, 0.7);
}
.report-selector-group select {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
  min-width: 210px;
}

.filters-panel {
  margin: 18px 0 10px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.75);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  box-shadow: 0 16px 30px rgba(2, 6, 23, 0.45);
}
.filters-left h3 {
  margin: 0 0 8px;
  color: #e2e8f0;
  font-size: 15px;
}
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.9);
  color: #e2e8f0;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}
.chip.active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.55), rgba(45, 212, 191, 0.55));
  border-color: rgba(148, 163, 184, 0.55);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.4);
}
.filters-right .meta {
  margin: 0;
  color: rgba(226, 232, 240, 0.8);
}

.loading-state,
.error-state,
.empty-state {
  padding: 30px;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 16px;
  margin-top: 20px;
  background: rgba(15, 23, 42, 0.7);
  color: #e2e8f0;
}
.error-state {
  color: #f87171;
  background-color: rgba(248, 113, 113, 0.18);
}

.skeleton-wrapper {
  width: 100%;
  display: grid;
  gap: 12px;
}
.skeleton-line {
  height: 12px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.15);
}
.skeleton-line.short {
  width: 40%;
  justify-self: center;
}
.skeleton-chart {
  height: 280px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.6);
}
.shimmer {
  position: relative;
  overflow: hidden;
}
.shimmer::after {
  content: '';
  position: absolute;
  inset: 0;
  transform: translateX(-100%);
  background: linear-gradient(120deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

.report-content {
  padding: 20px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  background: linear-gradient(160deg, rgba(15, 23, 42, 0.88), rgba(10, 15, 28, 0.92));
  box-shadow: 0 28px 60px rgba(2, 6, 23, 0.55);
}
.chart-shell {
  background: rgba(8, 15, 32, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  padding: 16px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.chart-header h2 {
  margin: 4px 0 0;
  color: #e2e8f0;
}
.badge {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.18);
  color: #bfdbfe;
  border: 1px solid rgba(59, 130, 246, 0.35);
  font-weight: 700;
}
.chart-container {
  position: relative;
  height: 420px;
  margin-top: 8px;
}
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.35s ease;
}
.fade-scale-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.96);
  filter: blur(2px);
}
.fade-scale-leave-to {
  opacity: 0;
  transform: translateY(-12px) scale(0.98);
  filter: blur(1px);
}

.export-links {
  margin-top: 18px;
  display: flex;
  gap: 12px;
}
.export-button {
  text-decoration: none;
  color: white;
  padding: 10px 20px;
  border-radius: 12px;
  font-weight: bold;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  border: none;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.4);
}
.export-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
.export-button.csv {
  background: linear-gradient(135deg, #22c55e, #16a34a);
}
.export-button.xlsx {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.export-button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(37, 99, 235, 0.25);
}

.empty-state {
  border: 1px solid rgba(148, 163, 184, 0.3);
  padding: 18px;
  border-radius: 12px;
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.5);
  text-align: center;
}
</style>
