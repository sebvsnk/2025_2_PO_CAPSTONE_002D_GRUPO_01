<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// Estado del formulario
const authStore = useAuthStore()
const form = ref({
  nombre: '',
  email: '',
  rol: 'MECANICO',
  rut: '',
  numero_telefonico: '',
})

const isLoading = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)
const showInviteConfirm = ref(false)

const nombreInput = ref(null)
const emailInput = ref(null)
const rutInput = ref(null)
const telefonoInput = ref(null)

const roles = ['SUPERVISOR', 'MECANICO', 'PORTERIA', 'GUARDIA', 'ANALISTA', 'CHOFER']
const nombreRegex = /^[A-Za-z\u00c0-\u017f\s]+$/u
const rutFormatRegex = /^\d{7,8}-[\dkK]$/
const telefonoStrictRegex = /^\+569\d{8}$/

/**
 * Valida un RUT chileno (con di­gito verificador - Modulo 11).
 */
const validarRut = (rut) => {
  if (typeof rut !== 'string' || !rut) {
    return false
  }
  const valorLimpio = rut.replace(/[.-]/g, '')
  const cuerpo = valorLimpio.slice(0, -1)
  const dv = valorLimpio.slice(-1).toUpperCase()

  if (!/^\d{7,8}[0-9K]$/.test(cuerpo + dv)) {
    return false
  }

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

/**
 * Valida un nÃºmero de telÃ©fono chileno (opcional).
 */
const validarTelefono = (telefono) => {
  if (!telefono) {
    return true
  }
  const telefonoLimpio = telefono.replace(/[\s\-()]/g, '')
  return telefonoStrictRegex.test(telefonoLimpio)
}

/**
 * Valida un correo electrÃ³nico.
 */
const validarEmail = (email) => {
  if (!email) return false
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const clearRefValidity = (inputRef) => {
  if (inputRef.value) {
    inputRef.value.setCustomValidity('')
  }
}

const triggerNativeError = (inputRef, message) => {
  if (inputRef.value) {
    inputRef.value.setCustomValidity(message)
    inputRef.value.reportValidity()
  }
}

const clearFieldValidity = (event) => {
  event?.target?.setCustomValidity('')
}

const allowOnlyNameCharacters = (event) => {
  const controlKeys = ['Backspace', 'Tab', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'Delete']
  if (controlKeys.includes(event.key)) {
    return
  }
  if (!/^[A-Za-z\u00c0-\u017f\s]$/.test(event.key)) {
    event.preventDefault()
  }
}

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

  // 1. Permitir teclas de control y atajos (Ctrl+C, Ctrl+V, etc.)
  if (teclasPermitidas.includes(event.key) || event.ctrlKey || event.metaKey) {
    return
  }
  // 2. Si NO es número ni K/k, bloqueamos el evento
  if (!/^[0-9kK]$/.test(event.key)) {
    event.preventDefault()
  }
}

const formatearRutInput = (event) => {
  let valor = event.target.value
  // --- FUNCIÓN MEJORADA DE FORMATEO ---
  // 1. Limpiar: Eliminar cualquier cosa que no sea número o K
  valor = valor.replace(/[^0-9kK]/g, '').toUpperCase()

  // 2. LÍMITE ESTRICTO: Un RUT chileno no tiene más de 9 caracteres reales (8 dígitos + DV)
  // Ej: 12.345.678-K -> "12345678K" (9 caracteres)
  if (valor.length > 9) {
    valor = valor.slice(0, 9)
  }

  // 3. Formatear: Agregar el guion antes del último carácter
  if (valor.length > 1) {
    const cuerpo = valor.slice(0, -1)
    const dv = valor.slice(-1)
    valor = `${cuerpo}-${dv}`
  }

  // 4. Forzar la actualización del valor en el input visual y en la variable
  event.target.value = valor
  form.value.rut = valor

  // 5. Limpiar validaciones nativas si las hubiera
  clearFieldValidity(event)
}

// 1. Bloquear cualquier tecla que no sea número (para el teléfono)
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
    '+',
  ]

  // Permitir atajos (Ctrl+C, etc) y teclas de movimiento
  if (teclasPermitidas.includes(event.key) || event.ctrlKey || event.metaKey) return

  // Bloquear si no es número (0-9)
  if (!/^[0-9]$/.test(event.key)) {
    event.preventDefault()
  }
}

// 2. Formatear estricto: Siempre +569 + 8 dígitos
const formatearTelefono = (event) => {
  let valor = event.target.value

  // A. Quedarse solo con los números puros de lo que ingresó el usuario
  let numeros = valor.replace(/\D/g, '')

  // B. Lógica de "Cuerpo":
  // Si el usuario pegó un número completo (ej: 56912345678), detectamos el 569 inicial y lo ignoramos
  // para quedarnos solo con el cuerpo real del teléfono.
  if (numeros.startsWith('569')) {
    numeros = numeros.substring(3)
  }

  // C. Si el usuario borró todo, dejamos el campo limpio (opcional)
  // Si prefieres que SIEMPRE quede el +569, borra este bloque 'if'.
  if (numeros.length === 0) {
    form.value.numero_telefonico = ''
    return
  }

  // D. Cortar a máximo 8 dígitos (que es el largo de un celular chileno sin el +569)
  if (numeros.length > 8) {
    numeros = numeros.slice(0, 8)
  }

  // E. Construir el formato final forzado
  const resultado = '+569' + numeros

  // F. Actualizar vista y modelo
  form.value.numero_telefonico = resultado

  clearFieldValidity(event)
}

const validateForm = () => {
  const nombreLimpio = form.value.nombre.trim()

  if (!nombreLimpio) {
    errorMsg.value = 'Error: El Nombre Completo es obligatorio.'
    triggerNativeError(nombreInput, 'Ingresa nombre y apellido.')
    return false
  }
  if (!nombreRegex.test(nombreLimpio)) {
    errorMsg.value = 'Error: El Nombre solo puede incluir letras y espacios.'
    triggerNativeError(nombreInput, 'Solo letras y espacios para el nombre.')
    return false
  }
  clearRefValidity(nombreInput)

  if (!validarEmail(form.value.email.trim())) {
    errorMsg.value = 'Error: El formato del Correo Electronico no es valido.'
    triggerNativeError(emailInput, 'Incluye un correo valido como usuario@empresa.com.')
    return false
  }
  clearRefValidity(emailInput)

  const rutLimpio = form.value.rut.trim()
  if (!rutFormatRegex.test(rutLimpio)) {
    errorMsg.value = 'Error: El RUT debe tener el formato 20058625-5.'
    triggerNativeError(rutInput, 'Formato correcto: 20058625-5.')
    return false
  }
  if (!validarRut(rutLimpio)) {
    errorMsg.value = 'Error: El RUT ingresado no es valido. Verifique el digito verificador.'
    triggerNativeError(rutInput, 'Revisa el digito verificador del RUT.')
    return false
  }
  clearRefValidity(rutInput)

  const telefonoValor = form.value.numero_telefonico.trim()
  if (telefonoValor && !validarTelefono(telefonoValor)) {
    errorMsg.value = 'Error: El telefono debe tener el formato +56912345678.'
    triggerNativeError(telefonoInput, 'Ejemplo valido: +56912345678.')
    return false
  }
  clearRefValidity(telefonoInput)

  return true
}

const requestInviteConfirmation = () => {
  errorMsg.value = null
  successMsg.value = null

  if (!validateForm()) {
    return
  }

  showInviteConfirm.value = true
}

const cancelInviteConfirmation = () => {
  showInviteConfirm.value = false
}

const confirmInviteCreation = async () => {
  if (isLoading.value) return
  showInviteConfirm.value = false
  await handleCreateUser()
}

// --- ðŸŒŸ FUNCIÃ“N DE CREACIÃ“N (CON VALIDACIÃ“N Y TRADUCCIÃ“N) ðŸŒŸ ---
const handleCreateUser = async () => {
  isLoading.value = true
  errorMsg.value = null
  successMsg.value = null

  try {
    const telefonoNormalizado = form.value.numero_telefonico.trim().replace(/[\s\-()]/g, '')

    const payload = {
      ...form.value,
      nombre: form.value.nombre.trim(),
      email: form.value.email.trim(),
      rut: form.value.rut.trim(),
      numero_telefonico: telefonoNormalizado,
    }

    const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/usuarios/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()

    if (!response.ok) {
      const detail =
        data.detail ||
        (data.rut
          ? `RUT: ${data.rut[0]}`
          : data.email
            ? `Email: ${data.email[0]}`
            : 'Error de validacion del servidor.')
      throw new Error(detail)
    }

    successMsg.value = `Listo. Usuario ${data.nombre} invitado con exito. Se envio el correo de activacion.`

    setTimeout(() => {
      router.push({ name: 'AdminUsers' })
    }, 1500)
  } catch (error) {
    console.error('Create User API Error:', error)

    let friendlyError = error.message

    if (
      error.message.includes('A user with this email address has already been registered') ||
      error.message.includes('Un usuario con este correo electronico ya existe')
    ) {
      friendlyError = 'Error: Un usuario con este correo electronico ya existe.'
    } else if (error.message.includes('RUT:')) {
      friendlyError = 'Error: El RUT ingresado ya esta en uso o no es valido.'
    }

    errorMsg.value = friendlyError
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="user-create-page">
    <section class="user-create-wrapper">
      <div class="user-card">
        <header class="user-header">
          <button class="back-button" @click="router.push({ name: 'AdminUsers' })">
            &larr; Volver a Gestión
          </button>
          <div class="header-copy">
            <p class="eyebrow">Invitación</p>
            <h1>Crear Nuevo Usuario</h1>
            <p>Invitar un nuevo usuario a la plataforma.</p>
          </div>
        </header>

        <form class="user-form" @submit.prevent="requestInviteConfirmation">
          <p class="form-hint">
            Validamos formato de nombre, correo, RUT y teléfono antes de enviar.
          </p>

          <div class="form-grid">
            <div class="form-group span-2">
              <label for="nombre">Nombre Completo</label>
              <div class="input-shell">
                <input
                  id="nombre"
                  ref="nombreInput"
                  v-model.trim="form.nombre"
                  placeholder="Ingrese nombre y apellido"
                  autocomplete="name"
                  @keydown="allowOnlyNameCharacters"
                  @input="clearFieldValidity"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="email">Correo Electrónico</label>
              <div class="input-shell">
                <input
                  id="email"
                  ref="emailInput"
                  v-model.trim="form.email"
                  type="email"
                  placeholder="correo@empresa.com"
                  autocomplete="email"
                  inputmode="email"
                  @input="clearFieldValidity"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="rol">Rol</label>
              <div class="input-shell select-shell">
                <select id="rol" v-model="form.rol">
                  <option v-for="role in roles" :key="role" :value="role">{{ role }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label for="rut">RUT</label>
              <div class="input-shell">
                <input
                  id="rut"
                  ref="rutInput"
                  :value="form.rut"
                  type="text"
                  placeholder="12345678-K"
                  maxlength="10"
                  autocomplete="off"
                  @keydown="bloquearTeclasNoRut"
                  @input="formatearRutInput"
                />
              </div>
            </div>
            <div class="form-group">
              <label for="telefono">Número Telefónico</label>
              <div class="input-shell">
                <input
                  id="telefono"
                  ref="telefonoInput"
                  type="tel"
                  :value="form.numero_telefonico"
                  placeholder="+56912345678"
                  maxlength="12"
                  autocomplete="tel"
                  @keydown="bloquearTeclasTelefono"
                  @input="formatearTelefono"
                />
              </div>
            </div>
          </div>

          <div v-if="successMsg" class="status-banner success" role="status">{{ successMsg }}</div>
          <div v-if="errorMsg" class="status-banner error" role="alert">{{ errorMsg }}</div>

          <button type="submit" :disabled="isLoading" class="submit-button">
            {{ isLoading ? 'Creando...' : 'Crear Usuario y Enviar Invitación' }}
          </button>
        </form>
      </div>
    </section>
    <Transition name="invite-modal-fade">
      <div
        v-if="showInviteConfirm"
        class="invite-modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby="invite-confirm-title"
      >
        <div class="invite-modal-content">
          <div class="invite-modal-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M4 4h16v16H4z" opacity="0.15" />
              <polyline points="22,6 12,13 2,6" />
              <path d="M2 18l6-6" />
              <path d="M22 18l-6-6" />
            </svg>
          </div>
          <h3 id="invite-confirm-title">¿Invitar a este usuario?</h3>
          <p>Revisa los datos ingresados. Se enviará una invitación al correo indicado.</p>
          <div class="invite-modal-actions">
            <button type="button" class="invite-modal-btn cancel" @click="cancelInviteConfirmation">
              Cancelar
            </button>
            <button
              type="button"
              class="invite-modal-btn confirm"
              :disabled="isLoading"
              @click="confirmInviteCreation"
            >
              {{ isLoading ? 'Enviando...' : 'Sí, enviar invitación' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.user-create-page {
  position: relative;
}
.user-create-wrapper {
  min-height: calc(100vh - 160px);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 42px 18px 96px;
}
.user-card {
  width: 100%;
  max-width: 560px;
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
.user-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  border: 1px solid rgba(59, 130, 246, 0.15);
  pointer-events: none;
}
.user-card::after {
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
.user-header {
  display: flex;
  gap: 18px;
  margin-bottom: 24px;
}
.header-copy {
  flex: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 6px;
}
.user-header h1 {
  margin: 0;
  color: #f8fafc;
  font-size: 1.7rem;
}
.user-header p {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.9);
}
.back-button {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.5);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.32), rgba(45, 212, 191, 0.32));
  color: #e2e8f0;
  padding: 6px 12px;
  font-weight: 700;
  letter-spacing: 0.01em;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow:
    0 10px 22px rgba(15, 23, 42, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.07);
}
.back-button:hover {
  border-color: rgba(59, 130, 246, 0.6);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.42), rgba(45, 212, 191, 0.42));
  transform: translateY(-1px);
  box-shadow:
    0 14px 30px rgba(15, 23, 42, 0.55),
    0 0 16px rgba(59, 130, 246, 0.22);
}
.user-form {
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.form-hint {
  margin: 0;
  color: rgba(148, 163, 184, 0.92);
  font-size: 0.92rem;
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
  font-size: 0.92rem;
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
.input-shell input,
.input-shell select {
  width: 100%;
  border: none;
  background: transparent;
  color: #f8fafc;
  font-size: 1rem;
  outline: none;
}
select {
  appearance: none;
}
.select-shell select {
  color: #f8fafc;
  background-color: transparent;
}
.select-shell select option {
  color: #e2e8f0;
  background-color: #0f172a;
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

.submit-button {
  border: none;
  padding: 16px 0;
  border-radius: 19px;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #0c111d;
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  cursor: pointer;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
  width: 100%;
  text-align: center;
  transition:
    transform 0.2s ease,
    box-shadow 0.25s ease,
    filter 0.2s ease;
}
.submit-button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
  box-shadow: 0 25px 45px rgba(14, 165, 233, 0.4);
}
.submit-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  box-shadow: none;
}

.invite-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(2, 6, 23, 0.8);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
}
.invite-modal-content {
  width: min(440px, 90%);
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 28px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 32px 80px rgba(2, 6, 23, 0.75);
  backdrop-filter: blur(10px);
}
.invite-modal-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  margin: 0 auto 18px;
  background: rgba(14, 165, 233, 0.15);
  border: 3px solid rgba(14, 165, 233, 0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #38bdf8;
}
.invite-modal-icon svg {
  width: 34px;
  height: 34px;
}
.invite-modal-content h3 {
  margin: 0 0 10px;
  color: #f8fafc;
  font-size: 1.35rem;
}
.invite-modal-content p {
  margin: 0 0 24px;
  color: rgba(226, 232, 240, 0.85);
  font-size: 0.95rem;
}
.invite-modal-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}
.invite-modal-btn {
  border: none;
  border-radius: 999px;
  font-weight: 600;
  padding: 12px 24px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.invite-modal-btn.cancel {
  background: rgba(148, 163, 184, 0.15);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}
.invite-modal-btn.cancel:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 18px rgba(15, 23, 42, 0.55);
}
.invite-modal-btn.confirm {
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0f172a;
  box-shadow: 0 18px 35px rgba(14, 165, 233, 0.45);
}
.invite-modal-btn.confirm:hover:not(:disabled) {
  transform: translateY(-1px);
}
.invite-modal-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.invite-modal-fade-enter-active,
.invite-modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.invite-modal-fade-enter-active .invite-modal-overlay,
.invite-modal-fade-leave-active .invite-modal-overlay {
  transition: opacity 0.3s ease;
}
.invite-modal-fade-enter-active .invite-modal-content,
.invite-modal-fade-leave-active .invite-modal-content {
  transition:
    transform 0.3s ease,
    opacity 0.3s ease;
}
.invite-modal-fade-enter-from,
.invite-modal-fade-leave-to {
  opacity: 0;
}
.invite-modal-fade-enter-from .invite-modal-content,
.invite-modal-fade-leave-to .invite-modal-content {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
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
</style>
