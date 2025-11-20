<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// Estado
const userId = route.params.id
const user = ref(null)
const originalUser = ref(null)
const isLoading = ref(true)
const isSaving = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)
const actionInProgress = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL
const nombreInput = ref(null)
const rutInput = ref(null)
const telefonoInput = ref(null)

const nombreRegex = /^[A-Za-z\u00c0-\u017f\s]+$/u
const rutFormatRegex = /^\d{7,8}-[\dkK]$/
const telefonoStrictRegex = /^\+569\d{8}$/

const modalState = ref({
  type: null,
  title: '',
  message: '',
  confirmLabel: '',
})

// --- 🛡️ FUNCIONES DE VALIDACIÓN Y FORMATEO (RUT Y TELÉFONO) ---

// 1. Bloquear teclas para RUT (Solo números y K)
const bloquearTeclasNoRut = (event) => {
  const teclasPermitidas = [
    'Backspace',
    'Tab',
    'ArrowLeft',
    'ArrowRight',
    'Delete',
    'Enter',
    'Home',
    'End',
  ]
  if (teclasPermitidas.includes(event.key) || event.ctrlKey || event.metaKey) return
  if (!/^[0-9kK]$/.test(event.key)) {
    event.preventDefault()
  }
}

// 2. Formatear RUT (Auto guion y mayúsculas)
const formatearRutInput = (event) => {
  let valor = event.target.value
  // Limpiar
  valor = valor.replace(/[^0-9kK]/g, '').toUpperCase()

  // Limitar largo (8 dígitos + DV = 9 caracteres reales)
  if (valor.length > 9) {
    valor = valor.slice(0, 9)
  }

  // Poner guion
  if (valor.length > 1) {
    const cuerpo = valor.slice(0, -1)
    const dv = valor.slice(-1)
    valor = `${cuerpo}-${dv}`
  }

  // Actualizar vista y modelo
  event.target.value = valor
  if (user.value) user.value.rut = valor

  clearFieldValidity(event)
}

// 3. Bloquear teclas para Teléfono (Solo números)
const bloquearTeclasTelefono = (event) => {
  const teclasPermitidas = [
    'Backspace',
    'Tab',
    'ArrowLeft',
    'ArrowRight',
    'Delete',
    'Enter',
    'Home',
    'End',
  ]
  if (teclasPermitidas.includes(event.key) || event.ctrlKey || event.metaKey) return
  if (!/^[0-9]$/.test(event.key)) {
    event.preventDefault()
  }
}

// 4. Formatear Teléfono (+569 fijo)
const formatearTelefono = (event) => {
  let valor = event.target.value
  let numeros = valor.replace(/\D/g, '')

  // Si pegan el número completo, quitamos el 569 inicial duplicado
  if (numeros.startsWith('569')) {
    numeros = numeros.substring(3)
  }

  // Si borran todo
  if (numeros.length === 0) {
    event.target.value = ''
    if (user.value) user.value.numero_telefonico = ''
    return
  }

  // Cortar a 8 dígitos
  if (numeros.length > 8) {
    numeros = numeros.slice(0, 8)
  }

  const resultado = '+569' + numeros
  event.target.value = resultado
  if (user.value) user.value.numero_telefonico = resultado

  clearFieldValidity(event)
}

// --- FIN FUNCIONES DE FORMATEO ---

const formatearUsuario = (data) => ({
  ...data,
  nombre: data.nombre?.trim() || '',
  rut: data.rut?.trim() || '',
  numero_telefonico: data.numero_telefonico?.trim() || '',
})

const validarRut = (rut) => {
  if (typeof rut !== 'string' || !rut) return false
  const valorLimpio = rut.replace(/[.-]/g, '')
  const cuerpo = valorLimpio.slice(0, -1)
  const dv = valorLimpio.slice(-1).toUpperCase()
  if (!/^\d{7,8}[0-9K]$/.test(cuerpo + dv)) return false
  let suma = 0
  let multiplo = 2
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo.charAt(i), 10) * multiplo
    multiplo = multiplo === 7 ? 2 : multiplo + 1
  }
  const dvEsperado = 11 - (suma % 11)
  const dvCalculado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString()
  return dv === dvCalculado
}

const validarTelefono = (telefono) => {
  if (!telefono) return true
  return telefonoStrictRegex.test(telefono.replace(/[\s\-()]/g, ''))
}

const clearRefValidity = (inputRef) => {
  inputRef.value?.setCustomValidity('')
}

const clearFieldValidity = (event) => {
  event?.target?.setCustomValidity('')
}

const triggerNativeError = (inputRef, message) => {
  if (inputRef.value) {
    inputRef.value.setCustomValidity(message)
    inputRef.value.reportValidity()
  }
}

const allowOnlyNameCharacters = (event) => {
  const controlKeys = ['Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'Delete']
  if (controlKeys.includes(event.key)) return
  if (!/^[A-Za-z\u00c0-\u017f\s]$/.test(event.key)) {
    event.preventDefault()
  }
}

const validateEditableFields = () => {
  if (!user.value) return false

  const nombreLimpio = user.value.nombre.trim()
  if (!nombreLimpio) {
    errorMsg.value = 'El Nombre Completo es obligatorio.'
    triggerNativeError(nombreInput, 'Ingresa nombre y apellido.')
    return false
  }
  if (!nombreRegex.test(nombreLimpio)) {
    errorMsg.value = 'El Nombre solo puede incluir letras y espacios.'
    triggerNativeError(nombreInput, 'Solo letras y espacios para el nombre.')
    return false
  }
  user.value.nombre = nombreLimpio
  clearRefValidity(nombreInput)

  const rutLimpio = user.value.rut.trim()
  if (!rutFormatRegex.test(rutLimpio)) {
    errorMsg.value = 'El RUT debe tener el formato 12345678-K.'
    triggerNativeError(rutInput, 'Formato correcto: 12345678-K.')
    return false
  }
  if (!validarRut(rutLimpio)) {
    errorMsg.value = 'El RUT ingresado no es válido. Verifica el dígito verificador.'
    triggerNativeError(rutInput, 'Revisa el dígito verificador del RUT.')
    return false
  }
  user.value.rut = rutLimpio
  clearRefValidity(rutInput)

  const telefonoValor = user.value.numero_telefonico.trim()
  if (telefonoValor && !validarTelefono(telefonoValor)) {
    errorMsg.value = 'El teléfono debe tener el formato +56912345678.'
    triggerNativeError(telefonoInput, 'Ejemplo válido: +56912345678.')
    return false
  }
  user.value.numero_telefonico = telefonoValor
  clearRefValidity(telefonoInput)

  return true
}

const fetchUserDetail = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    if (!response.ok) {
      throw new Error('Usuario no encontrado o acceso denegado.')
    }

    const data = await response.json()
    const formatted = formatearUsuario(data)
    user.value = { ...formatted }
    originalUser.value = { ...formatted }
  } catch (error) {
    console.error('API Error:', error)
    errorMsg.value = `Error al cargar detalle: ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const saveChanges = async () => {
  if (!validateEditableFields()) return
  isSaving.value = true
  actionInProgress.value = 'save'
  errorMsg.value = null
  successMsg.value = null

  const payload = {}
  for (const key in user.value) {
    if (user.value[key] !== originalUser.value[key] && key !== 'id') {
      payload[key] = user.value[key]
    }
  }

  if (Object.keys(payload).length === 0) {
    successMsg.value = 'No hay cambios para guardar.'
    isSaving.value = false
    actionInProgress.value = null
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()

    if (!response.ok) {
      errorMsg.value =
        data.detail || (data.email ? 'Email duplicado o inválido.' : 'Error de validación.')
      throw new Error('Fallo al actualizar usuario.')
    }

    successMsg.value = 'Listo. Cambios guardados con éxito.'
    originalUser.value = { ...user.value }
  } catch (e) {
    if (!errorMsg.value) {
      errorMsg.value = 'Error al comunicarse con la API durante la actualización.'
    }
  } finally {
    isSaving.value = false
    actionInProgress.value = null
  }
}

const deactivateAccount = async () => {
  isSaving.value = true
  actionInProgress.value = 'deactivate'
  errorMsg.value = null
  successMsg.value = null

  try {
    const response = await fetch(`${API_BASE_URL}/admin/usuarios/${userId}/`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.token}` },
    })

    if (response.status === 204) {
      successMsg.value = 'Usuario desactivado con éxito. Redirigiendo a la lista...'
      setTimeout(() => {
        router.push({ name: 'AdminUsers' })
      }, 2000)
    } else {
      const data = await response.json()
      throw new Error(data.detail || 'Fallo al desactivar la cuenta.')
    }
  } catch (error) {
    errorMsg.value = error.message || 'Error desconocido al intentar desactivar.'
  } finally {
    isSaving.value = false
    actionInProgress.value = null
  }
}

const requestSaveConfirmation = () => {
  errorMsg.value = null
  successMsg.value = null
  if (!validateEditableFields()) return
  modalState.value = {
    type: 'save',
    title: '¿Guardar cambios?',
    message: 'Se actualizará la información de este usuario en la plataforma.',
    confirmLabel: 'Sí, guardar',
  }
}

const requestDeactivateConfirmation = () => {
  errorMsg.value = null
  successMsg.value = null
  modalState.value = {
    type: 'deactivate',
    title: `¿Desactivar a ${user.value?.nombre || 'este usuario'}?`,
    message: 'Esta acción es permanente en Supabase Auth y no se puede deshacer.',
    confirmLabel: 'Sí, desactivar',
  }
}

const closeModal = () => {
  modalState.value.type = null
}

const confirmModalAction = async () => {
  if (modalState.value.type === 'save') {
    modalState.value.type = null
    await saveChanges()
  } else if (modalState.value.type === 'deactivate') {
    modalState.value.type = null
    await deactivateAccount()
  }
}

onMounted(fetchUserDetail)
</script>

<template>
  <div class="user-detail-page">
    <section class="user-detail-wrapper">
      <div v-if="isLoading" class="state-card loading">
        <span class="spinner"></span>
        <p>Cargando detalle del usuario...</p>
      </div>

      <div v-else-if="!user" class="state-card error">
        {{ errorMsg || 'Error al cargar detalle del usuario.' }}
      </div>

      <div v-else class="detail-card">
        <header class="detail-header">
          <button class="back-button" @click="router.push({ name: 'AdminUsers' })">
            &larr; Volver a la Lista
          </button>
          <div class="header-copy">
            <p class="eyebrow">ID: {{ user.id }}</p>
            <h1>{{ user.nombre }}</h1>
            <p>Modificar el perfil y rol de un usuario existente.</p>
          </div>
        </header>

        <form class="user-form" @submit.prevent="requestSaveConfirmation">
          <div class="form-grid">
            <div class="form-group">
              <label>ID Interno</label>
              <div class="input-shell disabled">
                <input type="text" :value="user.id" disabled />
              </div>
            </div>
            <div class="form-group">
              <label for="rol">Rol</label>
              <div class="input-shell disabled pill-input">
                <input id="rol" type="text" :value="user.rol" readonly />
              </div>
              <small class="note">El rol no se puede editar desde esta vista.</small>
            </div>
            <div class="form-group span-2">
              <label for="nombre">Nombre Completo</label>
              <div class="input-shell">
                <input
                  id="nombre"
                  ref="nombreInput"
                  v-model.trim="user.nombre"
                  placeholder="Nombre y apellido"
                  autocomplete="name"
                  @keydown="allowOnlyNameCharacters"
                  @input="clearFieldValidity"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="rut">RUT</label>
              <div class="input-shell">
                <input
                  id="rut"
                  ref="rutInput"
                  :value="user.rut"
                  type="text"
                  placeholder="12345678-K"
                  maxlength="10"
                  autocomplete="off"
                  @keydown="bloquearTeclasNoRut"
                  @input="formatearRutInput"
                />
              </div>
              <small class="note">El RUT debe ser único.</small>
            </div>
            <div class="form-group">
              <label>Correo Electrónico</label>
              <div class="input-shell disabled">
                <input type="email" :value="user.email" disabled />
              </div>
              <small class="note">El email es la clave de Supabase.</small>
            </div>
            <div class="form-group span-2">
              <label for="telefono">Teléfono</label>
              <div class="input-shell">
                <input
                  id="telefono"
                  ref="telefonoInput"
                  :value="user.numero_telefonico"
                  placeholder="+56912345678"
                  maxlength="12"
                  type="tel"
                  autocomplete="tel"
                  @keydown="bloquearTeclasTelefono"
                  @input="formatearTelefono"
                />
              </div>
            </div>
          </div>

          <div v-if="successMsg" class="status-banner success" role="status">{{ successMsg }}</div>
          <div v-if="errorMsg" class="status-banner error" role="alert">{{ errorMsg }}</div>

          <div class="action-buttons">
            <button
              type="button"
              class="danger-button"
              :disabled="isSaving"
              @click="requestDeactivateConfirmation"
            >
              {{
                isSaving && actionInProgress === 'deactivate'
                  ? 'Desactivando...'
                  : 'Desactivar Cuenta'
              }}
            </button>
            <button type="submit" class="accent-button" :disabled="isSaving">
              {{ isSaving && actionInProgress === 'save' ? 'Guardando...' : 'Guardar Cambios' }}
            </button>
          </div>
        </form>
      </div>
    </section>

    <Transition name="detail-modal-fade">
      <div
        v-if="modalState.type"
        class="action-modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="user-modal-title"
        @click.self="closeModal"
      >
        <div class="action-modal-content">
          <div class="action-modal-icon" :class="modalState.type">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M12 9v4" />
              <path d="M12 17h.01" />
              <path d="M7.938 4h8.124L22 12l-5.938 8H7.938L2 12z" />
            </svg>
          </div>
          <h3 id="user-modal-title">{{ modalState.title }}</h3>
          <p>{{ modalState.message }}</p>
          <div class="action-modal-buttons">
            <button type="button" class="modal-btn cancel" @click="closeModal">Cancelar</button>
            <button
              type="button"
              class="modal-btn confirm"
              :class="modalState.type"
              :disabled="isSaving"
              @click="confirmModalAction"
            >
              {{ isSaving ? 'Procesando...' : modalState.confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.user-detail-page {
  position: relative;
}
.user-detail-wrapper {
  min-height: calc(100vh - 160px);
  padding: 42px 18px 96px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.state-card {
  border-radius: 28px;
  padding: 50px 40px;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.85);
  box-shadow: 0 25px 60px rgba(2, 6, 23, 0.5);
  color: #f8fafc;
}
.state-card.error {
  color: #fecaca;
  background: rgba(248, 113, 113, 0.18);
}
.state-card.loading {
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}
.spinner {
  width: 54px;
  height: 54px;
  border: 4px solid rgba(148, 163, 184, 0.2);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

.detail-card {
  width: 100%;
  max-width: 600px;
  border-radius: 30px;
  padding: 34px;
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.82));
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 32px 70px rgba(2, 6, 23, 0.65);
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);
  animation: cardAppear 0.55s ease;
}
.detail-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(59, 130, 246, 0.15);
  pointer-events: none;
}
.detail-card::after {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  top: -80px;
  right: -60px;
  background: radial-gradient(circle, rgba(74, 222, 128, 0.35), transparent 60%);
  filter: blur(10px);
  animation: shimmer 9s linear infinite;
}
.detail-header {
  display: flex;
  gap: 18px;
  margin-bottom: 28px;
  align-items: flex-start;
}
.header-copy {
  flex: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.74rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 6px;
}
.detail-header h1 {
  margin: 0;
  color: #f8fafc;
  font-size: 1.7rem;
}
.detail-header p {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.9);
}
.back-button {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
  padding: 10px 18px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition:
    border 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}
.back-button:hover {
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(59, 130, 246, 0.2);
  transform: translateY(-1px);
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group.span-2 {
  grid-column: 1 / -1;
}
label {
  color: rgba(226, 232, 240, 0.95);
  font-weight: 600;
}
.input-shell {
  border: 1px solid rgba(148, 163, 184, 0.32);
  border-radius: 18px;
  padding: 11px 16px;
  background: rgba(11, 18, 32, 0.85);
  transition:
    border 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}
.input-shell:focus-within {
  border-color: rgba(56, 189, 248, 0.9);
  box-shadow: 0 12px 30px rgba(14, 165, 233, 0.2);
  transform: translateY(-1px);
}
.input-shell.disabled {
  opacity: 0.7;
}
.input-shell input,
.input-shell select {
  width: 100%;
  background: transparent;
  border: none;
  color: #f8fafc;
  font-size: 1rem;
  outline: none;
}
.pill-input input {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  text-align: center;
}
.note {
  font-size: 0.8rem;
  color: rgba(148, 163, 184, 0.8);
}

.status-banner {
  padding: 12px 14px;
  border-radius: 15px;
  font-weight: 600;
  border: 1px solid transparent;
}
.status-banner.success {
  color: #bbf7d0;
  background: rgba(34, 197, 94, 0.18);
  border-color: rgba(34, 197, 94, 0.35);
}
.status-banner.error {
  color: #fecaca;
  background: rgba(248, 113, 113, 0.15);
  border-color: rgba(248, 113, 113, 0.35);
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.accent-button,
.danger-button {
  flex: 1;
  border-radius: 18px;
  border: none;
  padding: 16px 0;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.accent-button {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0f172a;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
}
.accent-button:hover:not(:disabled),
.danger-button:hover:not(:disabled) {
  transform: translateY(-2px);
}
.danger-button {
  background: linear-gradient(120deg, #fb7185, #f97316);
  color: #fff;
  box-shadow: 0 18px 40px rgba(249, 115, 22, 0.35);
}
.accent-button:disabled,
.danger-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.action-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.85);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.action-modal-content {
  width: min(450px, 92%);
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 30px;
  padding: 32px;
  box-shadow: 0 35px 80px rgba(2, 6, 23, 0.75);
  text-align: center;
  backdrop-filter: blur(10px);
}
.action-modal-icon {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  margin: 0 auto 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(14, 165, 233, 0.4);
  background: rgba(14, 165, 233, 0.12);
  color: #38bdf8;
}
.action-modal-icon.deactivate {
  border-color: rgba(248, 113, 113, 0.5);
  background: rgba(248, 113, 113, 0.15);
  color: #f87171;
}
.action-modal-content h3 {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 1.4rem;
}
.action-modal-content p {
  margin: 0 0 22px;
  color: rgba(226, 232, 240, 0.85);
  font-size: 0.95rem;
}
.action-modal-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}
.modal-btn {
  border: none;
  border-radius: 999px;
  font-weight: 600;
  padding: 12px 28px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.modal-btn.cancel {
  background: rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}
.modal-btn.confirm {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0f172a;
  box-shadow: 0 18px 35px rgba(14, 165, 233, 0.45);
}
.modal-btn.confirm.deactivate {
  background: linear-gradient(120deg, #fb7185, #f97316);
  color: #fff;
  box-shadow: 0 18px 35px rgba(249, 115, 22, 0.4);
}
.modal-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.detail-modal-fade-enter-active,
.detail-modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.detail-modal-fade-enter-active .action-modal-content,
.detail-modal-fade-leave-active .action-modal-content {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}
.detail-modal-fade-enter-from,
.detail-modal-fade-leave-to {
  opacity: 0;
}
.detail-modal-fade-enter-from .action-modal-content,
.detail-modal-fade-leave-to .action-modal-content {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
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

@media (max-width: 640px) {
  .detail-card {
    padding: 26px;
  }
  .detail-header {
    flex-direction: column;
  }
  .action-buttons {
    flex-direction: column;
  }
}
</style>
