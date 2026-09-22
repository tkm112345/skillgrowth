import { createI18n } from 'vue-i18n'

import en from './locales/en.json'
import ja from './locales/ja.json'

const STORAGE_KEY = 'skillgrowth-locale'
const savedLocale = localStorage.getItem(STORAGE_KEY)

export const i18n = createI18n({
  legacy: false,
  locale: savedLocale || 'en',
  fallbackLocale: 'en',
  messages: { en, ja },
})

export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem(STORAGE_KEY, locale)
}
