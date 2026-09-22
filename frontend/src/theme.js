import { ref } from 'vue'

const media = window.matchMedia('(prefers-color-scheme: dark)')
export const isDark = ref(media.matches)

function apply(dark) {
  document.documentElement.classList.toggle('dark', dark)
}

apply(isDark.value)
media.addEventListener('change', (e) => {
  isDark.value = e.matches
  apply(isDark.value)
})
