// Сбор поведенческих метрик посетителя главной страницы.
// Раз в секунду накопленные данные уходят в POST /api/behavior-metrics/.

// Верхняя граница точек курсора, чтобы визит длиной в часы не раздувал payload.
const CURSOR_POINTS_LIMIT = 3600
// Обрезка метки кнопки: длинные тексты портят читаемость статистики.
const BUTTON_LABEL_LIMIT = 60

const sessionId = crypto.randomUUID()
const startedAt = Date.now()
const buttonsClicked = {}
const cursorPositions = []

let lastPointer = null

function buttonLabel(element) {
  const raw = element.getAttribute('aria-label') || element.textContent || element.tagName.toLowerCase()
  const label = raw.replace(/\s+/g, ' ').trim().slice(0, BUTTON_LABEL_LIMIT)
  return label || element.tagName.toLowerCase()
}

function toPercent(value, size) {
  return Number(((value / size) * 100).toFixed(1))
}

document.addEventListener('click', (event) => {
  const target = event.target.closest('button, a, select, input, textarea, [role="button"]')
  if (!target) return
  const label = buttonLabel(target)
  buttonsClicked[label] = (buttonsClicked[label] || 0) + 1
})

document.addEventListener('mousemove', (event) => {
  lastPointer = { x: event.clientX, y: event.clientY }
})

function sendMetrics() {
  const timeOnPage = Math.round((Date.now() - startedAt) / 1000)
  // Ошибки сети глушатся: сбор статистики не должен ломать работу сайта.
  fetch('/api/behavior-metrics/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      application_id: 0,
      time_on_page: timeOnPage,
      buttons_clicked: JSON.stringify(buttonsClicked),
      cursor_positions: JSON.stringify(cursorPositions),
      return_frequency: 0,
    }),
  }).catch(() => {})
}

setInterval(() => {
  // До первого движения мыши координат нет — углы карты не должны «греться» зря.
  if (lastPointer && cursorPositions.length < CURSOR_POINTS_LIMIT) {
    cursorPositions.push({
      x: toPercent(lastPointer.x, window.innerWidth),
      y: toPercent(lastPointer.y, window.innerHeight),
    })
  }
  sendMetrics()
}, 1000)
