<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// --- Usamos el 'user' del store (es reactivo) ---
const profile = computed(() => authStore.user)

// --- Lógica de Roles ---
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
    case 'CHOFER':
      return 'Chofer/Conductor'
    case 'ANALISTA':
      return 'Analista/Indicadores'
    default:
      return 'Usuario Registrado'
  }
}
</script>

<template>
  <section v-if="profile" class="profile-wrapper">
    <div class="profile-shell">
      <div class="profile-hero">
        <div class="hero-copy">
          <p class="eyebrow">Panel personal</p>
          <h1>Mi Perfil de Usuario</h1>
          <p>Revisa tu información personal, credenciales y datos de contacto.</p>
        </div>
        <div class="hero-meta">
          <span class="meta-label">Rol actual</span>
          <span class="meta-value">{{ getRoleTitle(profile.rol) }}</span>
        </div>
      </div>

      <div class="profile-card">
        <header class="profile-headline">
          <div :class="['profile-avatar', profile.rol?.toLowerCase()]">
            {{ profile.nombre?.charAt(0) || 'U' }}
          </div>
          <div class="headline-copy">
            <h2>{{ profile.nombre }}</h2>

            <p class="email email-break">{{ profile.email || 'Sin correo registrado' }}</p>

            <span :class="['role-pill', profile.rol?.toLowerCase()]">
              {{ getRoleTitle(profile.rol) }}
            </span>
          </div>
          <div class="quick-id">
            <p>ID interno</p>
            <span>#{{ profile.id || '--' }}</span>
          </div>
        </header>

        <div class="profile-sections">
          <section class="info-panel">
            <h3>Datos de Contacto</h3>
            <div class="data-grid">
              <article class="data-item full-width-mobile">
                <div class="icon-circle">
                  <svg viewBox="0 0 24 24" stroke="currentColor" fill="none">
                    <path
                      d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
                    />
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </div>
                <p class="label">Correo Electrónico</p>

                <p class="value email-break">{{ profile.email || 'No registrado' }}</p>
              </article>

              <article class="data-item">
                <div class="icon-circle">
                  <svg viewBox="0 0 24 24" stroke="currentColor" fill="none">
                    <path
                      d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
                    />
                  </svg>
                </div>
                <p class="label">Teléfono</p>
                <p class="value">{{ profile.numero_telefonico || 'No registrado' }}</p>
              </article>
            </div>
          </section>

          <section class="info-panel">
            <h3>Identificación</h3>
            <div class="data-grid">
              <article class="data-item">
                <div class="icon-circle">
                  <svg viewBox="0 0 24 24" stroke="currentColor" fill="none">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                </div>
                <p class="label">RUT</p>
                <p class="value">{{ profile.rut || 'No registrado' }}</p>
              </article>
              <article class="data-item">
                <div class="icon-circle">
                  <svg viewBox="0 0 24 24" stroke="currentColor" fill="none">
                    <path d="M21 10H7" />
                    <path d="M21 6H3" />
                    <path d="M21 14H3" />
                    <path d="M21 18H7" />
                  </svg>
                </div>
                <p class="label">ID Interno (Sistema)</p>
                <p class="value">#{{ profile.id || '--' }}</p>
              </article>
            </div>
          </section>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
/* ESTILOS ORIGINALES (MANTENIDOS) */

.profile-wrapper {
  min-height: auto;
  padding: 8px 16px 40px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  max-width: 820px;
  margin: -10px auto 0;
}
.profile-shell {
  padding: 24px;
  border-radius: 30px;
  background: transparent;
  border: none;
  box-shadow: none;
  backdrop-filter: none;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.profile-shell::before {
  content: '';
  position: absolute;
  width: 260px;
  height: 260px;
  top: -40px;
  right: 20px;
  background: radial-gradient(circle, rgba(34, 197, 94, 0.26), transparent 70%);
  filter: blur(46px);
  pointer-events: none;
  animation: auroraGreen 11s ease-in-out infinite alternate;
}
.profile-shell::after {
  content: none;
}
.profile-hero {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 22px;
  background: rgba(10, 15, 30, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.25);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
}
.hero-copy h1 {
  margin: 6px 0;
  font-size: 1.9rem;
  color: #f8fafc;
}
.hero-copy p {
  margin: 0;
  color: rgba(148, 163, 184, 0.9);
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 0.72rem;
  color: rgba(148, 163, 184, 0.85);
}
.hero-meta {
  align-self: center;
  text-align: right;
}
.meta-label {
  display: block;
  font-size: 0.8rem;
  color: rgba(148, 163, 184, 0.85);
  text-transform: uppercase;
}
.meta-value {
  display: inline-flex;
  margin-top: 6px;
  padding: 6px 16px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  font-weight: 700;
}

.profile-card {
  border-radius: 22px;
  background: rgba(11, 17, 33, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 30px 70px rgba(2, 6, 23, 0.6);
  overflow: hidden;
}
.profile-headline {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 14px;
  padding: 18px 20px;
  align-items: center;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18);
}
.profile-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  font-weight: 800;
  color: #0f172a;
  box-shadow: 0 0 0 4px rgba(255, 255, 255, 0.05);
}
.headline-copy h2 {
  margin: 0;
  color: #f8fafc;
}
.headline-copy .email {
  margin: 4px 0 10px;
  color: rgba(148, 163, 184, 0.85);
}
.role-pill {
  display: inline-flex;
  padding: 6px 14px;
  border-radius: 14px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #0f172a;
}
.quick-id {
  text-align: right;
  font-size: 0.85rem;
  color: rgba(148, 163, 184, 0.85);
}
.quick-id span {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #f8fafc;
}

.profile-sections {
  padding: 18px 20px 26px;
  display: grid;
  gap: 16px;
}
.info-panel {
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 18px;
  padding: 14px;
  background: rgba(15, 23, 42, 0.65);
}
.info-panel h3 {
  margin: 0 0 18px;
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.2em;
  color: rgba(148, 163, 184, 0.9);
}
.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.data-item {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 14px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.5);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
}

/* --- CORRECCIÓN VISUAL: ROMPER EL CORREO --- */
.email-break {
  word-break: break-all; /* Esta propiedad hace la magia */
  overflow-wrap: break-word;
}

/* --- CORRECCIÓN: Que la tarjeta de correo ocupe toda la fila si es muy largo en móviles --- */
@media (max-width: 600px) {
  .full-width-mobile {
    grid-column: 1 / -1;
  }
}

.icon-circle {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.18);
  color: #60a5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
}
.icon-circle svg {
  width: 22px;
  height: 22px;
  stroke-width: 1.7;
}
.label {
  font-size: 0.78rem;
  color: rgba(148, 163, 184, 0.85);
  text-transform: uppercase;
  letter-spacing: 0.15em;
}
.value {
  margin: 4px 0 0;
  font-size: 1.2rem;
  color: #f8fafc;
  font-weight: 600;
}

.profile-avatar.admin,
.role-pill.admin {
  background: #facc15;
}
.profile-avatar.supervisor,
.role-pill.supervisor {
  background: #14b8a6;
}
.profile-avatar.mecanico,
.role-pill.mecanico {
  background: #22c55e;
}
.profile-avatar.porteria,
.profile-avatar.guardia,
.role-pill.porteria,
.role-pill.guardia {
  background: #fb923c;
}
.profile-avatar.chofer,
.role-pill.chofer {
  background: #3b82f6;
}
.profile-avatar.analista,
.role-pill.analista {
  background: #0ea5e9;
}

@keyframes auroraGreen {
  0% {
    transform: translate3d(8%, -4%, 0) scale(1.02);
    opacity: 0.38;
  }
  50% {
    transform: translate3d(-10%, 12%, 0) scale(1.12);
    opacity: 0.55;
  }
  100% {
    transform: translate3d(10%, -12%, 0) scale(1.06);
    opacity: 0.42;
  }
}

@media (max-width: 768px) {
  .profile-hero {
    flex-direction: column;
  }
  .profile-headline {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .quick-id {
    text-align: center;
  }
}
</style>
