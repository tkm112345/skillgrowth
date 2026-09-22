import { ref } from 'vue'

const MODE_KEY = 'skillgrowth-theme-mode' // 'system' | 'light' | 'dark'
const ACCENT_KEY = 'skillgrowth-accent'

export const ACCENT_HUES = ['blue', 'orange', 'aqua', 'yellow', 'magenta', 'green', 'violet', 'red']

const media = window.matchMedia('(prefers-color-scheme: dark)')

function resolveDark(mode) {
  return mode === 'dark' || (mode === 'system' && media.matches)
}

const savedMode = localStorage.getItem(MODE_KEY) || 'system'
export const themeMode = ref(savedMode)
export const isDark = ref(resolveDark(savedMode))

function applyMode(mode) {
  if (mode === 'system') {
    delete document.documentElement.dataset.theme
  } else {
    document.documentElement.dataset.theme = mode
  }
  isDark.value = resolveDark(mode)
  // Element Plus's own dark theme (imported in main.js) activates via this class.
  document.documentElement.classList.toggle('dark', isDark.value)
}

applyMode(savedMode)

media.addEventListener('change', () => {
  if (themeMode.value === 'system') {
    isDark.value = media.matches
    document.documentElement.classList.toggle('dark', isDark.value)
  }
})

export function setThemeMode(mode) {
  themeMode.value = mode
  localStorage.setItem(MODE_KEY, mode)
  applyMode(mode)
}

const savedAccent = localStorage.getItem(ACCENT_KEY) || ''
export const accentHue = ref(savedAccent)

function applyAccent(hue) {
  if (hue) {
    document.documentElement.style.setProperty('--accent', `var(--hue-${hue})`)
  } else {
    document.documentElement.style.removeProperty('--accent')
  }
}

applyAccent(savedAccent)

export function setAccentHue(hue) {
  accentHue.value = hue
  if (hue) localStorage.setItem(ACCENT_KEY, hue)
  else localStorage.removeItem(ACCENT_KEY)
  applyAccent(hue)
}
