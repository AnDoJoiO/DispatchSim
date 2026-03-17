import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const activeTab = ref('emergency')
  const theme     = ref(localStorage.getItem('dispatch_theme') || 'light')

  function applyTheme(t) {
    theme.value = t
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('dispatch_theme', t)
  }

  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  function showTab(tab) {
    activeTab.value = tab
  }

  // Sync document attribute with stored theme on init
  applyTheme(theme.value)

  return { activeTab, theme, showTab, applyTheme, toggleTheme }
})
