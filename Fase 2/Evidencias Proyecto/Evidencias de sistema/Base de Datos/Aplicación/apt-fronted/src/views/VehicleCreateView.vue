<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()
const API_BASE_URL = import.meta.env.VITE_API_URL

// Estado del Formulario
const formVehiculo = ref({
  patente: '',
  marca: '',
  modelo: '',
})

// Datos para Chofer Nuevo
const formChoferNuevo = ref({
  nombre: '',
  rut: '',
  numero_telefonico: '',
  email: '',
})

// Datos para Chofer Existente
const selectedDriverId = ref(null)
const existingDrivers = ref([])

// Opciones: 'new' | 'existing' | 'none'
const driverOption = ref('new')

const isSubmitting = ref(false)
const isLoadingDrivers = ref(false)
const errorMsg = ref(null)

// Estado para animación de éxito
const showSuccessCheck = ref(false)
const successCheckText = ref('')

// --- VALIDACIONES Y FORMATEO ---

// 1. RUT (Formato y Validación)
const formatearRut = (event) => {
  let valor = event.target.value.replace(/[^0-9kK]/g, '').toUpperCase()
  if (valor.length > 9) valor = valor.slice(0, 9)
  if (valor.length > 1) {
    const cuerpo = valor.slice(0, -1)
    const dv = valor.slice(-1)
    valor = `${cuerpo}-${dv}`
  }
  formChoferNuevo.value.rut = valor
  event.target.value = valor
}

// Validación estricta del dígito verificador (Módulo 11)
const esRutValido = (rut) => {
  if (!rut || rut.length < 8) return false
  const cleanRut = rut.replace(/[^0-9kK]/g, '').toUpperCase()
  const cuerpo = cleanRut.slice(0, -1)
  const dv = cleanRut.slice(-1)
  if (!/^\d+$/.test(cuerpo)) return false

  let suma = 0
  let multiplo = 2
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo.charAt(i)) * multiplo
    multiplo = multiplo < 7 ? multiplo + 1 : 2
  }
  const dvEsperado = 11 - (suma % 11)
  const dvCalc = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString()
  return dv === dvCalc
}

// 2. Patente (Solo Alfanumérico)
const formatearPatente = (event) => {
  let valor = event.target.value.replace(/[^a-zA-Z0-9]/g, '').toUpperCase()
  if (valor.length > 6) valor = valor.slice(0, 6) // Patentes chile max 6 chars
  formVehiculo.value.patente = valor
  event.target.value = valor
}

// 3. Teléfono (+569 fijo)
const formatearTelefono = (event) => {
  let valor = event.target.value.replace(/\D/g, '')
  if (valor.startsWith('569')) valor = valor.substring(3)
  if (valor.length > 8) valor = valor.slice(0, 8)
  const resultado = valor ? '+569' + valor : ''
  formChoferNuevo.value.numero_telefonico = resultado
  if (!valor) event.target.value = ''
}

// 4. Cargar Choferes Libres
const loadDrivers = async () => {
  isLoadingDrivers.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/admin/usuarios/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (res.ok) {
      const users = await res.json()
      existingDrivers.value = users.filter((u) => u.rol === 'CHOFER' && !u.vehiculo_actual)
    }
  } catch (error) {
    console.error('Error cargando choferes:', error)
  } finally {
    isLoadingDrivers.value = false
  }
}

// --- LÓGICA DE GUARDADO ---
const handleSubmit = async () => {
  isSubmitting.value = true
  errorMsg.value = null

  try {
    // Validación Vehículo
    if (!formVehiculo.value.patente || formVehiculo.value.patente.length < 5) {
      throw new Error('La patente del vehículo es inválida o muy corta.')
    }

    let finalChoferId = null

    // Validación Chofer Nuevo
    if (driverOption.value === 'new') {
      if (
        !formChoferNuevo.value.nombre ||
        !formChoferNuevo.value.rut ||
        !formChoferNuevo.value.email
      ) {
        throw new Error('Nombre, RUT y Email son obligatorios para el nuevo chofer.')
      }
      if (!esRutValido(formChoferNuevo.value.rut)) {
        throw new Error('El RUT ingresado no es válido. Revise el dígito verificador.')
      }

      const choferPayload = {
        nombre: formChoferNuevo.value.nombre,
        rut: formChoferNuevo.value.rut,
        numero_telefonico: formChoferNuevo.value.numero_telefonico,
        email: formChoferNuevo.value.email,
      }

      const resChofer = await fetch(`${API_BASE_URL}/usuarios/contacto-chofer/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token}` },
        body: JSON.stringify(choferPayload),
      })
      const dataChofer = await resChofer.json()
      if (!resChofer.ok) throw new Error(dataChofer.detail || 'Error al crear chofer.')
      finalChoferId = dataChofer.id
    }

    // Validación Chofer Existente
    else if (driverOption.value === 'existing') {
      if (!selectedDriverId.value) {
        throw new Error('Debes seleccionar un chofer de la lista.')
      }
      finalChoferId = selectedDriverId.value
    }

    // Crear Vehículo
    const vehiculoPayload = {
      patente: formVehiculo.value.patente,
      marca: formVehiculo.value.marca,
      modelo: formVehiculo.value.modelo,
      chofer_id: finalChoferId,
    }

    const resVehiculo = await fetch(`${API_BASE_URL}/vehiculos/crear/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authStore.token}` },
      body: JSON.stringify(vehiculoPayload),
    })
    const dataVehiculo = await resVehiculo.json()

    if (!resVehiculo.ok) {
      let detalle = dataVehiculo.detail || 'Error al crear vehículo.'
      if (dataVehiculo.patente) detalle = `Patente: ${dataVehiculo.patente[0]}`
      throw new Error(detalle)
    }

    // Éxito + Animación
    successCheckText.value = `Vehículo ${dataVehiculo.patente} Registrado`
    showSuccessCheck.value = true

    setTimeout(() => router.push('/vehiculos'), 2000)
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadDrivers()
})
</script>

<template>
  <section class="vehicle-create-wrapper">
    <div class="vehicle-card glass-panel">
      <header class="vehicle-header">
        <button class="back-button" @click="router.push('/vehiculos')">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="m15 18-6-6 6-6" />
          </svg>
          Volver
        </button>
        <div class="header-copy">
          <p class="eyebrow">FLOTA</p>
          <h1>Ingresar Vehículo</h1>
        </div>
      </header>

      <div class="vehicle-form">
        <section class="form-section">
          <header class="section-header">
            <div class="icon-box driver">
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
                <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
            </div>
            <div>
              <h2>Asignación de Chofer</h2>
              <p>Define quién conducirá este vehículo.</p>
            </div>
          </header>

          <div class="tabs-container">
            <button
              type="button"
              class="tab-btn"
              :class="{ active: driverOption === 'new' }"
              @click="driverOption = 'new'"
            >
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
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                <circle cx="8.5" cy="7" r="4" />
                <line x1="20" y1="8" x2="20" y2="14" />
                <line x1="23" y1="11" x2="17" y2="11" />
              </svg>
              Nuevo
            </button>
            <button
              type="button"
              class="tab-btn"
              :class="{ active: driverOption === 'existing' }"
              @click="driverOption = 'existing'"
            >
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
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              Existente
            </button>
            <button
              type="button"
              class="tab-btn"
              :class="{ active: driverOption === 'none' }"
              @click="driverOption = 'none'"
            >
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
                <circle cx="12" cy="12" r="10" />
                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
              </svg>
              Ninguno
            </button>
          </div>

          <div class="panel-body">
            <Transition name="fade" mode="out-in">
              <div v-if="driverOption === 'new'" key="new" class="form-grid two-cols">
                <div class="form-group">
                  <label>Nombre Completo</label>
                  <div class="input-shell">
                    <input v-model="formChoferNuevo.nombre" placeholder="Ej: Juan Pérez" />
                  </div>
                </div>
                <div class="form-group">
                  <label>RUT (Obligatorio)</label>
                  <div class="input-shell">
                    <input
                      :value="formChoferNuevo.rut"
                      placeholder="12345678-9"
                      maxlength="12"
                      @input="formatearRut"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label>Email (Obligatorio)</label>
                  <div class="input-shell">
                    <input
                      v-model="formChoferNuevo.email"
                      type="email"
                      placeholder="correo@ejemplo.com"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label>Teléfono</label>
                  <div class="input-shell">
                    <input
                      :value="formChoferNuevo.numero_telefonico"
                      placeholder="+569..."
                      type="tel"
                      @input="formatearTelefono"
                    />
                  </div>
                </div>
              </div>

              <div
                v-else-if="driverOption === 'existing'"
                key="existing"
                class="form-group full-span"
              >
                <label>Seleccionar Chofer Libre</label>
                <div class="select-wrapper">
                  <select v-model="selectedDriverId" class="driver-select">
                    <option :value="null">-- Seleccionar de la lista --</option>
                    <option v-for="d in existingDrivers" :key="d.id" :value="d.id">
                      {{ d.nombre }} (RUT: {{ d.rut || 'S/R' }})
                    </option>
                  </select>
                </div>
                <p v-if="existingDrivers.length === 0 && !isLoadingDrivers" class="helper-warning">
                  ⚠️ No hay choferes sin vehículo asignado.
                </p>
              </div>

              <div v-else key="none" class="empty-message">
                <div class="icon-placeholder">🚛</div>
                <p>El vehículo se creará <strong>sin chofer asignado</strong>.</p>
                <span class="sub-text">Podrás asignarlo más tarde en "Gestión de Vehículos".</span>
              </div>
            </Transition>
          </div>
        </section>

        <section class="form-section">
          <header class="section-header">
            <div class="icon-box vehicle">
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
                <rect width="16" height="16" x="4" y="4" rx="2" ry="2" />
                <rect width="4" height="4" x="9" y="9" rx="1" />
              </svg>
            </div>
            <div>
              <h2>Datos del Vehículo</h2>
              <p>Información técnica para el registro.</p>
            </div>
          </header>
          <div class="form-grid two-cols">
            <div class="form-group">
              <label>Patente (Sin símbolos)</label>
              <div class="input-shell">
                <input
                  :value="formVehiculo.patente"
                  class="input-patente"
                  placeholder="AAAA12"
                  maxlength="6"
                  @input="formatearPatente"
                />
              </div>
            </div>
            <div class="form-group">
              <label>Marca</label>
              <div class="input-shell">
                <input v-model="formVehiculo.marca" placeholder="Ej: Scania" />
              </div>
            </div>
            <div class="form-group full-span">
              <label>Modelo</label>
              <div class="input-shell">
                <input v-model="formVehiculo.modelo" placeholder="Ej: R500" />
              </div>
            </div>
          </div>
        </section>

        <Transition name="fade">
          <div v-if="errorMsg" class="status-banner error">
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
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            {{ errorMsg }}
          </div>
        </Transition>

        <button :disabled="isSubmitting" class="submit-button-neon" @click="handleSubmit">
          <span v-if="!isSubmitting">Guardar Registro</span>
          <div v-else class="btn-content"><span class="spinner-mini"></span> Guardando...</div>
        </button>
      </div>
    </div>

    <Transition name="modal-fade">
      <div v-if="showSuccessCheck" class="success-overlay">
        <div class="success-content">
          <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none" />
            <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
          </svg>
          <h3>{{ successCheckText }}</h3>
        </div>
      </div>
    </Transition>
  </section>
</template>

<style scoped>
/* --- 1. Layout & Glass Panel --- */
.vehicle-create-wrapper {
  min-height: 90vh;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
  color: #e2e8f0;
}

.glass-panel {
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 32px;
  box-shadow: 0 35px 80px rgba(2, 6, 23, 0.6);
  width: 100%;
  max-width: 680px;
  padding: 40px;
  position: relative;
  overflow: hidden;
}
/* Brillo superior */
.glass-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.5), transparent);
}

/* --- 2. Header --- */
.vehicle-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  padding-bottom: 20px;
}
.back-button {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.back-button:hover {
  background: rgba(56, 189, 248, 0.15);
  border-color: rgba(56, 189, 248, 0.4);
  color: #e2e8f0;
}
.eyebrow {
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: #38bdf8;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0 0 4px;
  text-align: right;
}
.header-copy h1 {
  margin: 0;
  font-size: 1.8rem;
  color: #f8fafc;
  text-align: right;
}

/* --- 3. Form Sections --- */
.form-section {
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 20px;
  padding: 24px;
  margin-bottom: 24px;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}
.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.icon-box.driver {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}
.icon-box.vehicle {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.section-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #f1f5f9;
}
.section-header p {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: #94a3b8;
}

/* --- 4. Tabs --- */
.tabs-container {
  display: flex;
  background: rgba(15, 23, 42, 0.6);
  padding: 4px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  margin-bottom: 20px;
}
.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn.active {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  box-shadow: 0 2px 8px rgba(56, 189, 248, 0.1);
}
.tab-btn:hover:not(.active) {
  color: #e2e8f0;
}

/* --- 5. Inputs --- */
.form-grid {
  display: grid;
  gap: 16px;
}
.two-cols {
  grid-template-columns: 1fr 1fr;
}
.full-span {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  color: #cbd5e1;
  margin-bottom: 6px;
  font-weight: 500;
}
.input-shell {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 12px;
  padding: 0 14px;
  transition: all 0.2s;
}
.input-shell:focus-within {
  border-color: #38bdf8;
  box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
  background: rgba(15, 23, 42, 0.8);
}
.input-shell input,
.driver-select {
  width: 100%;
  height: 46px;
  background: transparent;
  border: none;
  color: #f8fafc;
  font-size: 0.95rem;
  outline: none;
}
.input-patente {
  font-family: monospace;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 700;
  color: #fbbf24 !important; /* Amber for license plate */
}
.driver-select option {
  background: #0f172a;
  color: #e2e8f0;
}

/* --- 6. Empty State --- */
.empty-message {
  text-align: center;
  padding: 30px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 16px;
  border: 1px dashed rgba(148, 163, 184, 0.3);
}
.icon-placeholder {
  font-size: 2.5rem;
  margin-bottom: 10px;
}
.helper-warning {
  color: #fbbf24;
  font-size: 0.85rem;
  margin-top: 8px;
}

/* --- 7. Error Banner --- */
.status-banner.error {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 14px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

/* --- 8. Submit Button Neon --- */
.submit-button-neon {
  width: 100%;
  height: 54px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  color: white;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.4);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.submit-button-neon:hover:not(:disabled) {
  box-shadow: 0 0 30px rgba(59, 130, 246, 0.6);
  transform: translateY(-2px);
}
.submit-button-neon:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #1e293b;
  box-shadow: none;
}
.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.spinner-mini {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* --- 9. Success Overlay --- */
.success-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}
.success-content {
  background: rgba(15, 23, 42, 0.95);
  padding: 40px 60px;
  border-radius: 30px;
  text-align: center;
  border: 1px solid rgba(34, 197, 94, 0.3);
  box-shadow: 0 0 50px rgba(34, 197, 94, 0.2);
}
.checkmark {
  width: 80px;
  height: 80px;
  display: block;
  stroke-width: 3;
  stroke: #22c55e;
  margin: 0 auto 20px;
}
.checkmark__circle {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}
.checkmark__check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

/* Keyframes & Animations */
@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-active {
  transition: all 0.4s ease;
}
.modal-fade-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

@media (max-width: 640px) {
  .two-cols {
    grid-template-columns: 1fr;
  }
  .tabs-container {
    flex-direction: column;
  }
}
</style>
