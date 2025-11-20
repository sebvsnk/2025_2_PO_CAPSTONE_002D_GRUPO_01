<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// --- Lógica (con corrección) ---
const router = useRouter()
const authStore = useAuthStore()
const email = ref('')
const password = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const loading = ref(false)
const showPassword = ref(false)

// --- 🌟 FUNCIÓN HANDLELOGIN CORREGIDA 🌟 ---
const handleLogin = async () => {
  loading.value = true
  errorMsg.value = '' // Limpiamos errores previos
  successMsg.value = '' // Limpiamos mensajes de éxito previos
  try {
    // 1. Se espera a que el store termine el login y cargue el perfil del usuario
    await authStore.login(email.value, password.value)

    // 2. Si el login fue exitoso, la VISTA redirige al Dashboard
    router.push({ name: 'Dashboard' })
  } catch {
    errorMsg.value = 'Correo o contraseña incorrectos. Por favor, verifica tus credenciales.'
  } finally {
    loading.value = false
  }
}
// --- FIN DE LA CORRECCIÓN ---
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
          Bienvenido al sistema de gestión de flota. Por favor, ingresa tus credenciales.
        </p>
      </div>

      <div class="login-form-panel">
        <h2 class="form-title">Iniciar Sesión</h2>
        <form @submit.prevent="handleLogin">
          <div class="input-group">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              class="input-icon"
            >
              <path
                d="M2.5 5.75A2.75 2.75 0 0 1 5.25 3h9.5A2.75 2.75 0 0 1 17.5 5.75v8.5A2.75 2.75 0 0 1 14.75 17h-9.5A2.75 2.75 0 0 1 2.5 14.25v-8.5Zm2.08.266 5.02 3.35a.75.75 0 0 0 .84 0l5.02-3.35a.75.75 0 1 0-.84-1.232L10 7.868 5.42 4.784a.75.75 0 0 0-.84 1.232Z"
              />
            </svg>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="tu@correo.com"
              autocomplete="username"
              required
              :disabled="loading"
            />
          </div>

          <div class="input-group">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              class="input-icon"
            >
              <path
                fill-rule="evenodd"
                d="M10 1a4.5 4.5 0 0 0-4.5 4.5V9H5a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6a2 2 0 0 0-2-2h-.5V5.5A4.5 4.5 0 0 0 10 1Zm3 8V5.5a3 3 0 1 0-6 0V9h6Z"
                clip-rule="evenodd"
              />
            </svg>
            <input
              id="password"
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="••••••••"
              autocomplete="current-password"
              required
              :disabled="loading"
            />
            <button type="button" class="password-toggle" @click="showPassword = !showPassword">
              <svg
                v-if="!showPassword"
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
                <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                <circle cx="12" cy="12" r="3" />
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
                <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                <path
                  d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"
                />
                <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                <line x1="2" x2="22" y1="2" y2="22" />
              </svg>
            </button>
          </div>

          <button type="submit" :disabled="loading" class="submit-button">
            <div v-if="loading" class="spinner"></div>
            <span v-else>Iniciar Sesión</span>
          </button>
        </form>

        <a href="#" class="forgot-link" @click.prevent="router.push('/forgot-password')">
          ¿Olvidaste tu contraseña?
        </a>
        <button class="public-status-button" @click="router.push('/status')">
          Ver Estado de Vehículo (Externo)
        </button>

        <Transition name="fade">
          <div v-if="errorMsg" class="error-message">{{ errorMsg }}</div>
        </Transition>
        <Transition name="fade">
          <div v-if="successMsg" class="success-message">{{ successMsg }}</div>
        </Transition>
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
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  background: transparent;
  padding: clamp(20px, 4vw, 60px);
}

.login-container::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(200px 200px at 18% 30%, rgba(34, 197, 94, 0.18), transparent 65%),
    radial-gradient(820px 520px at 24% 26%, rgba(59, 130, 246, 0.12), transparent 60%),
    linear-gradient(140deg, rgba(2, 6, 23, 0.95), rgba(7, 12, 25, 0.96));
  filter: blur(30px);
  animation: orbSingle 14s ease-in-out infinite alternate;
  z-index: 0;
}
.login-container::after {
  content: none;
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
@keyframes orbSingle {
  0% {
    transform: translate3d(-6%, 0, 0) scale(1);
    opacity: 0.5;
  }
  50% {
    transform: translate3d(8%, 0, 0) scale(1.08);
    opacity: 0.65;
  }
  100% {
    transform: translate3d(-6%, 0, 0) scale(1);
    opacity: 0.5;
  }
}

.login-box {
  width: 100%;
  max-width: 960px;
  display: flex;
  background:
    radial-gradient(120% 130% at 30% 50%, rgba(59, 130, 246, 0.18), transparent 60%),
    radial-gradient(120% 130% at 70% 50%, rgba(30, 64, 175, 0.12), transparent 65%),
    radial-gradient(150% 140% at 50% 50%, rgba(15, 23, 42, 0.18), transparent 70%),
    linear-gradient(135deg, rgba(9, 13, 25, 0.9), rgba(8, 12, 23, 0.9));
  border-radius: 24px;
  box-shadow:
    0 40px 90px rgba(2, 6, 23, 0.7),
    0 0 30px rgba(34, 197, 94, 0.12);
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.25);
  backdrop-filter: blur(18px);
  animation: slideUpFadeIn 0.6s ease-out forwards;
  position: relative;
}
.login-box::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    rgba(15, 23, 42, 0) 35%,
    rgba(15, 23, 42, 0.1) 50%,
    rgba(15, 23, 42, 0) 65%
  );
  mix-blend-mode: screen;
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
/* --- FIX PARA AUTOCOMPLETADO --- */
/* Esto quita el fondo blanco feo de Chrome/Edge */
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  /* 1. Cambia el color del texto a gris claro */
  -webkit-text-fill-color: #e2e8f0 !important;

  /* 2. "Pinta" el fondo con una sombra interior del color de tu tarjeta (#1e293b) */
  -webkit-box-shadow: 0 0 0 30px #1e293b inset !important;

  /* 3. Opcional: Mantiene el fondo transparente el mayor tiempo posible */
  transition: background-color 5000s ease-in-out 0s;
}
.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
}
.password-toggle svg {
  width: 20px;
  height: 20px;
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
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
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

.forgot-link {
  margin-top: 1rem;
  display: block;
  text-align: center;
  color: #60a5fa;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s ease;
}
.forgot-link:hover {
  color: #93c5fd;
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
.success-message {
  margin-top: 1rem;
  background: rgba(34, 197, 94, 0.12);
  color: #bbf7d0;
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid rgba(34, 197, 94, 0.3);
  font-weight: 600;
  text-align: center;
}

.public-status-button + .error-message,
.public-status-button + .success-message {
  margin-top: 0.8rem;
}

@media (max-width: 900px) {
  .login-box {
    flex-direction: column;
  }
  .login-info-panel {
    padding: 2.5rem;
    text-align: center;
  }
  .logo-header {
    justify-content: center;
  }
  .welcome-text {
    text-align: center;
  }
}

@media (max-width: 600px) {
  .login-form-panel {
    padding: 2rem;
  }
}
</style>
