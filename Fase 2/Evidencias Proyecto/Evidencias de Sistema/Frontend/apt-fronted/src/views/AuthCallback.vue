<template>
  <div class="callback-container">
    <div class="loading-box">
      <h1>Procesando Sesión...</h1>
      <p v-if="!errorMsg">Verificando tu token de acceso. Serás redirigido en un momento.</p>

      <div v-if="errorMsg" class="error-message">
        {{ errorMsg }}
        <p>Redirigiendo al Login en 3 segundos.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from '@/services/supabaseClient'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const authStore = useAuthStore()
const errorMsg = ref(null)

onMounted(async () => {
  errorMsg.value = null

  // 1. Obtener la sesión de Supabase (lee el token del URL hash y lo guarda en el Local Storage)
  // Esto es vital después de un recovery o invitation link.
  const {
    data: { session },
    error: sessionError,
  } = await supabase.auth.getSession()

  // --- VALIDACIÓN DE SESIÓN ---
  if (sessionError || !session || !session.access_token) {
    console.error('Error al obtener sesión de Supabase:', sessionError || 'Sesión no encontrada.')
    errorMsg.value = 'El enlace de recuperación/invitación expiró o es inválido.'

    // Redireccionar al login después de un mensaje de error
    setTimeout(() => {
      router.push('/login')
    }, 3000)
    return
  }

  // --- CARGA DE PERFIL (Django API) ---
  try {
    // Establecer el token en el Store para que las llamadas a Django funcionen
    authStore.token = session.access_token

    // Llamar a la API de Django (http://127.0.0.1:8000/api/v1/mi-perfil/)
    await authStore.fetchUserProfile(session.access_token)

    // ÉXITO TOTAL: Redirigir al Home
    router.push('/')
  } catch (e) {
    // Si la API de Django falla (aunque Supabase haya dado el token), forzar el cierre
    console.error('Error al obtener perfil de Django:', e)
    errorMsg.value =
      'El perfil de usuario no se pudo cargar desde la API. Contacte al administrador.'

    // Forzar cierre de sesión en Supabase y el Store
    await authStore.logout()

    setTimeout(() => {
      router.push('/login')
    }, 3000)
  }
})
</script>

<style scoped>
.callback-container {
  display: grid;
  place-items: center;
  min-height: 100vh;
  background-color: #f4f4f4;
}
.loading-box {
  text-align: center;
  padding: 3rem;
  background: var(--surface-highlight);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.error-message {
  color: #ef4444;
  margin-top: 1rem;
  padding: 10px;
  border: 1px solid #f87171;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 4px;
}
</style>

