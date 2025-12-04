<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const otId = route.params.otId
const otData = ref(null)
const isLoading = ref(true)
const errorMsg = ref(null)
const isDownloading = ref(false)

const API_BASE_URL = import.meta.env.VITE_API_URL

// 1. Cargar el JSON (Vista Previa HTML)
const fetchExportData = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    // Usamos la ruta correcta para obtener los datos JSON
    const url = `${API_BASE_URL}/ot/${otId}/exportar/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error al cargar los datos del reporte.')
    otData.value = await response.json()
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    // Pequeño delay artificial para que la animación de salida se aprecie
    setTimeout(() => {
      isLoading.value = false
    }, 400)
  }
}

// Helper para formatear fechas
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('es-CL')
}

// 2. Descargar el PDF real
const downloadReport = async () => {
  isDownloading.value = true
  errorMsg.value = null

  try {
    const url = `${API_BASE_URL}/ot/${otId}/exportar/?exportar=pdf`

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Error ${response.status}: No se pudo generar el PDF.`)
    }

    const blob = await response.blob()
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `OT_${otId}_reporte.pdf`
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
    errorMsg.value = error.message
  } finally {
    isDownloading.value = false
  }
}

onMounted(fetchExportData)
</script>

<template>
  <div class="export-wrapper">
    <div class="export-container">
      <header class="actions-header">
        <button class="back-button" @click="router.back()">
          <span class="icon">←</span> Volver
        </button>

        <button
          :disabled="isDownloading || isLoading"
          class="download-button"
          :class="{ downloading: isDownloading }"
          @click="downloadReport"
        >
          <div v-if="isDownloading" class="btn-content">
            <span class="mini-spinner"></span>
            <span>Generando PDF...</span>
          </div>
          <div v-else class="btn-content">
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
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <span>Descargar PDF</span>
          </div>
          <div v-if="isDownloading" class="progress-glow"></div>
        </button>
      </header>

      <Transition name="fade">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner-aurora"></div>
          <p>Preparando vista previa...</p>
        </div>
      </Transition>

      <div v-if="errorMsg" class="error-state">{{ errorMsg }}</div>

      <Transition name="slide-up" mode="out-in">
        <div v-if="otData && !isLoading" class="report-scroll-container aurora-scroll">
          <div class="report-paper">
            <header class="report-paper-header">
              <div class="logo-placeholder">APT</div>
              <div class="report-meta">
                <h1>Reporte de Cierre</h1>
                <p class="ot-number">Orden de Trabajo #{{ otData.id }}</p>
                <p class="date">Generado: {{ new Date().toLocaleString('es-CL') }}</p>
              </div>
            </header>

            <section class="paper-section">
              <h2>Información General</h2>
              <div class="info-grid">
                <div class="info-box">
                  <label>Vehículo</label>
                  <p>{{ otData.vehiculo?.marca }} {{ otData.vehiculo?.modelo }}</p>
                  <span class="badge">{{ otData.vehiculo?.patente }}</span>
                </div>
                <div class="info-box">
                  <label>Estado Final</label>
                  <p>{{ otData.estado?.label }}</p>
                </div>
                <div class="info-box">
                  <label>Supervisor</label>
                  <p>{{ otData.creado_por?.nombre }}</p>
                </div>
                <div class="info-box full">
                  <label>Descripción Inicial</label>
                  <p class="desc">{{ otData.descripcion }}</p>
                </div>
                <div class="info-box">
                  <label>Apertura</label>
                  <p>{{ formatDate(otData.fecha_apertura) }}</p>
                </div>
                <div class="info-box">
                  <label>Cierre</label>
                  <p>{{ formatDate(otData.fecha_cierre) }}</p>
                </div>
              </div>
            </section>

            <section class="paper-section">
              <h2>Detalle de Tareas ({{ otData.tareas.length }})</h2>

              <div v-for="tarea in otData.tareas" :key="tarea.id" class="task-item">
                <div class="task-header">
                  <h3>{{ tarea.nombre }}</h3>
                  <span class="task-status">{{ tarea.estado?.label }}</span>
                </div>

                <div class="task-sub-info">
                  <p><strong>Mecánico:</strong> {{ tarea.responsable?.nombre || 'N/A' }}</p>
                  <p>
                    <strong>Duración:</strong> {{ formatDate(tarea.inicio) }} -
                    {{ formatDate(tarea.fin) }}
                  </p>
                </div>

                <div v-if="tarea.repuestos_usados.length > 0" class="sub-section">
                  <h4>Repuestos:</h4>
                  <ul>
                    <li v-for="r in tarea.repuestos_usados" :key="r.id">
                      {{ r.cantidad }}x {{ r.repuesto.descripcion }} ({{ r.repuesto.codigo }})
                    </li>
                  </ul>
                </div>

                <div v-if="tarea.evidencias.length > 0" class="sub-section">
                  <h4>Evidencia Adjunta:</h4>
                  <div class="evidence-preview-grid">
                    <div v-for="file in tarea.evidencias" :key="file.id" class="evidence-thumb">
                      <img :src="file.url_descarga" loading="lazy" />
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
/* --- Layout Base --- */
.export-wrapper {
  min-height: 85vh;
  padding: 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.export-container {
  width: 100%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* --- Header y Botones --- */
.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
}

.back-button {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: #94a3b8;
  padding: 8px 16px;
  border-radius: 99px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.back-button:hover {
  background: rgba(59, 130, 246, 0.15);
  color: #e2e8f0;
  border-color: rgba(59, 130, 246, 0.5);
}

.download-button {
  position: relative;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  padding: 10px 24px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.download-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
}
.download-button:disabled {
  opacity: 0.8;
  cursor: wait;
}
.btn-content {
  display: flex;
  align-items: center;
  gap: 10px;
  position: relative;
  z-index: 2;
}

/* Animación de Descarga en el Botón */
.progress-glow {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  animation: loadingShim 1.5s infinite;
  z-index: 1;
}
@keyframes loadingShim {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* --- Contenedor con Scroll "Aurora Dark Glass" --- */
.report-scroll-container {
  background: rgba(15, 23, 42, 0.4); /* Fondo oscuro translúcido */
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 16px;
  padding: 4px; /* Espacio para el scroll */
  height: 75vh; /* Altura fija para permitir scroll */
  overflow-y: auto;
  backdrop-filter: blur(10px);
  box-shadow:
    inset 0 0 20px rgba(0, 0, 0, 0.2),
    0 20px 40px rgba(0, 0, 0, 0.3);
}

/* --- Scrollbar Aurora Dark Glass --- */

/* 1. El ancho de la barra */
::-webkit-scrollbar {
  width: 10px; /* Ancho vertical */
  height: 10px; /* Alto horizontal */
}

/* 2. El "carril" o fondo de la barra (Efecto Glass Oscuro) */
::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.6);
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

/* --- Hoja de Papel Digital --- */
.report-paper {
  background: white;
  color: #1e293b;
  padding: 40px;
  border-radius: 8px;
  min-height: 100%;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  font-family: 'Inter', sans-serif; /* Fuente limpia */
}

/* Estilos internos del reporte (simulando el PDF) */
.report-paper-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 20px;
  margin-bottom: 30px;
}
.logo-placeholder {
  font-weight: 900;
  font-size: 24px;
  color: #3b82f6;
  letter-spacing: -1px;
}
.report-meta {
  text-align: right;
}
.report-meta h1 {
  font-size: 1.5rem;
  color: #0f172a;
  margin: 0;
}
.ot-number {
  font-size: 1.1rem;
  font-weight: 700;
  color: #64748b;
  margin: 4px 0;
}
.date {
  font-size: 0.8rem;
  color: #94a3b8;
}

.paper-section {
  margin-bottom: 30px;
}
.paper-section h2 {
  font-size: 1.1rem;
  color: #3b82f6;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 8px;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.info-box label {
  display: block;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
}
.info-box p {
  margin: 2px 0 0;
  font-weight: 500;
  font-size: 0.95rem;
}
.info-box.full {
  grid-column: span 2;
}
.badge {
  display: inline-block;
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 700;
  font-size: 0.9rem;
  margin-top: 4px;
}

.task-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  background: #f8fafc;
}
.task-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.task-header h3 {
  margin: 0;
  font-size: 1rem;
}
.task-status {
  font-size: 0.75rem;
  background: #e2e8f0;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
}
.task-sub-info p {
  margin: 2px 0;
  font-size: 0.85rem;
  color: #475569;
}
.sub-section {
  margin-top: 12px;
  border-top: 1px dashed #cbd5e1;
  padding-top: 8px;
}
.sub-section h4 {
  font-size: 0.85rem;
  margin: 0 0 6px;
  color: #64748b;
}
.sub-section ul {
  padding-left: 20px;
  margin: 0;
  font-size: 0.85rem;
}
.evidence-preview-grid {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.evidence-thumb {
  width: 60px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #cbd5e1;
  flex-shrink: 0;
}
.evidence-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* --- Animaciones --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-leave-active {
  transition: all 0.3s ease-in;
}
.slide-up-enter-from {
  transform: translateY(40px);
  opacity: 0;
}
.slide-up-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

/* Spinner Grande */
.loading-state {
  text-align: center;
  padding: 60px;
}
.spinner-aurora {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #3b82f6;
  border-right-color: #22d3ee;
  border-bottom-color: rgba(59, 130, 246, 0.2);
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.3);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
