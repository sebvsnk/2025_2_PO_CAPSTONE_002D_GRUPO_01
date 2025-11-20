<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

const otForm = ref({
  vehiculo: null, // Guardará el ID del vehículo
  patente: '', // Usaremos esto para la búsqueda
  descripcion: '',
})

const vehiculosDisponibles = ref([])
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL

// Función para obtener la lista de vehículos disponibles para sugerencias
const fetchVehiculos = async () => {
  isLoading.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/vehiculos/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (response.ok) {
      vehiculosDisponibles.value = await response.json()
    }
  } catch (error) {
    console.error('Error al cargar lista de vehículos:', error)
    // No es un error crítico si falla, pero el selector estará vacío.
  } finally {
    // Mantener isLoading en false para la carga de OT, solo si no hay otro error
    if (!errorMsg.value) isLoading.value = false
  }
}

// Función para manejar la creación de la OT (RF-OT-01)
const handleCreateOt = async () => {
  isSubmitting.value = true
  errorMsg.value = null
  successMsg.value = null

  // 1. Buscar y validar la patente ingresada en la lista de sugerencias
  const vehiculoSeleccionado = vehiculosDisponibles.value.find(
    (v) => v.patente === otForm.value.patente.toUpperCase(),
  )

  if (!vehiculoSeleccionado) {
    errorMsg.value =
      'Patente no encontrada o no válida en el sistema. Asegúrese de seleccionar una de la lista.'
    isSubmitting.value = false
    return
  }

  // 2. Validar que no exista una OT activa para este vehículo
  try {
    const checkUrl = `${API_BASE_URL}/ot/?vehiculo=${vehiculoSeleccionado.id}`
    const checkResponse = await fetch(checkUrl, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (checkResponse.ok) {
      const checkData = await checkResponse.json()
      const lista = Array.isArray(checkData) ? checkData : checkData.results || []
      const abiertas = lista.filter((ot) => {
        const estado = (ot.estado?.code || ot.estado || '').toUpperCase()
        const patenteOt = (ot.vehiculo?.patente || '').toUpperCase()
        const patenteInput = vehiculoSeleccionado.patente.toUpperCase()
        return patenteOt === patenteInput && estado !== 'CERRADA'
      })
      if (abiertas.length > 0) {
        const otActiva = abiertas[0]
        errorMsg.value = `Ya existe una OT activa para esta patente (OT #${
          otActiva.numero_ot || otActiva.id || vehiculoSeleccionado.patente
        }). No puedes crear otra.`
        isSubmitting.value = false
        return
      }
    }
  } catch (checkError) {
    console.warn('No se pudo validar OT activa, se intentará crear igualmente.', checkError)
  }

  // 3. Crear payload
  // El serializer en Django espera el campo 'vehiculo' con el ID.
  const payload = {
    vehiculo: vehiculoSeleccionado.id, // ID del vehículo
    descripcion: otForm.value.descripcion,
  }

  try {
    const response = await fetch(`${API_BASE_URL}/ot/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()

    if (!response.ok) {
      // Capturamos el error de unicidad (RF-OT-04: Ya existe una OT activa)
      errorMsg.value =
        data.detail ||
        (data.non_field_errors ? data.non_field_errors[0] : 'Error de validación al crear OT.')
      throw new Error('Fallo al crear OT.')
    }

    const otLabel = data.numero_ot || data.id || vehiculoSeleccionado.patente
    successMsg.value = `Orden de Trabajo (OT) #${otLabel} creada con éxito.`

    // Opcional: Redirigir al tablero después de 2 segundos
    setTimeout(() => {
      // Redirigir al Tablero Kanban
      router.push({ name: 'SupervisorDashboard' })
    }, 2000)
  } catch (error) {
    if (!errorMsg.value) {
      errorMsg.value = `Error: ${error.message}`
    }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchVehiculos()
  } else {
    router.push({ name: 'Login' })
  }
})
</script>

<template>
  <section class="ot-create-wrapper">
    <div class="ot-create-container">
      <header class="ot-create-header">
        <button class="back-button" @click="router.push({ name: 'SupervisorDashboard' })">
          &larr; Volver al Tablero
        </button>
        <div class="header-copy">
          <p class="eyebrow">Nueva OT</p>
          <h1>Crear Orden de Trabajo (OT)</h1>
          <p class="helper-text">
            Selecciona un vehículo registrado y deja una descripción clara para que el equipo pueda actuar rápido.
          </p>
        </div>
      </header>

      <Transition name="fade-slide" mode="out-in">
        <div v-if="isLoading" key="loading" class="loading-state">
          <span class="spinner" aria-hidden="true"></span>
          <p>Cargando lista de vehículos...</p>
        </div>

        <form v-else key="form" class="ot-form" @submit.prevent="handleCreateOt">
          <p class="form-hint">
            Los campos se guardan al enviar. Puedes editar cualquier dato hasta confirmar la creación de la OT.
          </p>

          <div v-if="errorMsg" class="status-banner error" role="alert">{{ errorMsg }}</div>
          <div v-if="successMsg" class="status-banner success" role="status">{{ successMsg }}</div>

          <div class="form-group">
            <label for="patente">Patente del Vehículo</label>
            <div class="input-shell">
              <input
                id="patente"
                v-model="otForm.patente"
                type="text"
                placeholder="Ej: BBTT-34"
                required
                list="vehiculos-list"
                :disabled="isSubmitting"
              />
              <datalist id="vehiculos-list">
                <option v-for="v in vehiculosDisponibles" :key="v.id" :value="v.patente">
                  {{ v.marca || v.modelo || 'Vehículo' }}
                </option>
              </datalist>
            </div>
            <p class="note">
              Debe existir previamente en el sistema. Usa el autocompletado o copia la patente exacta.
            </p>
          </div>

          <div class="form-group">
            <label for="descripcion">Descripción / Motivo</label>
            <div class="input-shell">
              <textarea
                id="descripcion"
                v-model="otForm.descripcion"
                placeholder="Mantenimiento preventivo, cambio de aceite, etc."
                rows="4"
                :disabled="isSubmitting"
              ></textarea>
            </div>
            <p class="note">Sé concreto: qué sucede y qué esperas que se revise o corrija.</p>
          </div>

          <button type="submit" :disabled="isSubmitting" class="submit-button">
            {{ isSubmitting ? 'Creando OT...' : 'Crear Orden de Trabajo' }}
          </button>
        </form>
      </Transition>
    </div>
  </section>
</template>

<style scoped>
.ot-create-wrapper {
  min-height: calc(100vh - 180px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 40px 18px 90px;
}

.ot-create-container {
  width: 100%;
  max-width: 520px;
  position: relative;
  border-radius: 28px;
  padding: 32px;
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.82));
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 30px 60px rgba(2, 6, 23, 0.65);
  overflow: hidden;
  animation: cardAppear 0.55s ease;
}
.ot-create-container::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(59, 130, 246, 0.15);
  pointer-events: none;
}
.ot-create-container::after {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(74, 222, 128, 0.35), transparent 60%);
  top: -80px;
  right: -60px;
  filter: blur(8px);
  animation: shimmer 8s linear infinite;
}

.ot-create-header {
  display: flex;
  gap: 18px;
  align-items: flex-start;
  margin-bottom: 26px;
}
.header-copy {
  flex: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.18em;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 6px;
}
.ot-create-header h1 {
  margin: 0;
  font-size: 1.65rem;
  color: #f8fafc;
}
.helper-text {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.9);
  font-size: 0.95rem;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.5);
  color: #e2e8f0;
  font-weight: 600;
  cursor: pointer;
  transition: border 0.2s ease, background 0.2s ease, transform 0.2s ease;
}
.back-button:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.6);
  transform: translateY(-1px);
}
.back-button:focus-visible {
  outline: 2px solid rgba(14, 165, 233, 0.9);
  outline-offset: 3px;
}

.ot-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
  position: relative;
  z-index: 1;
}
.form-hint {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(148, 163, 184, 0.85);
}

.status-banner {
  padding: 12px 14px;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid transparent;
  animation: fadeIn 0.35s ease;
}
.status-banner.error {
  color: #fecaca;
  background: rgba(248, 113, 113, 0.12);
  border-color: rgba(248, 113, 113, 0.35);
}
.status-banner.success {
  color: #bbf7d0;
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.35);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.form-group label {
  font-size: 0.95rem;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.95);
}
.input-shell {
  border: 1px solid rgba(148, 163, 184, 0.32);
  border-radius: 16px;
  padding: 12px 16px;
  background: rgba(15, 23, 42, 0.6);
  transition: border 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.input-shell:focus-within {
  border-color: rgba(56, 189, 248, 0.9);
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.15);
  transform: translateY(-1px);
}

.input-shell input,
.input-shell textarea {
  width: 100%;
  background: transparent;
  border: none;
  outline: none;
  color: #f8fafc;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
}
.input-shell textarea {
  min-height: 140px;
}

.note {
  margin: -2px 0 0;
  font-size: 0.8rem;
  color: rgba(148, 163, 184, 0.9);
}

.submit-button {
  border: none;
  padding: 14px 0;
  border-radius: 18px;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #0c111d;
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.25s ease, filter 0.2s ease;
  box-shadow: 0 15px 35px rgba(14, 165, 233, 0.25);
}
.submit-button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 25px 45px rgba(14, 165, 233, 0.35);
}
.submit-button:disabled {
  cursor: not-allowed;
  filter: grayscale(0.4);
  opacity: 0.7;
  box-shadow: none;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  padding: 40px 0;
  color: #f8fafc;
}
.spinner {
  width: 54px;
  height: 54px;
  border: 4px solid rgba(148, 163, 184, 0.25);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes shimmer {
  0% {
    transform: translate(-20px, 0);
  }
  50% {
    transform: translate(-60px, 30px);
  }
  100% {
    transform: translate(0, -20px);
  }
}
@keyframes cardAppear {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 640px) {
  .ot-create-container {
    padding: 24px;
  }
  .ot-create-header {
    flex-direction: column;
  }
  .back-button {
    width: 100%;
    justify-content: center;
  }
}
</style>




