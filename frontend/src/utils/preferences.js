const STORAGE_KEY = 'elder_preferences'

export const defaultPreferences = {
  language: 'zh-CN',
  appearance: 'light',
  fontScale: 'default',
}

export function getPreferences() {
  if (typeof window === 'undefined') return { ...defaultPreferences }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...defaultPreferences }
    const parsed = JSON.parse(raw)
    return {
      ...defaultPreferences,
      ...parsed,
    }
  } catch {
    return { ...defaultPreferences }
  }
}

export function savePreferences(prefs) {
  const merged = {
    ...defaultPreferences,
    ...prefs,
  }
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged))
  }
  applyPreferences(merged)
  return merged
}

export function applyPreferences(prefs = getPreferences()) {
  if (typeof document === 'undefined') return prefs
  const root = document.documentElement
  const body = document.body
  root.lang = prefs.language || defaultPreferences.language
  root.dataset.appearance = prefs.appearance || defaultPreferences.appearance
  root.dataset.fontScale = prefs.fontScale || defaultPreferences.fontScale
  body.dataset.appearance = root.dataset.appearance
  body.dataset.fontScale = root.dataset.fontScale
  window.dispatchEvent(new CustomEvent('elder-preferences-changed', { detail: prefs }))
  return prefs
}

export function resetPreferences() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(STORAGE_KEY)
  }
  return savePreferences(defaultPreferences)
}
