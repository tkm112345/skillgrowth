import { beforeEach, describe, expect, it, vi } from 'vitest'

// theme.js reads matchMedia/localStorage and mutates document.documentElement
// as soon as it's imported, so each test needs a fresh module instance with
// a clean DOM/localStorage underneath it.
function mockMatchMedia(matches = false) {
  window.matchMedia = vi.fn().mockReturnValue({
    matches,
    addEventListener: () => {},
    removeEventListener: () => {},
  })
}

beforeEach(() => {
  localStorage.clear()
  document.documentElement.removeAttribute('data-theme')
  document.documentElement.classList.remove('dark')
  document.documentElement.style.removeProperty('--accent')
  mockMatchMedia(false)
  vi.resetModules()
})

describe('setThemeMode', () => {
  it('sets data-theme, toggles the dark class, and persists to localStorage', async () => {
    const { setThemeMode } = await import('./theme')
    setThemeMode('dark')
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('skillgrowth-theme-mode')).toBe('dark')
  })

  it('clears data-theme for system mode', async () => {
    const { setThemeMode } = await import('./theme')
    setThemeMode('dark')
    setThemeMode('system')
    expect(document.documentElement.dataset.theme).toBeUndefined()
  })
})

describe('setAccentHue', () => {
  it('sets the --accent CSS variable and persists it', async () => {
    const { setAccentHue } = await import('./theme')
    setAccentHue('violet')
    expect(document.documentElement.style.getPropertyValue('--accent')).toBe('var(--hue-violet)')
    expect(localStorage.getItem('skillgrowth-accent')).toBe('violet')
  })

  it('clears the accent when passed an empty value', async () => {
    const { setAccentHue } = await import('./theme')
    setAccentHue('violet')
    setAccentHue('')
    expect(document.documentElement.style.getPropertyValue('--accent')).toBe('')
    expect(localStorage.getItem('skillgrowth-accent')).toBeNull()
  })
})
