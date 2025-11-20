<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const router = useRouter()
const authStore = useAuthStore()

// --- Logica de roles: solo controla la visibilidad de las tarjetas ---
const is_admin = computed(() => authStore.userRole === 'ADMIN')
const is_supervisor = computed(() => authStore.userRole === 'SUPERVISOR')
const is_mecanico = computed(() => authStore.userRole === 'MECANICO')
const is_porteria = computed(() => authStore.userRole === 'PORTERIA')
const is_guardia = computed(() => authStore.userRole === 'GUARDIA')
const is_chofer = computed(() => authStore.userRole === 'CHOFER')
const is_analista = computed(() => authStore.userRole === 'ANALISTA')

// --- Navegacion simple para las tarjetas ---
const navigateTo = (name) => {
  router.push({ name })
}
</script>

<template>
  <section class="home-dashboard-panel page-surface">
    <header class="home-dashboard-header">
      <div class="home-dashboard-title">
        <p class="home-dashboard-eyebrow">Panel principal</p>
        <h2>Accesos directos segun tu rol</h2>
      </div>
      <p class="home-dashboard-helper">
        Selecciona una tarjeta para abrir el modulo correspondiente. Solo ves lo habilitado para tu
        perfil.
      </p>
    </header>

    <div class="grid-links">
      <article v-if="is_admin" class="link-card admin-link" @click="navigateTo('AdminUsers')">
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <circle cx="12" cy="8.2" r="4" />
            <path d="M5 20c0-3.3 3.1-6 7-6s7 2.7 7 6" />
          </svg>
        </span>
        <h3>Gestion de usuarios</h3>
        <p>Crear, editar o desactivar cuentas de la plataforma (RF-ADM-01/02/03).</p>
      </article>

      <article
        v-if="is_admin || is_supervisor || is_analista"
        class="link-card analyst-link"
        @click="navigateTo('ReportsView')"
      >
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <polyline points="4 16 9 11 13 15 20 8" />
            <polyline points="4 10 4 16 10 16" />
          </svg>
        </span>
        <h3>Reportes y metricas</h3>
        <p>Indicadores de productividad, tiempos y eficiencia (RF-REP-01/02/03).</p>
      </article>

      <article
        v-if="is_admin || is_analista"
        class="link-card audit-link"
        @click="navigateTo('AuditLogView')"
      >
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M12 3 5 6v5c0 4.2 2.9 8.2 7 9 4.1-.8 7-4.8 7-9V6l-7-3z" />
            <path d="m9.5 12 1.8 2 3.2-4" />
          </svg>
        </span>
        <h3>Auditoria de sistema</h3>
        <p>Trazabilidad de acciones y cambios de estado (RF-AUD-03).</p>
      </article>

      <article
        v-if="is_admin || is_supervisor"
        class="link-card supervisor-link"
        @click="navigateTo('SupervisorDashboard')"
      >
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M9 3h6l1 2h4v15H4V5h4z" />
            <path d="M9 8h6" />
            <path d="M9 12h6" />
            <path d="M9 16h3" />
          </svg>
        </span>
        <h3>Tablero de ordenes</h3>
        <p>Monitoreo de OTs en tiempo real y gestion (RF-TAB-01, RF-OT-01).</p>
      </article>

      <article
        v-if="is_porteria || is_guardia"
        class="link-card porteria-link"
        @click="navigateTo('CheckInView')"
      >
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M5 21V7l7-4 7 4v14" />
            <path d="M5 10h14" />
            <path d="M12 10v11" />
          </svg>
        </span>
        <h3>Bitacora de porteria</h3>
        <p>Registrar ingreso y salida de vehiculos (RF-ING-01, RF-BIT-01/02/03).</p>
      </article>

      <article
        v-if="is_mecanico || is_supervisor"
        class="link-card mecanico-link"
        @click="navigateTo('MechanicTasks')"
      >
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="m6 19 3-3" />
            <path d="m10 7 4-4 4 4-4 4" />
            <path d="m13 9 2 2" />
            <path d="M5.5 21a2.5 2.5 0 1 1 3.5-3.5" />
          </svg>
        </span>
        <h3>Mis tareas</h3>
        <p>Ver, iniciar, pausar y cerrar tareas asignadas (RF-TAR-02/03/05).</p>
      </article>

      <article v-if="is_chofer" class="link-card chofer-link" @click="navigateTo('VehicleStatus')">
        <span class="icon-badge" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path d="M3 16V8h11l4 5v3" />
            <path d="M7 16v2" />
            <path d="M17 16v2" />
            <circle cx="7" cy="19" r="2" />
            <circle cx="17" cy="19" r="2" />
            <path d="M3 13h14" />
          </svg>
        </span>
        <h3>Estado del vehiculo</h3>
        <p>Seguimiento de la mantencion en curso de tu vehiculo.</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.home-dashboard-panel {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
.home-dashboard-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.home-dashboard-title h2 {
  margin: 0;
  font-size: 1.85rem;
  color: var(--text-strong);
  letter-spacing: -0.01em;
}
.home-dashboard-eyebrow {
  margin: 0;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  color: var(--text-muted);
}
.home-dashboard-helper {
  margin: 0;
  color: var(--text-muted);
  max-width: 520px;
}

@media (min-width: 768px) {
  .home-dashboard-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
  .home-dashboard-helper {
    text-align: right;
  }
}

.grid-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 25px;
  width: 100%;
}

.link-card {
  background: linear-gradient(155deg, rgba(255, 255, 255, 0.02), rgba(6, 13, 26, 0.85)),
    var(--surface-card);
  border-radius: 18px;
  padding: 30px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border 0.3s ease;
  cursor: pointer;
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: var(--text-base);
}

.link-card:hover {
  transform: translateY(-5px) scale(1.01);
  box-shadow: 0 30px 60px rgba(2, 6, 23, 0.55);
  border-color: rgba(94, 155, 255, 0.45);
}

.link-card h3 {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-strong);
  margin-top: 15px;
  margin-bottom: 8px;
}

.link-card p {
  font-size: 0.95rem;
  color: var(--text-muted);
  margin: 0;
}

.icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-strong);
}
.icon-badge svg {
  width: 26px;
  height: 26px;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

/* Colores por rol */
.admin-link {
  border-color: rgba(250, 204, 21, 0.35);
  box-shadow: 0 20px 40px rgba(250, 204, 21, 0.12);
}
.admin-link .icon-badge {
  background: rgba(250, 204, 21, 0.15);
  color: #facc15;
}
.supervisor-link {
  border-color: rgba(45, 212, 191, 0.4);
  box-shadow: 0 20px 40px rgba(45, 212, 191, 0.15);
}
.supervisor-link .icon-badge {
  background: rgba(45, 212, 191, 0.15);
  color: #5eead4;
}
.mecanico-link {
  border-color: rgba(74, 222, 128, 0.35);
  box-shadow: 0 20px 40px rgba(74, 222, 128, 0.15);
}
.mecanico-link .icon-badge {
  background: rgba(74, 222, 128, 0.15);
  color: #4ade80;
}
.porteria-link {
  border-color: rgba(251, 146, 60, 0.4);
  box-shadow: 0 20px 40px rgba(251, 146, 60, 0.15);
}
.porteria-link .icon-badge {
  background: rgba(251, 146, 60, 0.15);
  color: #fb923c;
}
.chofer-link {
  border-color: rgba(96, 165, 250, 0.4);
  box-shadow: 0 20px 40px rgba(96, 165, 250, 0.15);
}
.chofer-link .icon-badge {
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
}
.analyst-link,
.audit-link {
  border-color: rgba(94, 234, 212, 0.38);
  box-shadow: 0 20px 40px rgba(94, 234, 212, 0.15);
}
.analyst-link .icon-badge,
.audit-link .icon-badge {
  background: rgba(94, 234, 212, 0.15);
  color: #5eead4;
}

@media (max-width: 600px) {
  .link-card {
    padding: 22px;
  }
  .grid-links {
    grid-template-columns: 1fr;
  }
}
</style>
