import { describe, expect, it } from 'vitest'

import { hueFor, tagStyle } from './hue'

const HUES = ['blue', 'orange', 'aqua', 'yellow', 'magenta', 'green', 'violet', 'red']

describe('hueFor', () => {
  it('is deterministic for the same key', () => {
    expect(hueFor('Python')).toBe(hueFor('Python'))
  })

  it('always returns one of the known hues', () => {
    for (const key of ['Python', 'public speaking', '', 'プロジェクト管理']) {
      expect(HUES).toContain(hueFor(key))
    }
  })

  it('coerces non-string keys', () => {
    expect(() => hueFor(123)).not.toThrow()
    expect(HUES).toContain(hueFor(123))
  })
})

describe('tagStyle', () => {
  it('derives color and borderColor from the same hue', () => {
    const hue = hueFor('Python')
    expect(tagStyle('Python')).toEqual({
      color: `var(--hue-${hue})`,
      borderColor: `var(--hue-${hue})`,
      backgroundColor: 'transparent',
    })
  })
})
