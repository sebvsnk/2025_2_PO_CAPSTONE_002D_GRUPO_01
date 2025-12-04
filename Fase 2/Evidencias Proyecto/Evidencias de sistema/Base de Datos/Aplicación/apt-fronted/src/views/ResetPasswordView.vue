<script setup>
import { ref, onMounted, computed } from 'vue'
import { supabase } from '@/services/supabaseClient'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// --- ESTADOS ---
const newPassword = ref('')
const confirmPassword = ref('')
const fatalError = ref('') // Para errores de carga (oculta el form)
const submissionError = ref('') // Para errores de envío (no oculta el form)
const successMessage = ref('')
const isLoading = ref(false)
const isVerifyingToken = ref(true) // <-- Inicia en true para la animación de carga
const showPassword = ref(false)

// --- COMPUTED: LOADING TEXT ---
const loadingText = computed(() => {
  if (isVerifyingToken.value) {
    return 'Verificando enlace...' // <-- Tu animación de carga
  }
  if (isLoading.value) {
    return 'Guardando contraseña...'
  }
  return 'Cargando...' // Fallback
})

// --- COMPUTED: VALIDACIÓN ---
const minLength = 8
const reqMinLength = computed(() => newPassword.value.length >= minLength)
const reqHasUpper = computed(() => /[A-Z]/.test(newPassword.value))
const reqHasNumber = computed(() => /\d/.test(newPassword.value))
const reqHasSymbol = computed(() => /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(newPassword.value))
const reqMatch = computed(
  () => newPassword.value === confirmPassword.value && confirmPassword.value.length > 0,
)

const passwordStrength = computed(() => {
  let score = 0
  if (reqMinLength.value) score++
  if (reqHasUpper.value) score++
  if (reqHasNumber.value) score++
  if (reqHasSymbol.value) score++

  if (newPassword.value.length === 0) {
    return { text: '', score: 0, color: 'transparent' }
  }
  switch (score) {
    case 1:
      return { text: 'Muy Débil', score: 1, color: '#f87171' }
    case 2:
      return { text: 'Débil', score: 2, color: '#facc15' }
    case 3:
      return { text: 'Buena', score: 3, color: '#007bff' }
    case 4:
      return { text: 'Fuerte', score: 4, color: '#22c55e' }
    default:
      return { text: 'Muy Débil', score: 1, color: '#f87171' }
  }
})

const isFormValid = computed(() => {
  return (
    reqMinLength.value &&
    reqHasUpper.value &&
    reqHasNumber.value &&
    reqHasSymbol.value &&
    reqMatch.value
  )
})

// --- MEJORA 1: onMounted (Arregla "Enlace inválido") ---
onMounted(async () => {
  auth.loadingMessage = 'Verificando enlace...'
  auth.isLoadingUser = true
  fatalError.value = ''
  try {
    const {
      data: { session },
      error: sessionError,
    } = await supabase.auth.getSession()

    // Validación mejorada (como la de AuthCallback)
    if (sessionError || !session || !session.access_token) {
      console.error('Error al obtener sesión de Supabase:', sessionError || 'Sesión no encontrada.')
      fatalError.value =
        'Enlace inválido. No se encontró un token. Por favor, solicita un nuevo enlace.'
      return // Detiene la ejecución
    }

    // Si todo está ok, el token es válido.
  } catch (e) {
    fatalError.value = e.message
  } finally {
    // Oculta el overlay de "Verificando enlace..."
    isVerifyingToken.value = false
    auth.isLoadingUser = false
  }
})

// --- MEJORA 2: handlePasswordSave (Arregla error "misma contraseña" y redirección) ---
// En: apt-fronted/src/views/ResetPasswordView.vue
// REEMPLAZA esta función completa:

const handlePasswordSave = async () => {
  submissionError.value = ''
  successMessage.value = ''

  if (!isFormValid.value) {
    submissionError.value = 'Debes cumplir todos los requisitos de la contraseña.'
    return
  }

  isLoading.value = true
  try {
    const { error } = await supabase.auth.updateUser({
      password: newPassword.value,
    })

    if (error) {
      throw new Error(error.message || 'Error desconocido de Supabase.')
    }

    successMessage.value = 'Contraseña establecida con éxito. Redirigiendo al login...'
    isLoading.value = false

    // --- 🌟 CORRECCIÓN DE REDIRECCIÓN DEFINITIVA 🌟 ---
    setTimeout(async () => {
      // 1. Cierra la sesión de Supabase
      await supabase.auth.signOut()

      // 2. Limpia el store local
      auth.token = null
      auth.user = null
      auth.flashMessage = 'Inicia sesión con tu nueva contraseña.'

      // 3. Forzamos la recarga de la página en la ruta /login
      //    Esto evita el "router guard" y limpia todo el estado.
      window.location.href = '/login'
    }, 3000) // 3 segundos para ver el checkmark
  } catch (error) {
    console.error('Error al actualizar la contraseña:', error)

    if (error.message.includes('New password should be different from the old password')) {
      submissionError.value = 'La nueva contraseña debe ser diferente a la anterior.'
    } else {
      submissionError.value = 'Error al guardar la contraseña. Inténtalo de nuevo.'
    }

    isLoading.value = false // Desbloquea el formulario en caso de error
  }
}

// Función para alternar visibilidad de contraseña
const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}
</script>

<template>
  <div>
    <Transition name="fade">
      <div v-if="isVerifyingToken || isLoading" class="loading-overlay">
        <div class="spinner"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>
    </Transition>

    <div class="login-container">
      <div class="login-box">
        <div class="login-info-panel">
          <div class="logo-header">
            <div class="logo-icon">APT</div>
            <h1>Taller PepsiCo</h1>
          </div>
          <p class="welcome-text">Establece una nueva contraseña segura para tu cuenta.</p>
        </div>

        <div class="login-form-panel">
          <div v-if="successMessage" class="success-animation-container">
            <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
              <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none" />
              <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
            </svg>
            <h3 class="success-title">¡Contraseña Guardada!</h3>
            <p class="success-text">{{ successMessage }}</p>
          </div>

          <form v-else @submit.prevent="handlePasswordSave">
            <h2 class="form-title">Establecer Contraseña</h2>

            <p v-if="fatalError" class="error-message">{{ fatalError }}</p>

            <template v-if="!fatalError">
              <p v-if="submissionError" class="error-message">{{ submissionError }}</p>

              <div class="input-group">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  class="input-icon"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Zm-3 2a1 1 0 0 1 1 1v2a1 1 0 1 1-2 0v-2a1 1 0 0 1 1-1Z"
                    clip-rule="evenodd"
                  />
                </svg>
                <input
                  id="newPassword"
                  v-model="newPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Nueva contraseña"
                  :maxlength="64"
                  required
                  :disabled="isLoading || isVerifyingToken"
                  autocomplete="new-password"
                />
                <span class="password-toggle" @click="togglePasswordVisibility">
                  <svg
                    v-if="showPassword"
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="feather feather-eye"
                  >
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    class="feather feather-eye-off"
                  >
                    <path
                      d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.05 18.05 0 0 1 2.94-3.5"
                    ></path>
                    <path d="M1 1l22 22"></path>
                    <path d="M22 12c0 7-4 8-11 8a18.05 18.05 0 0 1-2.94-3.5"></path>
                    <path d="M9.88 9.88c-.68.83-1.07 1.77-1.07 2.12c0 3 3 0 3 0"></path>
                  </svg>
                </span>
              </div>

              <div v-if="newPassword.length > 0" class="strength-meter">
                <div class="strength-bar-track">
                  <div
                    class="strength-bar"
                    :style="{
                      width: `${(passwordStrength.score / 4) * 100}%`,
                      backgroundColor: passwordStrength.color,
                    }"
                  ></div>
                </div>
                <span class="strength-text" :style="{ color: passwordStrength.color }">
                  {{ passwordStrength.text }}
                </span>
              </div>

              <ul v-if="newPassword.length > 0" class="requirements-list">
                <li :class="{ valid: reqMinLength }">
                  <svg
                    v-if="reqMinLength"
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Al menos 8 caracteres
                </li>
                <li :class="{ valid: reqHasUpper }">
                  <svg
                    v-if="reqHasUpper"
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Una mayúscula (A-Z)
                </li>
                <li :class="{ valid: reqHasNumber }">
                  <svg
                    v-if="reqHasNumber"
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Un número (0-9)
                </li>
                <li :class="{ valid: reqHasSymbol }">
                  <svg
                    v-if="reqHasSymbol"
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  <svg
                    v-else
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                  Un símbolo (!@#$)
                </li>
              </ul>

              <div class="input-group">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  class="input-icon"
                >
                  <path
                    fill-rule="evenodd"
                    d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h9a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Zm-3 2a1 1 0 0 1 1 1v2a1 1 0 1 1-2 0v-2a1 1 0 0 1 1-1Z"
                    clip-rule="evenodd"
                  />
                </svg>
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Confirmar contraseña"
                  :maxlength="64"
                  required
                  :disabled="isLoading || isVerifyingToken"
                  autocomplete="new-password"
                />
                <span class="password-toggle" @click="togglePasswordVisibility">
                  <svg
                    v-if="showPassword"
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
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <svg
                    v-else
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
                    <path
                      d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.05 18.05 0 0 1 2.94-3.5"
                    ></path>
                    <path d="M1 1l22 22"></path>
                    <path d="M22 12c0 7-4 8-11 8a18.05 18.05 0 0 1-2.94-3.5"></path>
                    <path d="M9.88 9.88c-.68.83-1.07 1.77-1.07 2.12c0 3 3 0 3 0"></path>
                  </svg>
                </span>
              </div>

              <span
                v-if="confirmPassword.length > 0 && !reqMatch"
                class="match-error"
                :class="{ valid: reqMatch }"
              >
                Las contraseñas no coinciden
              </span>
              <span v-if="confirmPassword.length > 0 && reqMatch" class="match-error valid">
                Las contraseñas coinciden
              </span>

              <button
                type="submit"
                :disabled="isLoading || isVerifyingToken || !isFormValid"
                class="submit-button"
              >
                <div v-if="isLoading" class="spinner"></div>
                <span v-else>Guardar Nueva Contraseña</span>
              </button>
            </template>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.login-container {
  display: grid;
  place-items: center;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background:
    radial-gradient(1000px 600px at 15% 20%, rgba(59, 130, 246, 0.25), transparent 60%),
    radial-gradient(900px 500px at 85% 0, rgba(14, 165, 233, 0.2), transparent 65%), #030712;
  padding: clamp(20px, 6vw, 80px);
}

@keyframes slideUpFadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-box {
  width: 100%;
  max-width: 960px;
  display: flex;
  background: rgba(6, 12, 24, 0.85);
  border-radius: 24px;
  box-shadow: 0 40px 80px rgba(2, 6, 23, 0.65);
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.25);
  backdrop-filter: blur(18px);
  animation: slideUpFadeIn 0.6s ease-out forwards;
}

.login-info-panel {
  flex-basis: 45%;
  background:
    radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.35), transparent 55%),
    linear-gradient(140deg, #0f172a, #1d3662);
  padding: clamp(2.5rem, 4vw, 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: rgba(148, 163, 184, 0.25);
}
.logo-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.logo-icon {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  font-weight: 800;
  font-size: 18px;
  flex-shrink: 0;
}
h1 {
  color: white;
  font-size: 28px;
  margin: 0;
}
.welcome-text {
  font-size: 1rem;
  line-height: 1.6;
  opacity: 0.85;
  color: rgba(204, 219, 240, 0.973);
  text-align: left;
  margin-bottom: 0;
}

.login-form-panel {
  flex-basis: 55%;
  padding: clamp(2.5rem, 4vw, 4rem);
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: var(--text-base);
}
.form-title {
  font-size: 28px;
  color: var(--text-strong);
  margin-bottom: 2rem;
  text-align: left;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.input-group {
  position: relative;
}
.input-icon {
  position: absolute;
  left: 14px;
  top: 13px;
  width: 20px;
  height: 20px;
  color: var(--text-muted);
  pointer-events: none;
}
input {
  font-family: 'Inter', sans-serif;
  padding: 12px 44px;
  border-radius: 10px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text-base);
}
.password-toggle {
  position: absolute;
  right: 14px;
  top: 13px;
  cursor: pointer;
  color: var(--text-muted);
  transition: color 0.2s ease;
  background: none;
  border: none;
  display: flex;
}
.password-toggle:hover {
  color: #93c5fd;
}

.submit-button {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 13px;
  background: linear-gradient(135deg, #1e3a8a, #2563eb 45%, #22d3ee 100%);
  color: #f8fafc;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  font-size: 0.95rem;
  font-weight: 700;
  min-height: 46px;
  margin: 10px auto 0;
  width: 100%;
  max-width: 320px;
  box-shadow:
    0 15px 35px rgba(37, 99, 235, 0.35),
    0 6px 15px rgba(34, 197, 235, 0.28);
}
.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 20px 30px rgba(37, 99, 235, 0.35);
}
.submit-button:disabled {
  background: rgba(148, 163, 184, 0.4);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.error-message {
  padding: 12px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  color: #fecaca;
  background-color: rgba(248, 113, 113, 0.15);
  border: 1px solid rgba(248, 113, 113, 0.35);
}

.loading-session-text {
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 20px 0;
}

.strength-meter {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: -5px;
  margin-bottom: 5px;
}
.strength-bar-track {
  flex-grow: 1;
  height: 8px;
  background: rgba(148, 163, 184, 0.25);
  border-radius: 4px;
  overflow: hidden;
}
.strength-bar {
  height: 100%;
  width: 0%;
  background: #f87171;
  transition:
    width 0.3s ease,
    background-color 0.3s ease;
}
.strength-text {
  font-size: 0.8rem;
  font-weight: 600;
  width: 70px;
  text-align: right;
  color: var(--text-muted);
  transition: color 0.3s ease;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0 0 10px 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.requirements-list li {
  font-size: 0.8rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
  transition: color 0.3s ease;
}
.requirements-list li.valid {
  color: #22c55e;
  font-weight: 500;
}
.requirements-list li svg {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  stroke-width: 3;
  transition: all 0.3s ease;
}
.requirements-list li:not(.valid) svg {
  color: #f87171;
}

.match-error {
  display: block;
  font-size: 0.8rem;
  font-weight: 500;
  margin-top: -5px;
  color: #f87171;
}
.match-error.valid {
  color: #22c55e;
}

.success-animation-container {
  text-align: center;
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(120, 172, 255, 0.28);
  border-radius: 18px;
  background: linear-gradient(145deg, rgba(9, 14, 28, 0.9), rgba(7, 12, 26, 0.82));
  box-shadow:
    0 25px 60px rgba(2, 6, 23, 0.7),
    0 0 50px rgba(34, 211, 238, 0.12),
    inset 0 0 0 1px rgba(255, 255, 255, 0.02);
  position: relative;
  overflow: hidden;
}
.success-animation-container::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  top: -40px;
  right: -20px;
  background: radial-gradient(circle, rgba(34, 211, 238, 0.28), transparent 62%);
  filter: blur(28px);
  opacity: 0.8;
  pointer-events: none;
}
.success-animation-container::after {
  content: '';
  position: absolute;
  width: 260px;
  height: 260px;
  bottom: -80px;
  left: -20px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.22), transparent 65%);
  filter: blur(28px);
  opacity: 0.65;
  pointer-events: none;
}
.success-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-strong);
  margin-bottom: 10px;
}
.success-text {
  color: var(--text-base);
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
  max-width: 320px;
}
.success-checkmark {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: block;
  stroke-width: 3.2;
  stroke: #22d3ee;
  stroke-miterlimit: 10;
  margin: 0 auto 20px;
  box-shadow: inset 0px 0px 0px #22d3ee;
  animation:
    fill 0.4s ease-in-out 0.4s forwards,
    scale 0.3s ease-in-out 0.9s both;
}
.checkmark-circle {
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  stroke-width: 3.2;
  stroke-miterlimit: 10;
  stroke: #22d3ee;
  fill: none;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}
.checkmark-check {
  transform-origin: 50% 50%;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke: #22c55e;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}
@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
@keyframes scale {
  0%,
  100% {
    transform: none;
  }
  50% {
    transform: scale3d(1.1, 1.1, 1);
  }
}
@keyframes fill {
  100% {
    box-shadow: inset 0px 0px 0px 40px #0b4660;
  }
}

.loading-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(2, 6, 23, 0.8);
  backdrop-filter: blur(6px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.loading-text {
  margin-top: 20px;
  font-size: 1.1rem;
  color: var(--text-base);
  font-weight: 600;
}
.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(148, 163, 184, 0.25);
  border-top-color: var(--primary-600);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 800px) {
  .login-box {
    flex-direction: column;
  }
  .login-info-panel {
    flex-basis: auto;
    padding: 2.5rem;
    text-align: center;
  }
  .logo-header {
    justify-content: center;
  }
  .login-form-panel {
    flex-basis: auto;
    padding: 2.5rem;
  }
  .form-title,
  .welcome-text {
    text-align: center;
  }
  .requirements-list {
    grid-template-columns: 1fr;
  }
}
</style>
