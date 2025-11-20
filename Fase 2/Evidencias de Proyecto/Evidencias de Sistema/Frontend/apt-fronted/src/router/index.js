// apt-fronted/src/router/index.js (Corregido para Aterrizar en HomeView)
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Importaciones de Vistas
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import MiPerfilView from '@/views/MiPerfilView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import AdminUserCreateView from '@/views/AdminUserCreateView.vue'
import AdminUserDetailView from '@/views/AdminUserDetailView.vue'
import ReportsView from '@/views/ReportsView.vue'
import AuditLogView from '@/views/AuditLogView.vue'
import SupervisorView from '@/views/SupervisorView.vue'
import OtCreateView from '@/views/OtCreateView.vue'
import OtDetailView from '@/views/OtDetailView.vue'
import TaskListView from '@/views/TaskListView.vue'
import TaskDetailView from '@/views/TaskDetailView.vue'
import CheckInView from '@/views/CheckInView.vue'
import MechanicTasksView from '@/views/MechanicTasksView.vue'
import VehicleCreateView from '@/views/VehicleCreateView.vue'
import VehicleListView from '@/views/VehicleListView.vue'
import VehicleEditView from '@/views/VehicleEditView.vue' // &lt;--- Importar
import TaskEvidenceView from '@/views/TaskEvidenceView.vue'
import TaskRepuestosView from '@/views/TaskRepuestosView.vue'
import OtHistorialView from '@/views/OtHistorialView.vue'
import OtExportView from '@/views/OtExportView.vue'
import PublicStatusView from '@/views/PublicStatusView.vue'
import AuthCallback from '@/views/AuthCallback.vue'
import VehicleStatusView from '@/views/VehicleStatusView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: HomeView, // Esta es la vista de "Acceso Rápido"
      meta: { requiresAuth: true, title: 'Acceso Rápido' },
    },
    {
      path: '/login',
      name: 'Login',
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: ForgotPasswordView,
      meta: { requiresAuth: false },
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: ResetPasswordView,
      meta: { requiresAuth: false },
    },
    {
      path: '/auth/callback',
      name: 'AuthCallback',
      component: AuthCallback,
      meta: { requiresAuth: false },
    },
    {
      path: '/mi-perfil',
      name: 'MiPerfil',
      component: MiPerfilView,
      meta: {
        requiresAuth: true,
        title: 'Mi Perfil de Usuario',
        subtitle: 'Revisa tu información personal y de contacto.',
      },
    },
    {
      path: '/admin/usuarios',
      name: 'AdminUsers',
      component: AdminUsersView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN'], // <-- Solo Admin entra aquí
        title: 'Gestión de Usuarios',
        subtitle: 'Crear, editar o desactivar perfiles de usuario.',
      },
    },
    {
      path: '/admin/usuarios/crear',
      name: 'AdminUserCreate',
      component: AdminUserCreateView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN'],
        title: 'Crear Usuario',
        subtitle: 'Invitar un nuevo usuario a la plataforma.',
      },
    },
    {
      path: '/admin/usuarios/:id',
      name: 'AdminUserDetail',
      component: AdminUserDetailView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN'],
        title: 'Editar Usuario',
        subtitle: 'Modificar el perfil y rol de un usuario existente.',
      },
    },
    {
      path: '/reportes',
      name: 'ReportsView',
      component: ReportsView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'ANALISTA'],
        title: 'Reportes y Métricas',
        subtitle: 'Indicadores de productividad, tiempos y eficiencia.',
      },
    },
    {
      path: '/auditoria',
      name: 'AuditLogView',
      component: AuditLogView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'ANALISTA'],
        title: 'Registro de Auditoría',
        subtitle: 'Trazabilidad de acciones y cambios de estado.',
      },
    },
    {
      path: '/supervisor',
      name: 'SupervisorDashboard',
      component: SupervisorView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR'],
        title: 'Tablero de Órdenes',
        subtitle: 'Monitoreo de OTs en tiempo real y gestión.',
      },
    },
    {
      path: '/ot/crear',
      name: 'OtCreate',
      component: OtCreateView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR'],
        title: 'Crear OT',
        subtitle: 'Abrir una nueva Orden de Trabajo para un vehículo.',
      },
    },
    {
      path: '/vehiculos',
      name: 'VehicleList',
      component: VehicleListView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR'],
        title: 'Flota de Vehículos',
        subtitle: 'Listado completo y gestión de flota.',
      },
    },
    {
      path: '/vehiculo/ingresar',
      name: 'VehicleCreate',
      component: VehicleCreateView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR'],
        title: 'Ingresar Vehículo',
        subtitle: 'Registrar un nuevo vehículo y su chofer asociado.',
      },
    },
    {
      path: '/vehiculo/:id/editar',
      name: 'VehicleEdit',
      component: VehicleEditView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR'], // Solo ellos pueden cambiar patentes
        title: 'Editar Vehículo',
        subtitle: 'Modificar datos y revisar historial de patentes.',
      },
    },
    {
      path: '/ot/:id',
      name: 'OtDetail',
      component: OtDetailView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'MECANICO', 'ANALISTA'],
        title: 'Detalle de Orden de Trabajo',
        subtitle: 'Gestiona tareas, evidencia y estado de la OT.',
      },
    },
    {
      path: '/ot/:otId/tareas',
      name: 'TaskList',
      component: TaskListView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'MECANICO'],
        title: 'Gestión de Tareas',
        subtitle: 'Asigna y revisa las tareas de una OT.',
      },
    },
    {
      path: '/tarea/:taskId',
      name: 'TaskDetail',
      component: TaskDetailView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'MECANICO', 'ANALISTA'],
        title: 'Detalle de Tarea',
        subtitle: 'Ejecuta el ciclo de vida y documenta la tarea.',
      },
    },
    {
      path: '/tarea/:taskId/evidencia',
      name: 'TaskEvidence',
      component: TaskEvidenceView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'MECANICO'],
        title: 'Evidencia de Tarea',
        subtitle: 'Adjunta fotos o documentos a la tarea.',
      },
    },
    {
      path: '/tarea/:taskId/repuestos',
      name: 'TaskRepuestos',
      component: TaskRepuestosView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'MECANICO'],
        title: 'Repuestos de Tarea',
        subtitle: 'Asigna repuestos del catálogo a la tarea.',
      },
    },
    {
      path: '/ot/historial',
      name: 'OtHistorial',
      component: OtHistorialView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'ANALISTA'],
        title: 'Historial de OTs',
        subtitle: 'Consulta de órdenes cerradas y anuladas.',
      },
    },
    {
      path: '/ot/:otId/exportar',
      name: 'OtExport',
      component: OtExportView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['ADMIN', 'SUPERVISOR', 'ANALISTA'],
        title: 'Exportar Reporte de OT',
        subtitle: 'Genera un documento PDF/imprimible de la OT.',
      },
    },
    {
      path: '/mis-tareas',
      name: 'MechanicTasks',
      component: MechanicTasksView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['MECANICO', 'SUPERVISOR'], // Supervisor también puede ver sus tareas
        title: 'Mis Tareas Pendientes',
        subtitle: 'Revisa las tareas asignadas a tu nombre.',
      },
    },
    {
      path: '/porteria/check-in',
      name: 'CheckInView',
      component: CheckInView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['PORTERIA', 'GUARDIA', 'ADMIN'],
        title: 'Bitácora de Portería',
        subtitle: 'Registrar entradas y salidas de vehículos.',
      },
    },
    {
      path: '/status',
      name: 'PublicStatus',
      component: PublicStatusView,
      meta: { requiresAuth: false },
    },
    // 2. Agregar la definición de la ruta en el array 'routes'
    {
      path: '/mi-vehiculo',
      name: 'VehicleStatus', // <--- Este nombre debe coincidir con el del HomeView
      component: VehicleStatusView,
      meta: {
        requiresAuth: true,
        requiredRoles: ['CHOFER'], // Solo choferes pueden entrar
        title: 'Estado de mi Vehículo',
        subtitle: 'Revisa el avance de la mantención en curso.',
      },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // --- 🌟 INICIO DE LA CORRECCIÓN 🌟 ---
  // Revisa el hash de la URL ANTES de hacer cualquier otra cosa.
  const isPasswordRecovery = window.location.hash.includes('type=recovery')
  const isInvite = window.location.hash.includes('type=invite')

  if ((isPasswordRecovery || isInvite) && to.name !== 'ResetPassword') {
    // Si es un enlace de recuperación Y AÚN NO VAMOS a ResetPassword:

    // 1. Forzamos el "logout visual" para que no se vea el dashboard.
    authStore.token = null
    authStore.user = null
    authStore.loadingMessage = 'Redireccionando a crear contraseña...'
    authStore.isLoadingUser = true

    // 2. Redirigimos a la página de ResetPassword.
    //    Esto activará la animación "Verificando enlace..." a pantalla completa.
    return next({ name: 'ResetPassword' })
  }
  // --- 🌟 FIN DE LA CORRECCIÓN 🌟 ---

  // Si estamos en la ruta de callback de Supabase (AuthCallback.vue),
  // no hacemos NADA. (Tu lógica de AuthCallback.vue se encargará).
  if (to.name === 'AuthCallback') {
    return next()
  }

  // 1. ESPERAR A LA INICIALIZACIÓN (Tu lógica existente)
  await authStore.initializeStore()

  // 2. OBTENER VALORES (Tu lógica existente)
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.userRole
  const routeRequiresAuth = to.meta.requiresAuth
  const requiredRoles = to.meta.requiredRoles || []

  // 3. LÓGICA PARA USUARIO AUTENTICADO (Tu lógica existente)
  if (isAuthenticated) {
    if (to.name === 'Login') {
      return next({ name: 'Dashboard' })
    }
    if (requiredRoles.length > 0) {
      if (requiredRoles.includes(userRole)) {
        return next() // Tiene el rol
      } else {
        return next({ name: 'Dashboard' }) // No tiene el rol
      }
    }
    return next() // Ruta sin roles
  } else {
    // 4. LÓGICA PARA USUARIO NO AUTENTICADO (Tu lógica existente)
    if (routeRequiresAuth) {
      return next({
        name: 'Login',
        query: { redirect: to.fullPath },
      })
    }
    return next() // Ruta pública
  }
})

export default router
