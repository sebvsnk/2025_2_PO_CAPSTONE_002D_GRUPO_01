<script setup>
import { onMounted, computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

// Comprobar sesión al cargar
onMounted(() => {
  authStore.checkSession()
})

// Páginas públicas (no muestran layout)
const isPublicRoute = computed(() => {
  const current = router.currentRoute.value
  const name = current.name
  const path = current.path || ''
  const locPath = window.location.pathname || ''
  return (
    ['Login', 'ForgotPassword', 'ResetPassword', 'PublicStatus', 'AuthCallback'].includes(name) ||
    path.startsWith('/reset-password') ||
    locPath.startsWith('/reset-password')
  )
})

// Estado global
const isAuthenticated = computed(() => authStore.isAuthenticated)

// --- Lógica de carga diferencial ---
const isLoading = computed(() => authStore.isLoadingUser)
const loadingMessage = computed(() => authStore.loadingMessage)

const showPageSkeleton = computed(() => isLoading.value)

// Flags de rol
const is_admin = computed(() => authStore.userRole === 'ADMIN')
const is_supervisor = computed(() => authStore.userRole === 'SUPERVISOR')
const is_mecanico = computed(() => authStore.userRole === 'MECANICO')
const is_porteria = computed(() => authStore.userRole === 'PORTERIA')
const is_guardia = computed(() => authStore.userRole === 'GUARDIA')
const is_analista = computed(() => authStore.userRole === 'ANALISTA')

// Utilidades
const isRouteActive = (routeNames) => {
  const names = Array.isArray(routeNames) ? routeNames : [routeNames]
  return names.includes(router.currentRoute.value.name)
}
const navigateTo = (name) => router.push({ name })

const getRoleTitle = (role) => {
  switch (role) {
    case 'ADMIN':
      return 'Administrador Principal'
    case 'SUPERVISOR':
      return 'Supervisor de Flota'
    case 'MECANICO':
      return 'Mecánico de Taller'
    case 'PORTERIA':
      return 'Personal de Portería'
    case 'GUARDIA':
      return 'Personal de Guardia'
    case 'ANALISTA':
      return 'Analista/Indicadores'

    // --- AGREGA ESTO AQUÍ ---
    case 'CHOFER':
      return 'Chofer'
    // ------------------------

    default:
      return 'Usuario Registrado'
  }
}

// Sidebar responsive (off-canvas)
const sidebarOpen = ref(false)
const toggleSidebar = () => (sidebarOpen.value = !sidebarOpen.value)
const closeSidebar = () => (sidebarOpen.value = false)
watch(() => router.currentRoute.value.fullPath, closeSidebar)

// --- LÓGICA DEL MODAL DE CONFIRMACIÓN ---
const showLogoutConfirm = ref(false)

const requestLogout = () => {
  showLogoutConfirm.value = true
}
const cancelLogout = () => {
  showLogoutConfirm.value = false
}

// --- FUNCIÓN DE LOGOUT CORREGIDA ---
const confirmLogout = async () => {
  showLogoutConfirm.value = false
  await authStore.logout('Has cerrado tu sesión.') // 1. Se espera a que el store termine el logout
  router.push({ name: 'Login' }) // 2. Se redirige al Login
}
</script>

<template>
  <Transition name="fade">
    <div v-if="isLoading" class="loading-overlay fullscreen">
      <div class="full-loader">
        <div class="full-spinner"></div>
        <div class="full-text">
          <h2>{{ loadingMessage || 'Cargando sesión...' }}</h2>
          <p>
            {{
              loadingMessage && loadingMessage.includes('Redireccionando a crear contrase')
                ? 'Preparando pantalla de restablecimiento...'
                : ''
            }}
          </p>
        </div>
      </div>
    </div>
  </Transition>

  <div v-if="!isPublicRoute" class="dashboard-layout">
    <div v-show="sidebarOpen" class="backdrop" @click="closeSidebar"></div>

    <nav v-if="isAuthenticated" class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-icon">APT</div>
        <span>Gestión Taller</span>
      </div>
      <div class="menu-links">
        <a
          class="nav-item"
          :class="{ 'is-active': isRouteActive(['Dashboard', 'VehicleCreate', 'OtCreate']) }"
          @click.prevent="navigateTo('Dashboard')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M9 3v18" />
            <path d="M21 9H3" />
            <path d="M21 15H3" />
          </svg>
          <span>Acceso Rápido</span>
        </a>
        <a
          class="nav-item profile-link"
          :class="{ 'is-active': isRouteActive('MiPerfil') }"
          @click.prevent="navigateTo('MiPerfil')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
          <span>Mi Perfil</span>
        </a>
        <a
          v-if="is_supervisor"
          class="nav-item"
          :class="{
            'is-active': isRouteActive([
              'SupervisorDashboard',
              'OtDetail',
              'TaskList',
              'OtHistorial',
            ]),
          }"
          @click.prevent="navigateTo('SupervisorDashboard')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M12 2v20M17 5H7M17 19H7" />
          </svg>
          <span>Órdenes de Trabajo</span>
        </a>
        <a
          v-if="is_admin"
          class="nav-item"
          :class="{
            'is-active': isRouteActive(['AdminUsers', 'AdminUserCreate', 'AdminUserDetail']),
          }"
          @click.prevent="navigateTo('AdminUsers')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
            <circle cx="8.5" cy="7" r="4" />
            <path d="M18 13v6M21 16h-6" />
          </svg>
          <span>Gestión de Usuarios</span>
        </a>

        <a
          v-if="is_analista || is_supervisor"
          class="nav-item"
          :class="{ 'is-active': isRouteActive('ReportsView') }"
          @click.prevent="navigateTo('ReportsView')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M3 3v18h18" />
            <path d="M18 17V9" />
            <path d="M12 17V4" />
            <path d="M6 17v-3" />
          </svg>
          <span>Reportes y Métricas</span>
        </a>
        <a
          v-if="is_admin || is_analista"
          class="nav-item"
          :class="{ 'is-active': isRouteActive('AuditLogView') }"
          @click.prevent="navigateTo('AuditLogView')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M20 12V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h7" />
            <path d="M14 18l-4-4l-4 4" />
          </svg>
          <span>Auditoría</span>
        </a>
        <a
          v-if="is_porteria || is_guardia"
          class="nav-item"
          :class="{ 'is-active': isRouteActive('CheckInView') }"
          @click.prevent="navigateTo('CheckInView')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M17 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2z" />
            <path d="M12 15h0" />
            <path d="M12 9v4" />
          </svg>
          <span>Ingreso de Vehículos</span>
        </a>
        <a
          v-if="is_mecanico"
          class="nav-item"
          :class="{
            'is-active': isRouteActive([
              'MechanicTasks',
              'TaskDetail',
              'TaskEvidence',
              'TaskRepuestos',
            ]),
          }"
          @click.prevent="navigateTo('MechanicTasks')"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M21 12.79A9 9 0 1 1 11.21 3 9 9 0 0 0 21 12.79z" />
          </svg>
          <span>Mis Tareas</span>
        </a>
      </div>
      <p class="sidebar-footer">Capstone 2025</p>
    </nav>

    <div v-else class="sidebar-skeleton"></div>

    <main class="main-content">
      <header class="main-header">
        <button class="burger" aria-label="Abrir menú" @click="toggleSidebar">
          <span></span><span></span><span></span>
        </button>

        <div class="header-titles">
          <h2 class="section-title">
            {{
              showPageSkeleton
                ? 'Cargando...'
                : router.currentRoute.value.meta.title || router.currentRoute.value.name
            }}
          </h2>
          <p class="section-subtitle">
            {{
              showPageSkeleton
                ? 'Verificando sesión...'
                : router.currentRoute.value.meta.subtitle || 'Panel de control y gestión.'
            }}
          </p>
        </div>

        <div v-if="isAuthenticated" class="header-actions-right">
          <div class="user-info-pill">
            <span class="user-name-header">{{ authStore.userName || 'Usuario' }}</span>
            <span :class="['role-tag-header', authStore.userRole?.toLowerCase()]">
              {{ getRoleTitle(authStore.userRole) }}
            </span>
          </div>
          <button class="logout-button-header" :disabled="isLoading" @click="requestLogout">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
              <polyline points="16 17 21 12 16 7" />
              <line x1="21" x2="9" y1="12" y2="12" />
            </svg>
          </button>
        </div>
      </header>

      <div class="content-body-reworked">
        <div v-if="showPageSkeleton" class="page-loading-skeleton">
          <div class="skeleton-card skeleton-info"></div>
          <div class="skeleton-card skeleton-desc"></div>
          <div class="skeleton-card skeleton-box"></div>
          <div class="skeleton-card skeleton-box"></div>
        </div>

        <router-view v-else v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>

  <div v-else>
    <router-view v-slot="{ Component }">
      <transition name="page-fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>

  <Transition name="modal-fade">
    <div v-if="showLogoutConfirm" class="confirm-modal-overlay" @click.self="cancelLogout">
      <div class="confirm-modal-content">
        <div class="modal-icon-container">
          <svg
            class="modal-icon"
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path
              d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
            />
            <line x1="12" x2="12" y1="9" y2="13" />
            <line x1="12" x2="12.01" y1="17" y2="17" />
          </svg>
        </div>
        <h3>¿Estás seguro?</h3>
        <p>Estás a punto de cerrar tu sesión actual.</p>
        <div class="modal-actions">
          <button class="modal-btn-cancel" @click="cancelLogout">Cancelar</button>
          <button class="modal-btn-confirm" @click="confirmLogout">Sí, Salir</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style>
/* App.vue — <style> */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --primary-500: #5e9bff;
  --primary-600: #3b82f6;
  --primary-700: #2563eb;
  --primary-800: #1d3ba6;
  --accent-50: #1b2439;
  --accent-100: #23304a;
  --ink-900: #f8fafc;
  --muted-600: #9caec8;
  --app-bg-1: #020713;
  --app-bg-2: #0c1527;
  --app-vignette: rgba(59, 130, 246, 0.18);
  --canvas-bg: #050c19;
  --surface-muted: #0d172a;
  --surface-card: #131f35;
  --surface-highlight: #1b2d4c;
  --text-strong: #f8fafc;
  --text-base: #e2e8f0;
  --text-muted: #9caec8;
  --input-bg: rgba(16, 25, 43, 0.95);
  --input-border: rgba(148, 163, 184, 0.45);
  --input-focus: rgba(94, 155, 255, 0.95);
  --input-placeholder: rgba(148, 163, 184, 0.6);
  --radius: 16px;
  --shadow-sm: 0 12px 30px rgba(2, 6, 23, 0.55);
  --shadow-md: 0 28px 70px rgba(2, 6, 23, 0.65);
  --card-bg: var(--surface-card);
  --card-border: rgba(148, 163, 184, 0.28);
  --card-shadow: 0 35px 70px rgba(2, 6, 23, 0.6);
}

html,
body {
  margin: 0;
  font-family:
    'Inter',
    system-ui,
    -apple-system,
    Segoe UI,
    Roboto,
    Ubuntu,
    'Helvetica Neue',
    sans-serif;
}

body {
  min-height: 100vh;
  background: var(--canvas-bg);
  position: relative;
  overflow-x: hidden;
  color: var(--text-base);
}

body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background:
    radial-gradient(800px 400px at 10% -10%, var(--app-vignette) 0%, transparent 55%),
    radial-gradient(700px 380px at 100% 0%, var(--app-vignette) 0%, transparent 60%),
    linear-gradient(135deg, var(--app-bg-1), var(--app-bg-2));
  transform: translateZ(0);
}

/* ===== Loading & Transitions ===== */
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
.loading-overlay.fullscreen {
  background:
    radial-gradient(circle at 20% 30%, rgba(56, 189, 248, 0.14), transparent 48%),
    radial-gradient(circle at 80% 20%, rgba(16, 185, 129, 0.12), transparent 50%),
    linear-gradient(145deg, rgba(2, 6, 23, 0.94), rgba(7, 12, 25, 0.96));
  backdrop-filter: blur(10px);
}
.loading-text {
  margin-top: 20px;
  font-size: 1.1rem;
  color: var(--text-base);
  font-weight: 600;
}
.full-loader {
  text-align: center;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.full-spinner {
  width: 76px;
  height: 76px;
  border-radius: 999px;
  border: 6px solid rgba(255, 255, 255, 0.12);
  border-top-color: #22d3ee;
  border-right-color: #10b981;
  animation: spin 0.9s linear infinite;
  margin: 0 auto;
  box-shadow: 0 0 30px rgba(32, 98, 204, 0.35);
}
.full-text h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 800;
}
.full-text p {
  margin: 0;
  opacity: 0.8;
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
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.2s ease;
}
.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
}

/* ===== Layout base ===== */
.dashboard-layout {
  min-height: 100vh;
  padding: 24px;
  gap: 24px;
  display: grid;
  grid-template-columns: minmax(240px, 280px) 1fr;
  background:
    radial-gradient(circle at top, rgba(59, 130, 246, 0.08), transparent 55%),
    radial-gradient(circle at 20% 20%, rgba(34, 197, 94, 0.06), transparent 45%),
    rgba(2, 6, 23, 0.95);
  position: relative;
}
.dashboard-layout::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 80% 0%, rgba(255, 255, 255, 0.05), transparent 35%);
}

/* ===== Sidebar ===== */
.sidebar {
  display: flex;
  flex-direction: column;
  background: linear-gradient(200deg, rgba(6, 10, 25, 0.98), rgba(12, 26, 54, 0.92));
  color: var(--text-base);
  padding: 1.6rem 1.2rem 1.4rem;
  border-radius: 28px;
  box-shadow:
    0 30px 60px rgba(2, 6, 23, 0.65),
    inset 0 0 0 1px rgba(148, 163, 184, 0.18);
  width: 100%;
  box-sizing: border-box;
  position: sticky;
  top: 16px;
  align-self: start;
  overflow: hidden;
}
.sidebar::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(140deg, rgba(59, 130, 246, 0.12), transparent 55%);
  pointer-events: none;
}
.sidebar::after {
  content: '';
  position: absolute;
  width: 180px;
  height: 180px;
  top: -60px;
  right: -50px;
  background: radial-gradient(circle, rgba(34, 197, 94, 0.2), transparent 60%);
  filter: blur(8px);
  pointer-events: none;
}
/* --- SKELETON SIDEBAR --- */
.sidebar-skeleton {
  background: rgba(15, 23, 42, 0.65);
  opacity: 0.5;
  border-radius: var(--radius);
  width: 260px;
  min-height: calc(100vh - 40px);
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--text-strong);
  margin-bottom: 1.6rem;
  padding: 0 4px;
  position: relative;
  z-index: 1;
}
.logo-icon {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border-radius: 14px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0));
  color: #fff;
  font-weight: 900;
  font-size: 16px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.25);
}
.menu-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: auto;
  position: relative;
  z-index: 1;
}
.sidebar-footer {
  margin-top: 12px;
  color: rgba(226, 232, 240, 0.88);
  font-weight: 700;
  font-size: 0.85rem;
  text-align: center;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  cursor: pointer;
  color: rgba(226, 232, 240, 0.9);
  text-decoration: none;
  font-weight: 600;
  border: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(6px);
  transition:
    background 0.2s ease,
    color 0.2s ease,
    transform 0.2s ease,
    border-color 0.2s ease;
}
.nav-item svg {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}
.nav-item span {
  flex: 1;
}
.nav-item:hover {
  background: rgba(59, 130, 246, 0.18);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateX(4px);
  color: #f8fafc;
}
.nav-item.is-active {
  background: linear-gradient(120deg, rgba(34, 197, 94, 0.25), rgba(59, 130, 246, 0.35));
  border-color: rgba(96, 165, 250, 0.5);
  color: #f8fafc;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.45);
}

/* ===== Main / Header ===== */
.main-content {
  grid-column: 2 / 3;
  background: transparent;
}
.main-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 1rem 1.75rem;
  background:
    radial-gradient(circle at 5% 10%, rgba(59, 130, 246, 0.25), transparent 55%),
    rgba(10, 18, 35, 0.92);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 10;
  margin-bottom: 20px;
}
.header-titles {
  margin-right: auto;
}
.section-title {
  margin: 0 0 4px 0;
  color: var(--text-strong);
  font-size: 1.45rem;
  font-weight: 800;
  letter-spacing: -0.01em;
}
.section-subtitle {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.95rem;
}

/* Burger */
.burger {
  display: none;
  background: transparent;
  border: none;
  padding: 8px;
  margin: -4px 4px -4px -4px;
  cursor: pointer;
  border-radius: 10px;
}
.burger:hover {
  background: rgba(0, 0, 0, 0.05);
}
.burger span {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--text-base);
  margin: 4px 0;
  border-radius: 2px;
}

/* Header actions */
.header-actions-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.user-info-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 14px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 999px;
}
.user-name-header {
  font-weight: 700;
  color: var(--text-base);
  font-size: 0.92rem;
}
.role-tag-header {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  color: #fff;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(148, 163, 184, 0.18);
}
.logout-button-header {
  background: none;
  border: none;
  color: #f87171;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
}
.logout-button-header:hover {
  color: #fca5a5;
  background: rgba(248, 113, 113, 0.1);
  transform: scale(1.05);
}

/* Tags rol */
.role-tag-header.admin {
  background: linear-gradient(135deg, #facc15, #fbbf24);
  color: #0f172a;
  border-color: rgba(250, 204, 21, 0.6);
  box-shadow: 0 8px 20px rgba(250, 204, 21, 0.25);
}
.role-tag-header.supervisor {
  background: #14b8a6;
}
.role-tag-header.mecanico {
  background: #22c55e;
}
.role-tag-header.porteria {
  background: #ff6700;
}
.role-tag-header.guardia {
  background: #ff6700;
}
.role-tag-header.chofer {
  background: #3b82f6;
}
.role-tag-header.analista {
  background: #00bcd4;
}

/* ===== Lienzo de cada página ===== */
.content-body-reworked {
  padding: 2rem 0;
  background: transparent;
  min-height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* ===== SKELETON LOADER DE PÁGINA ===== */
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
.page-loading-skeleton {
  animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 25px;
  padding: 1.75rem;
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
}
.skeleton-card {
  background: rgba(148, 163, 184, 0.25); /* Un poco más oscuro que el fondo */
  border-radius: 12px;
}
.skeleton-info {
  height: 200px;
}
.skeleton-desc {
  height: 150px;
}
.skeleton-box {
  height: 120px;
}
/* Estilos genéricos para esqueletos de otras páginas */
.page-loading-skeleton:not(.ot-content-layout) {
  grid-template-columns: 1fr;
}
.page-loading-skeleton:not(.ot-content-layout) .skeleton-box {
  display: none;
}
.page-loading-skeleton:not(.ot-content-layout) .skeleton-desc {
  height: 300px;
}
.page-loading-skeleton:not(.ot-content-layout) .skeleton-info {
  height: 100px;
}

/* ... (resto de estilos sin cambios: .card, .backdrop, @media, modal) ... */
.page-surface {
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.02), rgba(6, 13, 28, 0.85)),
    var(--surface-highlight);
  border: 1px solid var(--card-border);
  border-radius: var(--radius);
  box-shadow: var(--card-shadow);
  padding: 2rem;
  color: var(--text-base);
}
.page-surface :where(h1, h2, h3, h4, h5, h6) {
  color: var(--text-strong);
}
.page-surface :where(p, label, span, li) {
  color: var(--text-base);
}
.page-surface .muted,
.page-surface .muted-text {
  color: var(--text-muted);
}
.card {
  background:
    linear-gradient(160deg, rgba(255, 255, 255, 0.015), rgba(6, 12, 26, 0.85)), var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 16px;
  box-shadow: var(--card-shadow);
  color: var(--text-base);
}
.card :where(h1, h2, h3, h4, h5, h6) {
  color: var(--text-strong);
}
.card :where(p, label, span, li) {
  color: var(--text-base);
}

table {
  color: var(--text-base);
  border-color: rgba(148, 163, 184, 0.18);
}
th {
  color: var(--text-muted);
  background: rgba(148, 163, 184, 0.08);
}
td {
  border-color: rgba(148, 163, 184, 0.12);
}

input,
select,
textarea {
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text-base);
  border-radius: 10px;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}
input::placeholder,
textarea::placeholder {
  color: var(--input-placeholder);
}
input:focus,
select:focus,
textarea:focus {
  outline: none;
  border-color: var(--input-focus);
  box-shadow: 0 0 0 3px rgba(94, 155, 255, 0.2);
}
input:disabled,
select:disabled,
textarea:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.65);
  backdrop-filter: saturate(120%) blur(4px);
  z-index: 19;
  display: none;
}
@media (max-width: 1024px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
    padding: 12px;
  }
  .main-content {
    grid-column: 1 / -1;
  }
  .content-body-reworked {
    padding: 1.25rem;
    min-height: auto;
  }
  .section-title {
    font-size: 1.25rem;
  }
  .section-subtitle {
    display: none;
  }
  .burger {
    display: inline-block;
  }
  .sidebar,
  .sidebar-skeleton {
    position: fixed;
    left: 12px;
    top: 12px;
    bottom: 12px;
    width: min(84vw, 300px);
    transform: translateX(-120%);
    transition: transform 0.22s ease;
    z-index: 20;
    min-height: auto;
  }
  .sidebar.open {
    transform: translateX(0);
  }
  .backdrop {
    display: block;
  }
  .page-loading-skeleton {
    grid-template-columns: 1fr;
  }
}

.confirm-modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(3, 6, 18, 0.8);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.confirm-modal-content {
  background: rgba(15, 23, 42, 0.95);
  padding: 2.5rem;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  width: 90%;
  max-width: 400px;
  text-align: center;
}
.modal-icon-container {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(248, 113, 113, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  border: 4px solid rgba(248, 113, 113, 0.4);
}
.modal-icon {
  color: #f87171;
  width: 32px;
  height: 32px;
}
.confirm-modal-content h3 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-strong);
  margin: 0 0 0.5rem;
}
.confirm-modal-content p {
  font-size: 1rem;
  color: var(--text-muted);
  margin-bottom: 2rem;
}
.modal-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.modal-btn-cancel,
.modal-btn-confirm {
  padding: 12px 20px;
  font-size: 0.95rem;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.modal-btn-cancel {
  background: rgba(148, 163, 184, 0.1);
  color: var(--text-base);
  border: 1px solid rgba(148, 163, 184, 0.25);
}
.modal-btn-cancel:hover {
  background: rgba(148, 163, 184, 0.2);
}
.modal-btn-confirm {
  background: #f87171;
  color: #fff;
}
.modal-btn-confirm:hover {
  background: #b91c1c;
}
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-active .confirm-modal-content,
.modal-fade-leave-active .confirm-modal-content {
  transition: all 0.3s ease-out;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .confirm-modal-content,
.modal-fade-leave-to .confirm-modal-content {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}
</style>
