<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_URL

const patenteInput = ref('')
const otStatus = ref(null) // AquÃ­ guardaremos el resultado
const isLoading = ref(false)
const errorMsg = ref(null)

// Propiedad computada para el color (para los estilos)
const timelineClass = computed(() => {
  // Â¡AÃ±adimos '?' para evitar el crash si 'estado' es null!
  if (!otStatus.value || !otStatus.value.estado) return 'timeline-activa'
  switch (otStatus.value.estado.code) {
    case 'CERRADA':
      return 'timeline-cerrada'
    case 'ANULADA':
      return 'timeline-anulada'
    case 'PAUSADA':
      return 'timeline-pausada'
    case 'ACTIVA':
    default:
      return 'timeline-activa'
  }
})

const handleSearch = async () => {
  const patenteParaApi = patenteInput.value.toUpperCase().replace(/[-\s]/g, '')

  if (!patenteParaApi) {
    errorMsg.value = 'Por favor, ingresa una patente.'
    return
  }

  isLoading.value = true
  errorMsg.value = null
  otStatus.value = null

  try {
    const url = `${API_BASE_URL}/public/status/${patenteParaApi}/` // URL Corregida
    const response = await fetch(url)

    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.detail || 'Error al buscar la patente.')
    }

    otStatus.value = data
  } catch (error) {
    console.error(error)
    errorMsg.value = error.message
  } finally {
    isLoading.value = false
  }
}

// Helper para formatear fechas
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Limpiar la bÃºsqueda
const clearSearch = () => {
  otStatus.value = null
  patenteInput.value = ''
  errorMsg.value = null
}
</script>

<template>
  <div class="public-container">
    <div class="status-box">
      <a href="#" class="back-link" @click.prevent="router.push('/login')"> ← Volver al Login </a>

      <Transition name="fade-content" mode="out-in">
        <div v-if="!otStatus" class="search-wrapper">
          <h1>Ver Estado del Vehí­culo</h1>
          <p>Ingresa la patente de tu vehí­culo para ver el estado actual de la mantención.</p>

          <form class="search-form" @submit.prevent="handleSearch">
            <label for="patente">Patente</label>
            <input
              id="patente"
              v-model="patenteInput"
              type="text"
              placeholder="Ej: CJHD92"
              required
              @input="patenteInput = patenteInput.toUpperCase().replace(/[-\s]/g, '')"
            />
            <button type="submit" :disabled="isLoading">
              <span v-if="isLoading" class="button-spinner"></span>
              {{ isLoading ? 'Buscando...' : 'Buscar Patente' }}
            </button>
          </form>
        </div>

        <div v-else class="timeline-container">
          <h1>Estado: {{ otStatus.vehiculo?.patente || patenteInput }}</h1>
          <p :class="['status-tag', timelineClass]">
            {{ otStatus.estado?.label || 'Desconocido' }}
          </p>

          <ul class="timeline" :class="timelineClass">
            <li class="timeline-item" style="--i: 0">
              <span class="icon-wrapper activa">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              </span>
              <span class="date">{{ formatDate(otStatus.fecha_apertura) }}</span>
              <span class="title">Ingreso a Taller y Creación de OT</span>
              <span class="description"> Motivo: {{ otStatus.descripcion }} </span>
            </li>

            <template v-if="otStatus.tareas && otStatus.tareas.length > 0">
              <li
                v-for="(tarea, index) in otStatus.tareas"
                :key="tarea.id"
                class="timeline-item"
                :style="`--i: ${index + 1}`"
              >
                <span class="icon-wrapper" :class="tarea.estado?.code?.toLowerCase()">
                  <svg
                    v-if="tarea.estado?.code === 'HECHA'"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                  </svg>
                  <svg
                    v-else-if="tarea.estado?.code === 'PAUSADA'"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="10" y1="15" x2="10" y2="9"></line>
                    <line x1="14" y1="15" x2="14" y2="9"></line>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                  </svg>
                </span>

                <span class="date">Tarea: {{ tarea.estado?.label }}</span>
                <span class="title">{{ tarea.nombre }}</span>
              </li>
            </template>

            <li
              v-else-if="otStatus.estado?.code === 'ACTIVA'"
              class="timeline-item"
              :style="`--i: ${(otStatus.tareas?.length || 0) + 1}`"
            >
              <span class="icon-wrapper activa">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </span>
              <span class="date">En progreso...</span>
              <span class="title">Tareas de Mantención</span>
              <span class="description">El vehículo está siendo atendido.</span>
            </li>

            <li
              v-if="otStatus.estado?.code === 'CERRADA'"
              class="timeline-item"
              :style="`--i: ${(otStatus.tareas?.length || 0) + 1}`"
            >
              <span class="icon-wrapper cerrada">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                </svg>
              </span>
              <span class="date">{{ formatDate(otStatus.fecha_cierre) }}</span>
              <span class="title">Mantención Finalizada</span>
              <span class="description"> El vehí­culo está listo para ser retirado. </span>
            </li>

            <li v-if="otStatus.estado?.code === 'ANULADA'" class="timeline-item">
              <span class="icon-wrapper anulada">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
                </svg>
              </span>
              <span class="date">{{ formatDate(otStatus.fecha_cierre) || 'N/A' }}</span>
              <span class="title">Orden Anulada</span>
              <span class="description">
                La orden de trabajo fue anulada. Contacte al supervisor.
              </span>
            </li>
          </ul>

          <button class="back-button" @click="clearSearch">Buscar otra patente</button>
        </div>
      </Transition>

      <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
    </div>
  </div>
</template>

<style scoped>
/* Aurora Dark Glass para Consulta de Estado */
.public-container {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(24px, 4vw, 72px);
  overflow: hidden;
  color: #e5e7eb;
  background:
    radial-gradient(1200px 800px at 15% 15%, rgba(59, 130, 246, 0.18), transparent 60%),
    radial-gradient(1100px 900px at 80% 10%, rgba(34, 211, 238, 0.16), transparent 60%),
    linear-gradient(135deg, #0a1224, #0b1430 45%, #0b1a36 70%, #081021);
}
.public-container::before {
  content: '';
  position: absolute;
  width: 640px;
  height: 640px;
  top: -120px;
  left: -140px;
  background: radial-gradient(circle at center, rgba(34, 211, 238, 0.2) 0%, transparent 60%);
  filter: blur(12px);
  animation: orbSingle 14s ease-in-out infinite alternate;
  pointer-events: none;
}
.public-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(900px 700px at 65% 20%, rgba(49, 120, 198, 0.14), transparent 65%);
  mix-blend-mode: screen;
  opacity: 0.9;
  pointer-events: none;
}

.status-box {
  position: relative;
  width: min(560px, 88vw);
  padding: clamp(14px, 2vw, 22px);
  border-radius: 20px;
  background: linear-gradient(145deg, rgba(12, 18, 36, 0.92), rgba(9, 18, 32, 0.82));
  border: 1px solid rgba(120, 172, 255, 0.24);
  box-shadow:
    0 25px 60px rgba(0, 0, 0, 0.55),
    0 0 60px rgba(34, 211, 238, 0.18);
  backdrop-filter: blur(16px);
  overflow: hidden;
  /* AGREGA ESTAS 2 LÍNEAS: */
  animation: fadeInUp 1.5s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  opacity: 0; /* Empieza invisible para que no parpadee antes de animar */
}
.status-box::before {
  content: '';
  position: absolute;
  width: 520px;
  height: 520px;
  right: -180px;
  top: -220px;
  background: radial-gradient(circle at center, rgba(34, 211, 238, 0.2) 0%, transparent 60%);
  filter: blur(16px);
  opacity: 0.85;
  pointer-events: none;
}
.status-box::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(140deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0));
  pointer-events: none;
}

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 16px;
  padding: 8px 12px;
  color: #b9d8ff;
  font-weight: 700;
  text-decoration: none;
  letter-spacing: 0.01em;
  border: 1px solid rgba(120, 172, 255, 0.35);
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(34, 211, 238, 0.12));
  box-shadow:
    0 8px 22px rgba(0, 0, 0, 0.25),
    0 0 20px rgba(59, 130, 246, 0.18);
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.15s ease;
}
.back-link:hover {
  color: #e6f2ff;
  border-color: rgba(120, 172, 255, 0.6);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(34, 211, 238, 0.2));
  transform: translateY(-1px);
}

.search-wrapper h1,
.timeline-container h1 {
  text-align: center;
  color: #e9eefb;
  font-weight: 800;
  font-size: clamp(1.35rem, 2.4vw, 1.7rem);
  margin-bottom: 6px;
}
.search-wrapper p,
.timeline-container p {
  text-align: center;
  color: rgba(226, 232, 240, 0.8);
  margin-bottom: 16px;
  font-size: 0.95rem;
}

.search-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.search-form label {
  font-weight: 600;
  font-size: 0.88rem;
  color: rgba(226, 232, 240, 0.9);
}
.search-form input {
  width: 100%;
  max-width: 360px;
  align-self: center;
  padding: 0.8rem;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  background: rgba(9, 15, 28, 0.82);
  color: #e5e7eb;
  text-transform: uppercase;
  font-size: 1rem;
  font-weight: 500;
  text-align: center;
  transition: all 0.2s ease;
}
.search-form input::placeholder {
  color: rgba(148, 163, 184, 0.7);
}
.search-form input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow:
    0 0 0 4px rgba(56, 189, 248, 0.15),
    0 10px 40px rgba(34, 211, 238, 0.16);
}
.search-form input:-webkit-autofill,
.search-form input:-webkit-autofill:hover,
.search-form input:-webkit-autofill:focus {
  -webkit-text-fill-color: #e5e7eb;
  box-shadow: 0 0 0px 1000px rgba(9, 15, 28, 0.82) inset;
  transition: background-color 9999s ease-in-out 0s;
}
.search-form button {
  width: 100%;
  max-width: 230px;
  align-self: center;
  padding: 0.8rem;
  background: linear-gradient(135deg, #1e3a8a, #2563eb 45%, #22d3ee 100%);
  color: #f8fafc;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow:
    0 15px 40px rgba(34, 211, 238, 0.25),
    0 8px 20px rgba(37, 99, 235, 0.25);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}
.search-form button:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.02);
  box-shadow:
    0 16px 44px rgba(34, 211, 238, 0.3),
    0 10px 25px rgba(37, 99, 235, 0.28);
}
.search-form button:disabled {
  background: rgba(148, 163, 184, 0.28);
  color: rgba(226, 232, 240, 0.7);
  cursor: not-allowed;
  box-shadow: none;
}

.error-message {
  position: relative;
  margin: 1rem auto 0;
  padding: 10px 12px 10px 42px;
  border-radius: 12px;
  border: 1px solid rgba(248, 113, 113, 0.4);
  background: linear-gradient(135deg, rgba(127, 29, 29, 0.45), rgba(185, 28, 28, 0.35));
  color: #ffe4e6;
  text-align: left;
  backdrop-filter: blur(6px);
  box-shadow:
    0 10px 30px rgba(248, 113, 113, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  animation:
    alertShow 0.4s ease,
    alertGlow 2.2s ease-in-out infinite;
  max-width: 360px;
  width: 100%;
}
.error-message::before {
  content: '!';
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #fff, #fca5a5);
  color: #7f1d1d;
  font-weight: 900;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 12px rgba(248, 113, 113, 0.45);
}
.button-spinner {
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
}
.status-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 18px;
  color: #0b1224;
  border-radius: 999px;
  font-weight: 800;
  font-size: 1rem;
  background: linear-gradient(135deg, #22d3ee, #06b6d4);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.08),
    0 12px 30px rgba(34, 211, 238, 0.28);
}

.timeline {
  width: min(980px, 100%);
  list-style: none;
  padding: 0;
  margin: 4px 0 0;
  position: relative;
  background: rgba(8, 15, 30, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 18px;
  box-shadow:
    0 16px 45px rgba(0, 0, 0, 0.45),
    inset 0 1px 0 rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(14px);
  padding: 18px 14px;
  max-height: 420px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #22d3ee33 transparent;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 34px;
  top: 18px;
  bottom: 18px;
  width: 2px;
  background: linear-gradient(
    180deg,
    rgba(34, 211, 238, 0) 0%,
    rgba(34, 211, 238, 0.7) 12%,
    rgba(59, 130, 246, 0.7) 88%,
    rgba(59, 130, 246, 0) 100%
  );
  border-radius: 999px;
  opacity: 0.9;
  z-index: 0;
}
.timeline-item {
  position: relative;
  padding-left: 76px;
  padding-bottom: 26px;
  border-left: none;
  transition: color 0.3s ease;
  opacity: 0;
  transform: translateY(10px);
  animation: timelineIn 0.45s ease-out forwards;
  animation-delay: calc(var(--i, 0) * 0.08s);
}
.timeline-item::before {
  content: none;
}
.icon-wrapper {
  position: absolute;
  left: 13px;
  top: 0;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(14, 23, 42, 0.95);
  border: 3px solid rgba(148, 163, 184, 0.38);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(148, 163, 184, 0.8);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
  transition:
    border-color 0.3s ease,
    color 0.3s ease,
    transform 0.2s ease;
}
.timeline-item:hover .icon-wrapper {
  transform: translateY(-2px);
}
.timeline-item .date {
  display: block;
  font-size: 0.92rem;
  color: rgba(226, 232, 240, 0.75);
  margin-bottom: 6px;
}
.timeline-item .title {
  display: block;
  font-size: 1.08rem;
  font-weight: 800;
  color: #e9eefb;
}
.timeline-item .description {
  display: block;
  font-size: 0.95rem;
  color: rgba(226, 232, 240, 0.75);
  margin-top: 6px;
}
.back-button {
  margin-top: 16px;
  background: rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.35);
  padding: 10px 16px;
  border-radius: 12px;
  cursor: pointer;
  color: #e5e7eb;
  transition:
    border-color 0.2s ease,
    transform 0.2s ease;
}
.back-button:hover {
  border-color: rgba(148, 163, 184, 0.6);
  transform: translateY(-1px);
}

.status-tag.timeline-activa {
  background: linear-gradient(135deg, #14b8a6, #22d3ee);
  color: #052e2e;
}
.status-tag.timeline-pausada {
  background: linear-gradient(135deg, #facc15, #f9a825);
  color: #1f1300;
}
.status-tag.timeline-cerrada {
  background: linear-gradient(135deg, #22c55e, #4ade80);
  color: #062c12;
}
.status-tag.timeline-anulada {
  background: linear-gradient(135deg, #f87171, #fb7185);
  color: #300108;
}

.timeline.timeline-activa .timeline-item {
  color: #14b8a6;
}
.timeline.timeline-pausada .timeline-item {
  color: #facc15;
}
.timeline.timeline-cerrada .timeline-item {
  color: #22c55e;
}
.timeline.timeline-anulada .timeline-item {
  color: #f87171;
}

.icon-wrapper.activa,
.icon-wrapper.en_proceso,
.icon-wrapper.nueva {
  border-color: rgba(20, 184, 166, 0.85);
  color: #2dd4bf;
}
.icon-wrapper.pausada {
  border-color: rgba(250, 204, 21, 0.8);
  color: #facc15;
}
.icon-wrapper.cerrada,
.icon-wrapper.hecha {
  border-color: rgba(34, 197, 94, 0.85);
  color: #4ade80;
}
.icon-wrapper.anulada {
  border-color: rgba(248, 113, 113, 0.85);
  color: #f87171;
}

.fade-content-enter-active,
.fade-content-leave-active {
  transition: opacity 0.3s ease-out;
}
.fade-content-enter-from,
.fade-content-leave-to {
  opacity: 0;
}

.timeline::-webkit-scrollbar {
  width: 8px;
}
.timeline::-webkit-scrollbar-track {
  background: transparent;
}
.timeline::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.35), rgba(59, 130, 246, 0.4));
  border-radius: 999px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}
.timeline::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, rgba(34, 211, 238, 0.55), rgba(59, 130, 246, 0.6));
}

@keyframes timelineIn {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes orbSingle {
  0% {
    transform: translateX(0) translateY(0) scale(1);
  }
  50% {
    transform: translateX(200px) translateY(50px) scale(1.05);
  }
  100% {
    transform: translateX(380px) translateY(0) scale(0.98);
  }
}

@keyframes alertShow {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
@keyframes alertGlow {
  0% {
    box-shadow:
      0 10px 30px rgba(248, 113, 113, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }
  50% {
    box-shadow:
      0 12px 36px rgba(248, 113, 113, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.12);
  }
  100% {
    box-shadow:
      0 10px 30px rgba(248, 113, 113, 0.25),
      inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }
}

/* AGREGA LOS KEYFRAMES AL FINAL DEL CSS: */
@keyframes fadeInUp {
  0% {
    opacity: 0;
    transform: translateY(40px) scale(0.95); /* Empieza un poco abajo y pequeño */
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1); /* Termina en su lugar y tamaño normal */
  }
}
</style>
