<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// --- Lógica (sin cambios, ya era correcta) ---
const authStore = useAuthStore()
const email = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)

const handleForgotPassword = async () => {
  loading.value = true
  errorMsg.value = ''
  successMsg.value = ''

  try {
    // Esto llama a Supabase, que envía el correo con el link que apunta a /reset-password
    await authStore.handlePasswordReset(email.value)

    successMsg.value =
      'Revisa tu correo (bandeja de entrada y spam) para establecer tu nueva contraseña.'
  } catch {
    // Si Supabase devuelve un 400 (ej. email no existe), lo manejamos genéricamente
    errorMsg.value = 'Error: Asegúrate de que el correo sea válido e intenta más tarde.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-info-panel">
        <div class="logo-header">
          <div class="logo-icon">APT</div>
          <h1>Taller PepsiCo</h1>
        </div>
        <p class="welcome-text">
          Ingresa tu correo electrónico para recibir un enlace de recuperación.
        </p>
      </div>

      <div class="login-form-panel">
        <div v-if="!successMsg">
          <h2 class="form-title">Recuperar Contraseña</h2>

          <form @submit.prevent="handleForgotPassword">
            <div class="input-group">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                class="input-icon"
              >
                <path d="M2.5 5.75A2.75 2.75 0 0 1 5.25 3h9.5A2.75 2.75 0 0 1 17.5 5.75v8.5A2.75 2.75 0 0 1 14.75 17h-9.5A2.75 2.75 0 0 1 2.5 14.25v-8.5Zm2.08.266 5.02 3.35a.75.75 0 0 0 .84 0l5.02-3.35a.75.75 0 1 0-.84-1.232L10 7.868 5.42 4.784a.75.75 0 0 0-.84 1.232Z" />
              </svg>
              <input
                id="email"
                v-model="email"
                type="email"
                placeholder="tu@correo.com"
                required
                :disabled="loading"
              />
            </div>

            <button type="submit" :disabled="loading" class="submit-button">
              <div v-if="loading" class="spinner"></div>
              <span v-else>Enviar Enlace</span>
            </button>
          </form>
          <Transition name="fade">
            <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
          </Transition>
        </div>

        <div v-else class="success-animation-container">
          <svg class="success-checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none" />
            <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
          </svg>
          <h3 class="success-title">¡Enviado!</h3>
          <p class="success-text">{{ successMsg }}</p>
        </div>

        <button class="public-status-button" @click="router.push('/login')">
          ← Volver al Login
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

.login-container {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background: transparent;
  overflow: hidden;
  padding: clamp(20px, 6vw, 80px);
}
.login-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(900px 540px at 20% 22%, rgba(59, 130, 246, 0.16), transparent 60%),
    radial-gradient(780px 500px at 82% 18%, rgba(34, 197, 94, 0.1), transparent 62%),
    linear-gradient(140deg, rgba(2, 6, 23, 0.95), rgba(7, 12, 25, 0.96));
  filter: blur(24px);
  animation: orbSingle 14s ease-in-out infinite alternate;
  z-index: 0;
}
.login-container > * {
  position: relative;
  z-index: 1;
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
  background:
    radial-gradient(110% 120% at 22% 40%, rgba(59, 130, 246, 0.16), transparent 55%),
    radial-gradient(110% 120% at 78% 60%, rgba(59, 130, 246, 0.12), transparent 60%),
    linear-gradient(135deg, rgba(9, 13, 25, 0.9), rgba(8, 12, 23, 0.9));
  border-radius: 24px;
  box-shadow:
    0 40px 90px rgba(2, 6, 23, 0.7),
    0 0 30px rgba(34, 197, 94, 0.12);
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.22);
  backdrop-filter: blur(18px);
  animation: slideUpFadeIn 0.6s ease-out forwards;
  position: relative;
}
.login-box::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(15, 23, 42, 0) 38%, rgba(15, 23, 42, 0.12) 50%, rgba(15, 23, 42, 0) 62%);
  pointer-events: none;
  z-index: 1;
}

.login-info-panel {
  flex-basis: 45%;
  background:
    radial-gradient(220px 220px at 18% 30%, rgba(34, 197, 94, 0.18), transparent 65%),
    radial-gradient(820px 520px at 24% 26%, rgba(59, 130, 246, 0.12), transparent 60%),
    linear-gradient(140deg, #0b162d, #123159);
  padding: clamp(2.5rem, 4vw, 4rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: var(--text-base);
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
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid rgba(148, 163, 184, 0.28);
  color: #e2e8f0;
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
  opacity: 0.9;
  color: var(--text-base);
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
  top: 50%;
  transform: translateY(-50%);
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
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.28);
  color: var(--text-base);
}
input:focus {
  border-color: rgba(59, 130, 246, 0.6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}
input::-webkit-autofill {
  box-shadow: 0 0 0px 1000px rgba(15, 23, 42, 0.88) inset;
  -webkit-text-fill-color: var(--text-base);
}

.submit-button {
  margin-top: 10px;
  padding: 14px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.submit-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 20px 30px rgba(37, 99, 235, 0.35);
}
.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.forgot-link,
.success-text {
  color: var(--text-muted);
}

.public-status-button {
  margin-top: 1.25rem;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  cursor: pointer;
  font-weight: 600;
  color: var(--text-base);
  width: 100%;
  transition: all 0.2s ease;
}
.public-status-button:hover {
  background: rgba(59, 130, 246, 0.15);
  color: var(--text-strong);
}

.error-message {
  margin-top: 1rem;
  background: rgba(248, 113, 113, 0.15);
  color: #fecaca;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(248, 113, 113, 0.3);
  font-weight: 600;
  text-align: center;
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

.success-message {
  display: none;
}
</style>


