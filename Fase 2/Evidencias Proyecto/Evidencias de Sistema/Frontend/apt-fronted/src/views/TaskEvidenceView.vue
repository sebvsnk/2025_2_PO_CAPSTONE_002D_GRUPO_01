<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const taskId = route.params.taskId
const evidences = ref([])
const isLoading = ref(true)
const isUploading = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)

const MAX_FILES = 4

const fileInput = ref(null)
const selectedFile = ref(null)
const previewFiles = ref([])

const modalImageUrl = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL

const isImage = (filename) => {
  if (!filename) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
  const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'))
  return imageExtensions.includes(ext)
}

const fetchEvidence = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/evidencia/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error al cargar la evidencia.')
    evidences.value = await response.json()
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isLoading.value = false
  }
}

const revokePreviews = () => {
  previewFiles.value.forEach((item) => {
    if (item.url) {
      URL.revokeObjectURL(item.url)
    }
  })
  previewFiles.value = []
}

const processFiles = (files) => {
  revokePreviews()
  if (!files || files.length === 0) {
    selectedFile.value = null
    return
  }

  const rawFiles = Array.from(files)
  const warning =
    rawFiles.length > MAX_FILES ? `Puedes adjuntar hasta ${MAX_FILES} archivos por subida.` : null
  const fileArray = rawFiles.slice(0, MAX_FILES)
  selectedFile.value = fileArray
  errorMsg.value = warning
  successMsg.value = null

  previewFiles.value = fileArray.map((file) => {
    const isImg = file.type.startsWith('image/')
    return {
      name: file.name,
      size: file.size,
      isImage: isImg,
      url: isImg ? URL.createObjectURL(file) : null,
    }
  })
}

const handleFileChange = (event) => {
  processFiles(event.target.files)
}

const handleDrop = (event) => {
  event.preventDefault()
  processFiles(event.dataTransfer?.files)
}

const handleUpload = async () => {
  if (!selectedFile.value || selectedFile.value.length === 0) {
    errorMsg.value = 'Por favor, selecciona uno o más archivos para subir.'
    return
  }

  isUploading.value = true
  errorMsg.value = null
  successMsg.value = null

  const formData = new FormData()
  for (const file of selectedFile.value) {
    formData.append('file', file)
  }

  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/evidencia/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
      body: formData,
    })

    const data = await response.json()

    if (!response.ok) {
      const errorDetail = data.detail || data.errors?.[0]?.error || 'Error al subir archivos.'
      throw new Error(errorDetail)
    }

    const successCount = data.data.length
    const errorCount = data.errors.length

    successMsg.value = `✨ Subida completada: ${successCount} archivo(s) guardados correctamente.`
    if (errorCount > 0) {
      errorMsg.value = `⚠️ Fallaron ${errorCount} archivo(s). Revisa el tamaño o tipo.`
      console.error('Errores de subida parcial:', data.errors)
    }

    if (fileInput.value) {
      fileInput.value.value = ''
    }
    selectedFile.value = null
    revokePreviews()

    await fetchEvidence()
  } catch (error) {
    if (!errorMsg.value) {
      errorMsg.value = error.message
    }
  } finally {
    isUploading.value = false
  }
}

const clearSelection = () => {
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  selectedFile.value = null
  revokePreviews()
}

const openImageModal = (url) => {
  modalImageUrl.value = url
}
const closeImageModal = () => {
  modalImageUrl.value = null
}

onMounted(fetchEvidence)
</script>

<template>
  <div class="evidence-page">
    <div class="evidence-container">
      <header class="evidence-header">
        <div class="header-copy">
          <h1>Gestión de evidencia</h1>
          <p class="subtitle">Adjunta o revisa los archivos de respaldo para la tarea.</p>
        </div>
        <button
          class="back-button"
          @click="router.push({ name: 'TaskDetail', params: { taskId } })"
        >
          Volver a la tarea #{{ taskId }}
        </button>
      </header>

      <Transition name="alert-fade">
        <p v-if="errorMsg" class="status-banner error">{{ errorMsg }}</p>
      </Transition>
      <Transition name="alert-fade">
        <p v-if="successMsg" class="status-banner success">{{ successMsg }}</p>
      </Transition>

      <div class="evidence-group">
        <div class="content-grid">
          <!-- SUBIDA -->
          <section class="glass-card upload-section">
            <div class="section-heading">
              <div>
                <p class="eyebrow">Subir archivos</p>
                <h2>Nueva evidencia</h2>
              </div>
              <span v-if="previewFiles.length" class="selection-count">
                {{ previewFiles.length }} seleccionados
              </span>
            </div>
            <div class="upload-panel">
            <label class="upload-box" @dragover.prevent @drop.prevent="handleDrop">
              <input ref="fileInput" type="file" multiple @change="handleFileChange" />
              <div class="upload-icon">
                <svg viewBox="0 0 24 24">
                  <path
                    d="M21.44 11.05 12.95 19.54a4.5 4.5 0 0 1-6.36-6.36l9.9-9.9A3 3 0 1 1 20.73 8.5L10.83 18.4"
                  />
                </svg>
              </div>
              <h3>Arrastra archivos o haz clic para seleccionarlos</h3>
              <p>Formatos: imágenes o PDF · Máx 10MB por archivo</p>
            </label>

            <div class="upload-controls">
              <button
                :disabled="isUploading || !previewFiles.length"
                class="upload-button"
                @click="handleUpload"
              >
                {{ isUploading ? 'Subiendo...' : 'Subir Archivo(s)' }}
              </button>
              <button class="clear-button" :disabled="!previewFiles.length" @click="clearSelection">
                Limpiar selección
              </button>
            </div>

            <Transition name="uploading-slide">
              <div v-if="isUploading" class="uploading-indicator">
                <span class="pulse-dot"></span>
                <div class="indicator-copy">
                  <p>Subiendo archivos...</p>
                  <small>No cierres esta ventana mientras completamos la carga.</small>
                </div>
              </div>
            </Transition>
          </div>

          <div v-if="previewFiles.length" class="preview-grid">
            <div v-for="file in previewFiles" :key="file.name" class="preview-card">
              <div class="preview-thumb" :class="{ placeholder: !file.isImage }">
                <img v-if="file.isImage" :src="file.url" :alt="file.name" />
                <div v-else class="preview-placeholder">
                  <span>{{ file.name.split('.').pop()?.toUpperCase() }}</span>
                </div>
              </div>
              <p class="preview-name">{{ file.name }}</p>
              <span class="file-info">{{ (file.size / 1024).toFixed(0) }} KB</span>
            </div>
          </div>
          </section>

        <!-- EXISTENTE -->
        <section class="glass-card evidence-section">
          <div class="section-heading">
            <div>
              <p class="eyebrow">Historial</p>
              <h2>Evidencia existente</h2>
            </div>
            <span class="badge">{{ evidences.length }}</span>
          </div>

          <div class="evidence-scroll">
            <div v-if="isLoading" class="loading-state">
              <div class="spinner-ring">
                <span></span>
              </div>
              <div class="loading-copy">
                <p>Cargando evidencia</p>
                <small>Estamos trayendo los archivos asociados a la tarea.</small>
              </div>
            </div>

            <div v-else-if="evidences.length > 0" class="cards-grid">
              <article v-for="file in evidences" :key="file.id" class="evidence-card">
                <div
                  class="thumbnail-wrapper"
                  :class="{ clickable: isImage(file.path) }"
                  @click="isImage(file.path) ? openImageModal(file.url_descarga) : null"
                >
                  <img
                    v-if="isImage(file.path)"
                    :src="file.url_descarga"
                    :alt="file.path.split('/').pop()"
                    class="thumbnail"
                    loading="lazy"
                  />
                  <a
                    v-else
                    :href="file.url_descarga"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="file-icon-link"
                  >
                    <div class="file-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                      </svg>
                    </div>
                  </a>
                </div>
                <div class="file-details">
                  <a
                    :href="file.url_descarga"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="filename"
                    :title="file.path.split('/').pop()"
                  >
                    {{ file.path.split('/').pop() }}
                  </a>
                  <span class="file-info">
                    {{ (file.tamano_bytes / 1024).toFixed(0) }} KB ·
                    {{ new Date(file.fecha_subida).toLocaleDateString() }}
                  </span>
                </div>
              </article>
            </div>

            <p v-else class="empty-state">No hay evidencia adjunta a esta tarea.</p>
          </div>
          </section>
        </div>
      </div>
    </div>

    <Transition name="modal-fade">
      <div v-if="modalImageUrl" class="image-modal-overlay" @click="closeImageModal">
        <div class="image-modal-content" @click.stop>
          <span class="close-button" @click="closeImageModal">&times;</span>
          <img :src="modalImageUrl" alt="Vista ampliada" />
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.evidence-page {
  position: relative;
  min-height: 100vh;
  padding: 12px 20px 70px;
  background: transparent;
  background-image: none;
  color: #e2e8f0;
}
.evidence-container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 28px;
  border-radius: 36px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background:
    radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.18), transparent 55%),
    radial-gradient(circle at 85% 0%, rgba(16, 185, 129, 0.16), transparent 50%),
    rgba(6, 12, 25, 0.75);
  box-shadow: 0 35px 100px rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(16px);
  position: relative;
  overflow: hidden;
}
.evidence-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 78% 12%, rgba(16, 185, 129, 0.2), transparent 60%);
  pointer-events: none;
}
.evidence-container > * {
  position: relative;
  z-index: 1;
}
.evidence-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  margin-bottom: 28px;
}
.header-copy h1 {
  margin: 0;
  font-size: 1.95rem;
  font-weight: 700;
  color: #f8fafc;
}
.header-copy .subtitle {
  margin-top: 6px;
  color: rgba(226, 232, 240, 0.75);
  font-size: 0.95rem;
}
.header-copy .eyebrow {
  margin-bottom: 6px;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.25em;
  font-size: 0.65rem;
  color: rgba(191, 219, 254, 0.7);
}
.back-button {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.45);
  color: #bbf7d0;
  padding: 10px 20px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  text-transform: uppercase;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.back-button:hover {
  background: rgba(16, 185, 129, 0.35);
  box-shadow: 0 10px 35px rgba(16, 185, 129, 0.35);
  transform: translateY(-1px);
}
.status-banner {
  margin-bottom: 16px;
  padding: 12px 18px;
  border-radius: 16px;
  font-weight: 600;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.25);
}
.status-banner.success {
  color: #34d399;
  border-color: rgba(34, 197, 94, 0.4);
  background: rgba(22, 101, 52, 0.3);
  animation: glowPulse 1.6s ease-in-out infinite alternate;
}
.status-banner.error {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(127, 29, 29, 0.3);
}
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.alert-fade-enter-from,
.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 30px;
  align-items: flex-start;
}
.evidence-group {
  margin-top: 12px;
  padding: 0;
  border-radius: 32px;
  background: transparent;
  border: none;
  box-shadow: none;
}
.glass-card {
  background: rgba(10, 15, 30, 0.9);
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  box-shadow:
    0 25px 60px rgba(2, 6, 23, 0.7),
    inset 0 0 0 1px rgba(255, 255, 255, 0.02);
  padding: 28px;
  backdrop-filter: blur(18px);
}
.evidence-section {
  max-height: 78vh;
  display: flex;
  flex-direction: column;
}
.evidence-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
  margin-right: -6px;
  max-height: 520px;
}
.evidence-scroll::-webkit-scrollbar {
  width: 8px;
}
.evidence-scroll::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.35);
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.25);
  box-shadow: inset 0 0 12px rgba(2, 6, 23, 0.55);
}
.evidence-scroll::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(34, 197, 94, 0.9), rgba(14, 165, 233, 0.85));
  border-radius: 999px;
  box-shadow:
    inset 0 0 6px rgba(15, 23, 42, 0.6),
    0 6px 18px rgba(34, 197, 94, 0.4);
}
.evidence-scroll {
  scrollbar-width: thin;
  scrollbar-color: rgba(34, 197, 94, 0.9) rgba(15, 23, 42, 0.4);
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 22px;
}
.section-heading h2 {
  margin: 2px 0 0;
  font-size: 1.3rem;
  color: #f8fafc;
}
.selection-count {
  font-size: 0.85rem;
  color: rgba(226, 232, 240, 0.8);
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: rgba(15, 23, 42, 0.6);
}
.upload-panel {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.upload-box {
  border: 1px dashed rgba(96, 165, 250, 0.5);
  border-radius: 26px;
  padding: 32px 28px;
  background: rgba(15, 23, 42, 0.65);
  text-align: center;
  color: rgba(226, 232, 240, 0.85);
  transition: border 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
  cursor: pointer;
}
.upload-box:hover {
  border-color: rgba(14, 165, 233, 0.75);
  box-shadow: 0 20px 40px rgba(14, 165, 233, 0.25);
  transform: translateY(-2px);
}
.upload-box input[type='file'] {
  display: none;
}
.upload-box h3 {
  margin: 14px 0 6px;
  font-size: 1.05rem;
  color: #f8fafc;
}
.upload-box p {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(226, 232, 240, 0.65);
}
.upload-icon {
  width: 60px;
  height: 60px;
  border-radius: 18px;
  margin: 0 auto;
  display: grid;
  place-items: center;
  background: linear-gradient(145deg, rgba(14, 165, 233, 0.25), rgba(14, 165, 233, 0.05));
  color: #7dd3fc;
}
.upload-icon svg {
  width: 34px;
  height: 34px;
  stroke: currentColor;
  stroke-width: 1.8;
  fill: none;
}
.upload-controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.uploading-indicator {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 20px;
  border: 1px solid rgba(59, 130, 246, 0.35);
  background: rgba(8, 47, 73, 0.5);
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.25);
  overflow: hidden;
}
.pulse-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: linear-gradient(120deg, #22d3ee, #3b82f6);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.7);
  animation: dotPulse 1s ease-in-out infinite;
}
.indicator-copy p {
  margin: 0;
  font-weight: 600;
  color: #f0f9ff;
}
.indicator-copy small {
  display: block;
  color: rgba(226, 232, 240, 0.7);
}
.uploading-slide-enter-active,
.uploading-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.uploading-slide-enter-from,
.uploading-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
.upload-button,
.clear-button {
  padding: 12px 26px;
  border-radius: 999px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}
.upload-button {
  background: linear-gradient(120deg, #22d3ee, #3b82f6, #8b5cf6);
  color: #030712;
  box-shadow: 0 20px 45px rgba(59, 130, 246, 0.4);
}
.upload-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
.clear-button {
  background: rgba(148, 163, 184, 0.2);
  border: 1px solid rgba(148, 163, 184, 0.4);
  color: #e2e8f0;
}
.clear-button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.preview-grid {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}
.preview-card {
  border-radius: 20px;
  padding: 14px;
  background: rgba(8, 13, 27, 0.96);
  border: 1px solid rgba(59, 130, 246, 0.25);
  box-shadow: 0 18px 40px rgba(2, 6, 23, 0.45);
}
.preview-thumb {
  width: 100%;
  height: 160px;
  border-radius: 16px;
  overflow: hidden;
  background: rgba(15, 23, 42, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  animation: fadeIn 0.35s ease forwards;
}
.preview-thumb.placeholder {
  border: 1px dashed rgba(148, 163, 184, 0.35);
}
.preview-placeholder span {
  font-weight: 700;
  color: rgba(226, 232, 240, 0.85);
}
.preview-name {
  margin: 12px 0 0;
  color: rgba(226, 232, 240, 0.9);
  font-size: 0.9rem;
  word-break: break-all;
}
.file-info {
  display: block;
  font-size: 0.8rem;
  color: rgba(148, 163, 184, 0.9);
  margin-top: 4px;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
}
.evidence-card {
  border-radius: 24px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(11, 17, 33, 0.95);
  overflow: hidden;
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.6);
  transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.evidence-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 35px 80px rgba(14, 165, 233, 0.35);
}
.thumbnail-wrapper {
  height: 170px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.66);
  overflow: hidden;
  transition: background 0.2s ease, transform 0.2s ease;
}
.thumbnail-wrapper.clickable {
  cursor: zoom-in;
}
.thumbnail-wrapper.clickable:hover {
  background-color: rgba(59, 130, 246, 0.25);
  transform: scale(1.01);
}
.thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  animation: fadeIn 0.4s ease forwards;
}
.file-icon-link {
  display: flex;
  width: 100%;
  height: 100%;
  align-items: center;
  justify-content: center;
  color: rgba(148, 163, 184, 0.9);
  transition: color 0.2s ease;
}
.file-icon-link:hover {
  color: #f8fafc;
}
.file-icon {
  width: 64px;
  height: 64px;
}
.file-icon svg {
  width: 100%;
  height: 100%;
  stroke: currentColor;
  stroke-width: 1.6;
  fill: none;
}
.file-details {
  padding: 14px 16px 18px;
  text-align: left;
}
.filename {
  font-weight: 600;
  font-size: 0.92rem;
  color: #38bdf8;
  text-decoration: none;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.filename:hover {
  text-decoration: underline;
}
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  padding: 8px 14px;
  border-radius: 999px;
  color: #f8fafc;
  font-weight: 600;
  background: linear-gradient(120deg, rgba(234, 179, 8, 0.35), rgba(59, 130, 246, 0.45));
  border: 1px solid rgba(234, 179, 8, 0.5);
}
.loading-state,
.empty-state {
  padding: 18px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px dashed rgba(148, 163, 184, 0.3);
  color: rgba(226, 232, 240, 0.7);
  text-align: center;
}
.loading-state {
  display: flex;
  align-items: center;
  gap: 16px;
  text-align: left;
}
.loading-copy p {
  margin: 0;
  font-weight: 600;
  color: #e0f2fe;
}
.loading-copy small {
  color: rgba(226, 232, 240, 0.65);
}
.spinner-ring {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  position: relative;
  border: 2px solid rgba(59, 130, 246, 0.2);
}
.spinner-ring span {
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: #8b5cf6;
  animation: spin 0.9s linear infinite;
}
.image-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.92);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2200;
  padding: 20px;
  backdrop-filter: blur(4px);
}
.image-modal-content {
  position: relative;
  max-width: 80vw;
  max-height: 80vh;
  background: rgba(8, 13, 27, 0.95);
  border-radius: 28px;
  padding: 24px;
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.75);
  border: 1px solid rgba(59, 130, 246, 0.35);
}
.image-modal-content img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 18px;
  object-fit: contain;
}
.close-button {
  position: absolute;
  top: 12px;
  right: 18px;
  font-size: 2rem;
  color: rgba(148, 163, 184, 0.7);
  cursor: pointer;
  transition: color 0.2s ease, transform 0.2s ease;
}
.close-button:hover {
  color: #fff;
  transform: scale(1.05);
}
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.spinner-ring span {
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #38bdf8;
  border-right-color: #8b5cf6;
  animation: spin 0.9s linear infinite;
}
@media (max-width: 768px) {
  .evidence-container {
    padding: 26px;
  }
  .evidence-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .upload-controls {
    flex-direction: column;
  }
  .content-grid {
    grid-template-columns: 1fr;
  }
  .evidence-section {
    max-height: none;
  }
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes glowPulse {
  from {
    box-shadow: 0 0 15px rgba(34, 197, 94, 0.2);
  }
  to {
    box-shadow: 0 0 25px rgba(34, 197, 94, 0.45);
  }
}
@keyframes dotPulse {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  50% {
    transform: scale(1.3);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0.8;
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.98);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
