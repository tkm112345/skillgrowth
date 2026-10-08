import { flushPromises, mount } from '@vue/test-utils'
import ElementPlus from 'element-plus'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

import { i18n } from '../i18n'
import { api } from '../api'
import GlobalSearch from './GlobalSearch.vue'

vi.mock('../api', () => ({
  api: { search: vi.fn() },
}))

function makeRouter() {
  const blank = { template: '<div />' }
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', component: blank },
      { path: '/skills', component: blank },
      { path: '/timeline', component: blank },
      { path: '/portfolio', component: blank },
    ],
  })
}

let currentWrapper = null

async function mountSearch() {
  const router = makeRouter()
  await router.push('/')
  currentWrapper = mount(GlobalSearch, {
    global: { plugins: [i18n, router, ElementPlus] },
  })
  return { wrapper: currentWrapper, router }
}

beforeEach(() => {
  api.search.mockReset()
  vi.useFakeTimers()
})

afterEach(() => {
  // el-popover teleports its panel to document.body; unmount to tear that
  // down too, otherwise it leaks into the next test's document.body query.
  currentWrapper?.unmount()
  currentWrapper = null
  vi.useRealTimers()
})

describe('GlobalSearch', () => {
  it('does not search for fewer than 2 characters', async () => {
    const { wrapper } = await mountSearch()
    await wrapper.find('input').setValue('a')
    vi.advanceTimersByTime(300)
    await flushPromises()
    expect(api.search).not.toHaveBeenCalled()
  })

  it('searches after the debounce and shows the result', async () => {
    api.search.mockResolvedValue([{ entity_type: 'skill', entity_id: 1, title: 'Python', snippet: 'skill' }])
    const { wrapper } = await mountSearch()
    await wrapper.find('input').setValue('py')
    vi.advanceTimersByTime(300)
    await flushPromises()
    expect(api.search).toHaveBeenCalledWith('py')
    // el-popover teleports its panel to document.body, outside wrapper.element.
    expect(document.body.textContent).toContain('Python')
  })

  it('navigates to the entity route on result click', async () => {
    api.search.mockResolvedValue([{ entity_type: 'skill', entity_id: 1, title: 'Python', snippet: 'skill' }])
    const { wrapper, router } = await mountSearch()
    const pushSpy = vi.spyOn(router, 'push')
    await wrapper.find('input').setValue('py')
    vi.advanceTimersByTime(300)
    await flushPromises()
    document.body.querySelector('.search-result').dispatchEvent(new Event('mousedown', { bubbles: true }))
    await flushPromises()
    expect(pushSpy).toHaveBeenCalledWith({ path: '/skills', query: { highlight: 1 } })
  })
})
