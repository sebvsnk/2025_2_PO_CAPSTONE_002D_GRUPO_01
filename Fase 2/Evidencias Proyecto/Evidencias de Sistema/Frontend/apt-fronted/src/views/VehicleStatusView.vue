<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const API_BASE_URL = import.meta.env.VITE_API_URL

const myOts = ref([])
const isLoading = ref(true)
const errorMsg = ref(null)

const formatDate = (dateString) => {
  if (!dateString) return 'Pendiente'
  return new Date(dateString).toLocaleString('es-CL', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const fetchMyStatus = async () => {
  isLoading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/mi-estado/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!res.ok) throw new Error('No se pudo cargar el estado.')
    myOts.value = await res.json()
  } catch (e) {
    errorMsg.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchMyStatus)
</script>

<template>
  <div class="status-page">
    <header class="page-header">
      <button class="back-button" @click="router.push({ name: 'Dashboard' })">← Volver</button>
      <div class="header-content">
        <p class="eyebrow">Mi Vehículo</p>
        <h1>Estado de Mantención</h1>
      </div>
    </header>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner-aurora"></div>
      <p>Buscando información de tu vehículo...</p>
    </div>

    <div v-else-if="errorMsg" class="error-card">
      {{ errorMsg }}
    </div>

    <div v-else-if="myOts.length === 0" class="empty-state glass-card">
      <div class="icon-empty">🚛</div>
      <h3>Todo en orden</h3>
      <p>Tu vehículo asignado no tiene órdenes de trabajo activas en este momento.</p>
    </div>

    <div v-else class="ots-container">
      <div v-for="ot in myOts" :key="ot.id" class="glass-card ot-card">
        <div class="ot-header">
          <div>
            <span class="ot-id">OT #{{ ot.id }}</span>
            <h2 class="vehicle-title">{{ ot.vehiculo?.marca }} {{ ot.vehiculo?.modelo }}</h2>
            <span class="patente-badge">{{ ot.vehiculo?.patente }}</span>
          </div>
          <div class="status-badge" :class="ot.estado.code.toLowerCase()">
            {{ ot.estado.label }}
          </div>
        </div>

        <div class="timeline-wrapper">
          <ul class="timeline">
            <li class="timeline-item">
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
              <span class="date">{{ formatDate(ot.fecha_apertura) }}</span>
              <span class="title">Ingreso a Taller</span>
              <span class="desc">{{ ot.descripcion }}</span>
            </li>

            <li
              v-for="(tarea, idx) in ot.tareas"
              :key="tarea.id"
              class="timeline-item"
              :style="`--delay: ${idx * 0.1}s`"
            >
              <span class="icon-wrapper" :class="tarea.estado?.code?.toLowerCase()">
                <svg
                  v-if="tarea.estado?.code === 'HECHA'"
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="3"
                >
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </span>
              <span class="date">{{ tarea.estado?.label }}</span>
              <span class="title">{{ tarea.nombre }}</span>
            </li>

            <li class="timeline-item current-status">
              <span class="icon-wrapper pulse" :class="ot.estado.code.toLowerCase()">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                >
                  <circle cx="12" cy="12" r="10"></circle>
                  <circle cx="12" cy="12" r="3"></circle>
                </svg>
              </span>
              <span class="date">Ahora</span>
              <span class="title">En {{ ot.estado.label }}</span>
              <span class="desc">
                {{
                  ot.estado.code === 'ACTIVA'
                    ? 'Los mecánicos están trabajando.'
                    : 'Esperando actualización.'
                }}
              </span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Layout y Fondo */
.status-page {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 60px;
  color: #e2e8f0;
}

.page-header {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 30px;
}

.back-button {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.3);
  color: #cbd5e1;
  padding: 8px 16px;
  border-radius: 99px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}
.back-button:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #38bdf8;
  color: white;
}

.eyebrow {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: #94a3b8;
  margin: 0 0 4px;
}
h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #f8fafc;
}

/* Tarjetas Glass */
.glass-card {
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.6));
  border: 1px solid rgba(120, 172, 255, 0.2);
  border-radius: 24px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(12px);
  padding: 24px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  animation: slideUp 0.5s ease-out;
}
/* Brillo Aurora sutil */
.glass-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.15), transparent 70%);
  filter: blur(40px);
  pointer-events: none;
}

.ot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
  padding-bottom: 16px;
  margin-bottom: 20px;
}

.ot-id {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}
.vehicle-title {
  margin: 0;
  font-size: 1.4rem;
  color: #fff;
}
.patente-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  font-family: monospace;
  font-weight: 700;
  color: #cbd5e1;
  letter-spacing: 1px;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 99px;
  font-weight: 700;
  font-size: 0.9rem;
  text-transform: uppercase;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
}
.status-badge.activa {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}
.status-badge.pausada {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
}

/* Timeline (Estilo Aurora) */
.timeline {
  list-style: none;
  padding: 0 0 0 10px;
  margin: 0;
  position: relative;
}
.timeline::before {
  content: '';
  position: absolute;
  left: 29px; /* Ajustado al centro del icono */
  top: 10px;
  bottom: 20px;
  width: 2px;
  background: linear-gradient(to bottom, rgba(59, 130, 246, 0.5), rgba(59, 130, 246, 0.1));
}

.timeline-item {
  position: relative;
  padding-left: 60px;
  padding-bottom: 24px;
  opacity: 0;
  animation: fadeInItem 0.4s ease forwards;
  animation-delay: var(--delay, 0s);
}

.icon-wrapper {
  position: absolute;
  left: 10px;
  top: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.9);
  border: 2px solid rgba(71, 85, 105, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  z-index: 2;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

/* Colores de Iconos */
.icon-wrapper.activa {
  border-color: #3b82f6;
  color: #3b82f6;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
}
.icon-wrapper.hecha {
  border-color: #10b981;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}
.icon-wrapper.pausada {
  border-color: #f59e0b;
  color: #f59e0b;
}
.icon-wrapper.pulse {
  animation: pulseRing 2s infinite;
}

.date {
  font-size: 0.8rem;
  color: #94a3b8;
  display: block;
  margin-bottom: 2px;
}
.title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #f1f5f9;
  display: block;
}
.desc {
  font-size: 0.9rem;
  color: #cbd5e1;
  margin-top: 2px;
  display: block;
  line-height: 1.4;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px;
}
.icon-empty {
  font-size: 3rem;
  margin-bottom: 10px;
  opacity: 0.5;
}

/* Loading Spinner Aurora */
.loading-container {
  text-align: center;
  padding: 40px;
}
.spinner-aurora {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #3b82f6;
  border-right-color: #10b981;
  margin: 0 auto 15px;
  animation: spin 1s linear infinite;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes fadeInItem {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
@keyframes pulseRing {
  0% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0);
  }
}

@media (max-width: 600px) {
  .ot-header {
    flex-direction: column;
    gap: 10px;
  }
  .status-badge {
    align-self: flex-start;
  }
}
</style>
