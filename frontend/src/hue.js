const HUES = ['blue', 'orange', 'aqua', 'yellow', 'magenta', 'green', 'violet', 'red']

// Deterministic hash so the same category/type always gets the same hue,
// without maintaining an explicit lookup table per page.
export function hueFor(key) {
  let hash = 0
  for (const ch of String(key)) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0
  return HUES[hash % HUES.length]
}

export function tagStyle(key) {
  const hue = hueFor(key)
  return {
    color: `var(--hue-${hue})`,
    borderColor: `var(--hue-${hue})`,
    backgroundColor: 'transparent',
  }
}
