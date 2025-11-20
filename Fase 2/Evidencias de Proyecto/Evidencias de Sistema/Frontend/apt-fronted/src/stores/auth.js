// apt-fronted/src/stores/auth.js (Corregido)
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { supabase } from '@/services/supabaseClient'
// import router from '@/router' // <-- Esta línea permanece eliminada

const API_URL = import.meta.env.VITE_API_URL

export const useAuthStore = defineStore('auth', () => {
  // --- Estado Reactivo ---
  const user = ref(null)
  const token = ref(null)
  const flashMessage = ref(null)

  // --- AÑADIR ESTA LÍNEA ---
  const isInitialized = ref(false)
  let sessionCheckPromise = null
  // -------------------------

  // Inicia en 'true' por defecto.
  const isLoadingUser = ref(true)
  const loadingMessage = ref('Cargando sesión...')

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value)
  const userRole = computed(() => user.value?.rol || null)
  const userName = computed(() => user.value?.nombre || 'Usuario')

  // --- Funciones Core ---
  async function fetchUserProfile(jwt) {
    console.log('[auth] fetchUserProfile token:', jwt?.slice(0, 20))
    const response = await fetch(`${API_URL}/mi-perfil/`, {
      headers: {
        Authorization: `Bearer ${jwt}`,
      },
    })
    if (!response.ok) {
      const errorBody = await response.text()
      console.error('[auth] Perfil API falló:', response.status, errorBody)
      throw new Error('Error al obtener el perfil de usuario desde la API.')
    }
    user.value = await response.json()
  }

  // --- 🌟 FUNCIÓN LOGIN CORREGIDA 🌟 ---
  async function login(email, password) {
    loadingMessage.value = 'Iniciando sesión...'
    isLoadingUser.value = true

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })
      if (error) throw error
      token.value = data.session.access_token
      await fetchUserProfile(token.value)

      // router.push({ name: 'Dashboard' }) // <-- LÍNEA ELIMINADA (Esta es la línea 52 del error)
    } catch (error) {
      console.error('Error en el login de Supabase:', error)
      throw error // Propaga el error a LoginView
    } finally {
      isLoadingUser.value = false
    }
  }

  async function logout(message = 'Sesión cerrada correctamente.') {
    loadingMessage.value = 'Cerrando sesión...'
    isLoadingUser.value = true

    await new Promise((r) => setTimeout(r, 750))

    user.value = null
    token.value = null
    flashMessage.value = message

    await supabase.auth.signOut()
    isLoadingUser.value = false
  }

  async function checkSession() {
    loadingMessage.value = 'Cargando sesión...'
    isLoadingUser.value = true

    try {
      const { data } = await supabase.auth.getSession()
      if (data.session) {
        token.value = data.session.access_token
        await fetchUserProfile(token.value)
      } else {
        // Limpiar estado si no hay sesión
        token.value = null
        user.value = null
      }
    } catch (error) {
      console.error('Fallo al verificar la sesión:', error)
      token.value = null
      user.value = null
    } finally {
      // Marcar como inicializado SOLO después de que checkSession termine
      isInitialized.value = true
      isLoadingUser.value = false
    }
  }

  async function handlePasswordReset(email) {
    if (!email) {
      throw new Error('Por favor, ingresa tu correo para recuperar la contraseña.')
    }
    const REDIRECT_URL = 'http://localhost:5173/reset-password'
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: REDIRECT_URL,
    })
    if (error) throw error
  }

  // --- REEMPLAZAR initializeStore CON ESTO ---
  async function initializeStore() {
    // Si ya se inicializó, no hacer nada.
    if (isInitialized.value) return

    // Si checkSession no se ha empezado a ejecutar, lanzarlo
    if (!sessionCheckPromise) {
      sessionCheckPromise = checkSession()
    }

    // Esperar a que la promesa de checkSession (nueva o en curso) termine
    await sessionCheckPromise

    // Limpiar la promesa para futuras recargas (ej. F5)
    sessionCheckPromise = null
  }
  // --- Retorno del Store ---
  return {
    user,
    token,
    isAuthenticated,
    userRole,
    userName,
    flashMessage,
    isLoadingUser,
    loadingMessage,
    login,
    logout,
    checkSession,
    handlePasswordReset,
    initializeStore, // Asegúrate de que esta función se retorna
    fetchUserProfile,
  }
})
