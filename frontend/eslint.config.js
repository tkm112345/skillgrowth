import js from '@eslint/js'
import vue from 'eslint-plugin-vue'
import globals from 'globals'

export default [
  { ignores: ['dist/**'] },
  js.configs.recommended,
  ...vue.configs['flat/essential'],
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: globals.browser,
    },
    rules: {
      // Page-level route components (src/views/*.vue) are conventionally
      // single-word (Dashboard, Profile, ...); not a naming mistake.
      'vue/multi-word-component-names': 'off',
      // `catch (e) { ... }` without using `e` is the established pattern
      // in this codebase for swallow-and-fallback error handling.
      'no-unused-vars': ['error', { caughtErrors: 'none' }],
    },
  },
]
