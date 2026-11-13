/**
 * Возвращает корректный абсолютный URL для медиафайла.
 * Бэкенд (ImageField с use_url=True + request в контексте) уже отдаёт
 * полные URL вида http://localhost:8004/media/...
 * Если по какой-то причине придёт относительный путь — добавим хост.
 */
const BACKEND_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8004/api')
  .replace(/\/api\/?$/, '')

export function getMediaUrl(path) {
  if (!path) return null
  // Уже абсолютный URL — возвращаем как есть
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  // Относительный путь — добавляем хост бэкенда
  return `${BACKEND_URL}${path.startsWith('/') ? '' : '/'}${path}`
}
