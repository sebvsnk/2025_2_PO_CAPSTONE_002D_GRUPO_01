<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

// Estado
const router = useRouter()
const authStore = useAuthStore()
const users = ref([])
const filteredUsers = ref([])
const filterText = ref('')
const filterRole = ref('TODOS')
const currentPage = ref(1)
const pageSize = 10
const isLoading = ref(true)
const errorMsg = ref(null)

const API_BASE_URL = import.meta.env.VITE_API_URL

// FunciÃ³n para obtener la lista de usuarios
const fetchUsers = async () => {
  isLoading.value = true
  errorMsg.value = null
  try {
    const response = await fetch(`${API_BASE_URL}/admin/usuarios/`, {
      headers: {
        Authorization: `Bearer ${authStore.token}`,
      },
    })

    if (response.status === 403) {
      errorMsg.value = 'Acceso denegado. Se requieren permisos de Administrador.'
      router.push({ name: 'Dashboard' })
      return
    }

    if (!response.ok) {
      throw new Error(`Error al cargar usuarios: ${response.statusText}`)
    }

    const data = await response.json()
    users.value = data
    filteredUsers.value = data
  } catch (error) {
    console.error('API Error:', error)
    errorMsg.value = `No se pudo conectar con el servicio de usuarios. ${error.message}`
  } finally {
    isLoading.value = false
  }
}

const applyFilters = () => {
  const text = filterText.value.trim().toLowerCase()
  const role = filterRole.value
  filteredUsers.value = users.value.filter((u) => {
    const matchesRole = role === 'TODOS' || (u.rol || '').toLowerCase() === role.toLowerCase()
    const matchesText =
      !text ||
      (u.nombre || '').toLowerCase().includes(text) ||
      (u.email || '').toLowerCase().includes(text) ||
      (u.rut || '').toLowerCase().includes(text) ||
      String(u.numero_telefonico || '')
        .toLowerCase()
        .includes(text) ||
      String(u.id || '').includes(text)
    return matchesRole && matchesText
  })
  currentPage.value = 1
}

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredUsers.value.slice(start, start + pageSize)
})
const totalPages = computed(() =>
  Math.max(1, Math.ceil((filteredUsers.value.length || 0) / pageSize)),
)
// Cargar usuarios al montar el componente
onMounted(() => {
  if (authStore.isAuthenticated) {
    fetchUsers()
  } else {
    router.push({ name: 'Login' })
  }
})

// NavegaciÃ³n al formulario de creaciÃ³n
const navigateToCreateUser = () => {
  router.push({ name: 'AdminUserCreate' })
}

// NavegaciÃ³n a la vista de detalle/ediciÃ³n
const viewUserDetail = (userId) => {
  router.push({ name: 'AdminUserDetail', params: { id: userId } })
}
</script>

<template>
  <section class="admin-users-wrapper">
    <div class="hero-header">
      <div class="hero-copy">
        <p class="eyebrow">Equipo</p>
        <h1>Gestión de Usuarios</h1>
        <p>Crear, editar o desactivar perfiles de la plataforma.</p>
        <p v-if="!isLoading" class="hero-meta">Mostrando {{ users.length }} perfiles de usuario.</p>
      </div>
      <button class="accent-button" @click="navigateToCreateUser">+ Crear Usuario</button>
    </div>

    <div v-if="isLoading" class="state-card loading-card">
      <span class="spinner" aria-hidden="true"></span>
      <p>Cargando perfiles de usuario...</p>
    </div>

    <div v-else-if="errorMsg" class="state-card error-card">
      {{ errorMsg }}
    </div>

    <div v-else class="users-card">
      <div class="filters-bar">
        <div class="filter-input">
          <input
            v-model="filterText"
            type="text"
            placeholder="Buscar por nombre, correo, RUT o número"
            @input="applyFilters"
          />
        </div>
        <div class="filter-select">
          <select v-model="filterRole" @change="applyFilters">
            <option value="TODOS">Todos los roles</option>
            <option value="ADMIN">Admin</option>
            <option value="SUPERVISOR">Supervisor</option>
            <option value="MECANICO">Mecánico</option>
            <option value="PORTERIA">Portería</option>
            <option value="GUARDIA">Guardia</option>
            <option value="ANALISTA">Analista</option>
            <option value="CHOFER">Chofer</option>
          </select>
        </div>
      </div>

      <div class="table-head">
        <span>Nombre</span>
        <span>Rol</span>
        <span>RUT</span>
        <span>Email</span>
        <span>Teléfono</span>
        <span>Acción</span>
      </div>
      <div class="users-scroll aurora-scroll">
        <Transition name="list-fade" mode="out-in">
          <div :key="currentPage" class="list-page-container">
            <div
              v-for="user in paginatedUsers"
              :key="user.id"
              class="user-row-card"
              @click="viewUserDetail(user.id)"
            >
              <div class="cell name">
                <div class="avatar-circle" :class="user.rol ? user.rol.toLowerCase() : 'default'">
                  {{ user.nombre?.charAt(0) || 'U' }}
                </div>
                <div>
                  <p class="user-name">{{ user.nombre }}</p>
                  <p class="user-email">{{ user.email }}</p>
                </div>
              </div>
              <div class="cell">
                <span :class="['role-tag', user.rol ? user.rol.toLowerCase() : 'default']">
                  {{ user.rol || 'N/A' }}
                </span>
              </div>
              <div class="cell muted">{{ user.rut || 'N/A' }}</div>
              <div class="cell muted hide-mobile">{{ user.email }}</div>
              <div class="cell muted">{{ user.numero_telefonico || 'N/A' }}</div>
              <div class="cell action">
                <button class="ghost-button" @click.stop="viewUserDetail(user.id)">Editar</button>
              </div>
            </div>

            <div v-if="paginatedUsers.length === 0" class="empty-search">
              <p>No se encontraron usuarios en esta página.</p>
            </div>
          </div>
        </Transition>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
          Anterior
        </button>
        <span>Página {{ currentPage }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
          Siguiente
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.admin-users-wrapper {
  min-height: calc(100vh - 140px);
  padding: 18px 18px 80px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 28px 32px;
  border-radius: 28px;
  background: linear-gradient(150deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.8));
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.6);
}
.hero-copy {
  flex: 1;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.85);
  margin: 0 0 6px;
}
.hero-header h1 {
  margin: 0;
  font-size: 1.9rem;
  color: #f8fafc;
}
.hero-header p {
  margin: 6px 0 0;
  color: rgba(148, 163, 184, 0.92);
}
.hero-meta {
  font-size: 0.9rem;
}

.accent-button {
  align-self: flex-start;
  border: none;
  border-radius: 18px;
  padding: 12px 22px;
  font-weight: 700;
  letter-spacing: 0.03em;
  background: linear-gradient(120deg, #34d399, #0ea5e9);
  color: #0f172a;
  cursor: pointer;
  box-shadow: 0 18px 40px rgba(14, 165, 233, 0.35);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.accent-button:hover {
  transform: translateY(-2px) scale(1.01);
}

.state-card {
  border-radius: 24px;
  padding: 40px;
  text-align: center;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.8);
}
.loading-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  color: #f8fafc;
}
.loading-card .spinner {
  position: relative;
  display: inline-block;
  box-sizing: border-box;
  width: 66px;
  height: 66px;
  margin-bottom: 4px;
  border-radius: 50%;
  border: 4px solid transparent;
  border-top-color: #22d3ee;
  border-right-color: rgba(59, 130, 246, 0.55);
  border-left-color: rgba(59, 130, 246, 0.18);
  border-bottom-color: rgba(34, 211, 238, 0.12);
  animation:
    aurora-spin 0.9s linear infinite,
    pulseGlow 2s ease-in-out infinite;
  box-shadow:
    0 0 18px rgba(34, 211, 238, 0.35),
    0 0 32px rgba(59, 130, 246, 0.22);
}
.loading-card .spinner::after {
  content: '';
  position: absolute;
  inset: 14px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.24), rgba(255, 255, 255, 0));
  filter: blur(2px);
}
.error-card {
  color: #fecaca;
  border-color: rgba(248, 113, 113, 0.35);
  background: rgba(248, 113, 113, 0.18);
}

.users-card {
  border-radius: 28px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.72);
  box-shadow: 0 25px 60px rgba(2, 6, 23, 0.55);
  overflow: hidden;
}
.filters-bar {
  display: flex;
  gap: 12px;
  padding: 14px 16px;
  align-items: center;
  flex-wrap: wrap;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(8, 13, 24, 0.5);
}
.filters-bar input,
.filters-bar select {
  background: rgba(9, 15, 28, 0.9);
  border: 1px solid rgba(120, 172, 255, 0.25);
  color: #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 180px;
  outline: none;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}
.filters-bar input:focus,
.filters-bar select:focus {
  border-color: #22d3ee;
  box-shadow: 0 0 0 3px rgba(34, 211, 238, 0.18);
}
.table-head,
.user-row-card {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 2fr 1fr 1fr;
  gap: 12px;
  padding: 18px 24px;
  align-items: center;
}
.table-head {
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.9);
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
}
.user-row-card {
  cursor: pointer;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
  transition:
    background 0.2s ease,
    transform 0.2s ease;
}
.user-row-card:hover {
  background: rgba(30, 41, 59, 0.6);
  transform: translateY(-1px);
}

/* --- SCROLL AURORA --- */

/* 1. El contenedor DEBE tener límite de altura */
.users-scroll {
  max-height: 450px; /* <--- AJUSTA ESTO: Si es muy alto, no habrá scroll. Prueba 400px o 50vh */
  overflow-y: auto; /* Esto activa el scroll vertical */
  overflow-x: hidden;
  padding-right: 8px; /* Espacio para que el texto no choque con la barra */
  margin-right: 2px;
}

/* 2. Estilo de la barra (Track/Fondo) */
.aurora-scroll::-webkit-scrollbar {
  width: 8px; /* Grosor de la barra */
}
.aurora-scroll::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.4); /* Fondo oscuro translúcido */
  border-radius: 4px;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

/* 3. Estilo del indicador (Thumb/Dedo) */
.aurora-scroll::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #22d3ee, #3b82f6, #8b5cf6); /* Gradiente Neón */
  border-radius: 10px;
  border: 2px solid rgba(15, 23, 42, 0.9); /* Borde para dar efecto flotante */
}
.aurora-scroll::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(
    180deg,
    #67e8f9,
    #60a5fa,
    #a78bfa
  ); /* Más brillante al pasar el mouse */
}

.cell {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #f8fafc;
}
.cell.name {
  gap: 14px;
}
.cell.muted {
  color: rgba(148, 163, 184, 0.85);
}
.cell.action {
  justify-content: flex-end;
}
.user-name {
  margin: 0;
  font-weight: 600;
}
.user-email {
  margin: 2px 0 0;
  font-size: 0.85rem;
  color: rgba(148, 163, 184, 0.85);
}
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 14px 16px 18px;
}
.page-btn {
  border: 1px solid rgba(120, 172, 255, 0.35);
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.18), rgba(34, 211, 238, 0.18));
  color: #dbeafe;
  padding: 8px 12px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 700;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(34, 211, 238, 0.25);
}

.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #0f172a;
}
.role-tag {
  padding: 4px 12px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.8rem;
  letter-spacing: 0.04em;
}
.ghost-button {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: transparent;
  color: #e2e8f0;
  padding: 6px 14px;
  font-weight: 600;
}
.ghost-button:hover {
  border-color: rgba(59, 130, 246, 0.5);
}

.role-tag.admin,
.avatar-circle.admin {
  background: #facc15;
  color: #0f172a;
}
.role-tag.supervisor,
.avatar-circle.supervisor {
  background: #14b8a6;
  color: #fff;
}
.role-tag.mecanico,
.avatar-circle.mecanico {
  background: #22c55e;
  color: #fff;
}
.role-tag.porteria,
.avatar-circle.porteria,
.role-tag.guardia,
.avatar-circle.guardia {
  background: #fb923c;
  color: #fff;
}
.role-tag.chofer,
.avatar-circle.chofer {
  background: #3b82f6;
  color: #fff;
}
.role-tag.analista,
.avatar-circle.analista {
  background: #0ea5e9;
  color: #fff;
}
.role-tag.default,
.avatar-circle.default {
  background: rgba(148, 163, 184, 0.5);
  color: #0f172a;
}

/* ... tus estilos existentes ... */

/* Estilo para el contenedor interno que añadimos para la transición */
.list-page-container {
  display: flex;
  flex-direction: column;
  gap: 0; /* El gap ya lo maneja el border-bottom de las tarjetas */
}

/* --- ANIMACIÓN DE TRANSICIÓN DE LISTA --- */
.list-fade-enter-active,
.list-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.list-fade-enter-from {
  opacity: 0;
  transform: translateY(10px); /* Entra desde abajo un poquito */
}

.list-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px); /* Sale hacia arriba */
}

.empty-search {
  padding: 40px;
  text-align: center;
  color: rgba(148, 163, 184, 0.7);
  font-style: italic;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes aurora-spin {
  to {
    transform: rotate(360deg);
  }
}
@keyframes pulseGlow {
  0% {
    box-shadow:
      0 0 18px rgba(34, 211, 238, 0.35),
      0 0 32px rgba(59, 130, 246, 0.22);
    opacity: 0.95;
  }
  50% {
    box-shadow:
      0 0 24px rgba(34, 211, 238, 0.5),
      0 0 40px rgba(59, 130, 246, 0.3);
    opacity: 1;
  }
  100% {
    box-shadow:
      0 0 18px rgba(34, 211, 238, 0.35),
      0 0 32px rgba(59, 130, 246, 0.22);
    opacity: 0.95;
  }
}

@media (max-width: 900px) {
  .table-head,
  .user-row-card {
    grid-template-columns: 1.5fr 1fr 1fr 1fr;
  }
  .hide-mobile {
    display: none;
  }
}
@media (max-width: 640px) {
  .hero-header {
    flex-direction: column;
  }
  .accent-button {
    width: 100%;
    text-align: center;
  }
  .users-card {
    border-radius: 20px;
  }
  .table-head {
    display: none;
  }
  .user-row-card {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  .cell {
    justify-content: space-between;
  }
  .cell.action {
    justify-content: flex-start;
  }
}
</style>
