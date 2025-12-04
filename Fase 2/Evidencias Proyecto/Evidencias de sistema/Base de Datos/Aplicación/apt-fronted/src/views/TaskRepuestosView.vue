<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const taskId = route.params.taskId
const usedRepuestos = ref([])
const availableRepuestos = ref([])

const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMsg = ref(null)
const successMsg = ref(null)

const newRepuestoForm = ref({
  repuesto_id: null,
  cantidad: 1,
})

const API_BASE_URL = import.meta.env.VITE_API_URL

const fetchUsedRepuestos = async () => {
  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/repuestos/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error al cargar repuestos usados.')
    usedRepuestos.value = await response.json()
  } catch (error) {
    errorMsg.value = error.message
  }
}

const fetchAvailableRepuestos = async () => {
  try {
    const url = `${API_BASE_URL}/repuestos/`
    const response = await fetch(url, {
      headers: { Authorization: `Bearer ${authStore.token}` },
    })
    if (!response.ok) throw new Error('Error al cargar catálogo de repuestos.')
    availableRepuestos.value = await response.json()
  } catch (error) {
    errorMsg.value = error.message
  }
}

const handleAddRepuesto = async () => {
  if (!newRepuestoForm.value.repuesto_id || newRepuestoForm.value.cantidad <= 0) {
    errorMsg.value = 'Debe seleccionar un repuesto y una cantidad válida.'
    return
  }

  isSubmitting.value = true
  errorMsg.value = null
  successMsg.value = null

  const payload = {
    repuesto: newRepuestoForm.value.repuesto_id,
    cantidad: newRepuestoForm.value.cantidad,
  }

  try {
    const url = `${API_BASE_URL}/tareas/${taskId}/repuestos/`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.token}`,
      },
      body: JSON.stringify(payload),
    })

    const data = await response.json()
    if (!response.ok) {
       
      const errorKey = Object.keys(data)[0]
      // eslint-disable-next-line security/detect-object-injection
      throw new Error(data[errorKey]?.[0] || 'Error al añadir el repuesto.')
    }

    successMsg.value = 'Listo. Repuesto añadido con éxito.'
    newRepuestoForm.value.repuesto_id = null
    newRepuestoForm.value.cantidad = 1

    await fetchUsedRepuestos()
  } catch (error) {
    errorMsg.value = error.message
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  isLoading.value = true
  await Promise.all([fetchUsedRepuestos(), fetchAvailableRepuestos()])
  isLoading.value = false
})
</script>

<template>
  <div class="repuestos-page">
    <div class="repuestos-container">
      <header class="repuestos-header">
        <div class="header-copy">
          <h1>Repuestos usados</h1>
          <p class="subtitle">Asigna repuestos del catálogo a la tarea.</p>
        </div>
        <button class="back-button" @click="router.push({ name: 'TaskDetail', params: { taskId } })">
          Volver a la tarea #{{ taskId }}
        </button>
      </header>

      <Transition name="alert-fade">
        <div v-if="errorMsg" class="status-banner error">{{ errorMsg }}</div>
      </Transition>
      <Transition name="alert-fade">
        <div v-if="successMsg" class="status-banner success">{{ successMsg }}</div>
      </Transition>

      <div class="repuestos-group">
        <div class="repuestos-content-grid">
          <section class="glass-card">
            <div class="section-heading">
              <div>
                <p class="eyebrow">Formulario</p>
                <h2>Añadir repuesto</h2>
              </div>
          </div>
          <form class="add-form" @submit.prevent="handleAddRepuesto">
            <div class="form-group">
              <label>Repuesto (catálogo)</label>
              <select v-model="newRepuestoForm.repuesto_id" required>
                <option :value="null" disabled>Selecciona un repuesto...</option>
                <option v-for="r in availableRepuestos" :key="r.id" :value="r.id">
                  [{{ r.codigo || 'S/C' }}] {{ r.descripcion }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Cantidad (ej: 1, 0.5)</label>
              <input
                v-model.number="newRepuestoForm.cantidad"
                type="number"
                min="0.1"
                step="0.1"
                required
              />
            </div>
            <button type="submit" :disabled="isSubmitting" class="primary-button">
              {{ isSubmitting ? 'Añadiendo...' : 'Añadir repuesto' }}
            </button>
          </form>
          </section>

          <section class="glass-card">
            <div class="section-heading">
              <div>
                <p class="eyebrow">Listado</p>
                <h2>Repuestos usados ({{ usedRepuestos.length }})</h2>
              </div>
            </div>
            <div v-if="isLoading" class="loading-state">
              <div class="spinner-ring"><span></span></div>
              <div>
                <p>Cargando repuestos</p>
                <small>Traemos tus repuestos usados...</small>
              </div>
            </div>
            <div v-else-if="usedRepuestos.length > 0" class="table-wrapper">
              <table class="repuestos-table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Descripción</th>
                    <th>Cantidad</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in usedRepuestos" :key="item.id">
                    <td>{{ item.repuesto.codigo || 'S/C' }}</td>
                    <td>{{ item.repuesto.descripcion }}</td>
                    <td>{{ item.cantidad }} ({{ item.repuesto.unidad_medida }})</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="empty-state">No se han añadido repuestos a esta tarea.</p>
          </section>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.repuestos-page {
  position: relative;
  min-height: 100vh;
  padding: 40px 20px 70px;
  background: transparent;
  background-image: none;
  color: #e2e8f0;
}
.repuestos-page::before {
  content: none;
}
.repuestos-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0;
  border-radius: 0;
  border: none;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
  position: relative;
}
.repuestos-container::before {
  content: none;
}
.repuestos-container > * {
  position: relative;
  z-index: 1;
}
.repuestos-header {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
  padding-bottom: 18px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.25);
  margin-bottom: 24px;
}
.header-copy h1 {
  margin: 0;
  font-size: 1.9rem;
  color: #f8fafc;
}
.subtitle {
  margin: 6px 0 0;
  color: rgba(226, 232, 240, 0.75);
}
.back-button {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.4);
  color: #bbf7d0;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: background 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}
.back-button:hover {
  background: rgba(16, 185, 129, 0.3);
  box-shadow: 0 12px 30px rgba(16, 185, 129, 0.35);
  transform: translateY(-1px);
}
.status-banner {
  margin-bottom: 12px;
  padding: 12px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(8, 47, 73, 0.4);
  font-weight: 600;
}
.status-banner.success {
  color: #34d399;
  border-color: rgba(34, 197, 94, 0.45);
  background: rgba(16, 185, 129, 0.18);
}
.status-banner.error {
  color: #f87171;
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(127, 29, 29, 0.25);
}
.alert-fade-enter-active,
.alert-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.alert-fade-enter-from,
.alert-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
.repuestos-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  margin-top: 4px;
  flex: 1;
}
.repuestos-group {
  margin-top: 16px;
  padding: 28px;
  border-radius: 32px;
  background:
    radial-gradient(circle at 12% 40%, rgba(59, 130, 246, 0.12), transparent 55%),
    radial-gradient(circle at 88% 30%, rgba(16, 185, 129, 0.12), transparent 55%),
    linear-gradient(145deg, rgba(5, 10, 23, 0.92), rgba(9, 13, 26, 0.92));
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow:
    0 35px 90px rgba(2, 6, 23, 0.7),
    0 0 35px rgba(16, 185, 129, 0.15);
  min-height: 480px;
  display: flex;
  flex-direction: column;
}
.glass-card {
  background: rgba(10, 15, 30, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 24px;
  padding: 18px;
  box-shadow:
    0 25px 60px rgba(2, 6, 23, 0.7),
    inset 0 0 0 1px rgba(255, 255, 255, 0.02);
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-heading h2 {
  margin: 4px 0 0;
  color: #f8fafc;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.3em;
  font-size: 0.65rem;
  color: rgba(191, 219, 254, 0.7);
}
.add-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-group label {
  font-weight: 600;
  color: #e2e8f0;
  margin-bottom: 4px;
  display: block;
}
.form-group input,
.form-group select {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(15, 23, 42, 0.75);
  color: #f8fafc;
  outline: none;
  transition: border 0.2s ease, box-shadow 0.2s ease;
  box-sizing: border-box;
}
.form-group input:focus,
.form-group select:focus {
  border-color: rgba(16, 185, 129, 0.6);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}
.primary-button {
  margin: 12px 0 0;
  padding: 12px 16px;
  border: none;
  border-radius: 14px;
  font-weight: 700;
  cursor: pointer;
  color: #042f2e;
  background: linear-gradient(120deg, #22d3ee, #10b981, #3b82f6);
  box-shadow: 0 18px 45px rgba(16, 185, 129, 0.35);
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
  width: min(100%, 320px);
  align-self: center;
}
.primary-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}
.primary-button:hover:enabled {
  transform: translateY(-1px);
}
.loading-state {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px dashed rgba(148, 163, 184, 0.35);
  color: #e2e8f0;
}
.spinner-ring {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  position: relative;
  border: 2px solid rgba(59, 130, 246, 0.2);
}
.spinner-ring span {
  position: absolute;
  inset: -2px;
  border-radius: 50%;
  border: 3px solid transparent;
  border-top-color: #22d3ee;
  border-right-color: #10b981;
  animation: spin 0.9s linear infinite;
}
.table-wrapper {
  max-height: 340px;
  overflow-y: auto;
  padding-right: 8px;
  margin-right: -4px;
}
.table-wrapper::-webkit-scrollbar {
  width: 8px;
}
.table-wrapper::-webkit-scrollbar-track {
  background: rgba(15, 23, 42, 0.35);
  border-radius: 999px;
  border: 1px solid rgba(59, 130, 246, 0.25);
  box-shadow: inset 0 0 12px rgba(2, 6, 23, 0.55);
}
.table-wrapper::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, rgba(56, 189, 248, 0.85), rgba(16, 185, 129, 0.95));
  border-radius: 999px;
  box-shadow:
    inset 0 0 6px rgba(15, 23, 42, 0.6),
    0 6px 18px rgba(56, 189, 248, 0.45);
}
.table-wrapper {
  scrollbar-width: thin;
  scrollbar-color: rgba(16, 185, 129, 0.9) rgba(15, 23, 42, 0.35);
}
.repuestos-table {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 14px;
  background: rgba(8, 12, 25, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.2);
  table-layout: fixed;
}
.repuestos-table th,
.repuestos-table td {
  padding: 12px;
  text-align: left;
  color: #e2e8f0;
  word-break: break-word;
}
.repuestos-table th {
  background: rgba(15, 23, 42, 0.85);
  font-weight: 700;
  letter-spacing: 0.02em;
}
.repuestos-table tr:nth-child(even) {
  background: rgba(8, 47, 73, 0.1);
}
.repuestos-table tr + tr td {
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}
.empty-state {
  padding: 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px dashed rgba(148, 163, 184, 0.3);
  color: rgba(226, 232, 240, 0.8);
  text-align: center;
}
@media (max-width: 768px) {
  .repuestos-container {
    padding: 24px;
  }
  .repuestos-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .back-button {
    align-self: stretch;
    text-align: center;
  }
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
