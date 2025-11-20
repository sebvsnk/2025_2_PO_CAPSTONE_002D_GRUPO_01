import { defineConfig, globalIgnores } from 'eslint/config'
import globals from 'globals'
import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import pluginSecurity from 'eslint-plugin-security' // <--- 1. IMPORTAR ESTO
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'

export default defineConfig([
  {
    name: 'app/files-to-lint',
    files: ['**/*.{js,mjs,jsx,vue}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  {
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
  },

  // Configuraciones Base
  js.configs.recommended,

  // --- 2. CONFIGURACIÓN DE SEGURIDAD ---
  pluginSecurity.configs.recommended,

  // --- 3. REGLAS DE VUE (CAMBIO IMPORTANTE) ---
  // Cambiamos de 'essential' a 'recommended' para detectar riesgos como v-html
  ...pluginVue.configs['flat/recommended'],

  skipFormatting,
])
