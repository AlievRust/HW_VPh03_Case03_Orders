import './admin.css'

const root = document.querySelector('#admin-app')
const tokenKey = 'luxury_auto_admin_token'
let token = sessionStorage.getItem(tokenKey)
let services = []
let editingId = null

const api = async (path, options = {}) => {
  const headers = { 'Content-Type': 'application/json', ...options.headers }
  if (token) headers.Authorization = `Bearer ${token}`
  const response = await fetch(`/api${path}`, { ...options, headers })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || 'Ошибка запроса')
  }
  return response.status === 204 ? null : response.json()
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function showAuth(canRegister = false, error = '') {
  root.innerHTML = `
    <main class="admin-shell auth-shell">
      <section class="auth-card">
        <p class="admin-kicker">LUXURY-AUTO / ADMIN</p>
        <h1>Панель управления</h1>
        <p class="auth-lead">Войдите, чтобы управлять услугами и диапазонами бюджета.</p>
        <form id="login-form" class="admin-form">
          <label>Логин<input name="login" required autocomplete="username" /></label>
          <label>Пароль<input name="password" type="password" required autocomplete="current-password" /></label>
          <button class="admin-button" type="submit">Войти</button>
          <p class="form-error">${escapeHtml(error)}</p>
        </form>
        ${canRegister ? '<button class="link-button" id="show-register">Зарегистрировать первого администратора</button>' : ''}
        <a class="back-link" href="/">Вернуться на сайт</a>
      </section>
    </main>
  `
  document.querySelector('#login-form').addEventListener('submit', login)
  document.querySelector('#show-register')?.addEventListener('click', showRegister)
}

function showRegister() {
  root.innerHTML = `
    <main class="admin-shell auth-shell">
      <section class="auth-card">
        <p class="admin-kicker">LUXURY-AUTO / FIRST ACCESS</p>
        <h1>Создать администратора</h1>
        <p class="auth-lead">Регистрация доступна только до создания первой учётной записи.</p>
        <form id="register-form" class="admin-form">
          <label>Логин<input name="login" required minlength="3" autocomplete="username" /></label>
          <label>Имя в панели<input name="nickname" required autocomplete="nickname" /></label>
          <label>Пароль<input name="password" type="password" required minlength="8" autocomplete="new-password" /></label>
          <button class="admin-button" type="submit">Создать администратора</button>
          <p class="form-error"></p>
        </form>
        <button class="link-button" id="back-login">Вернуться ко входу</button>
      </section>
    </main>
  `
  document.querySelector('#register-form').addEventListener('submit', register)
  document.querySelector('#back-login').addEventListener('click', initializeAuth)
}

async function initializeAuth() {
  if (token) {
    try {
      await api('/auth/me')
      return renderAdmin()
    } catch {
      sessionStorage.removeItem(tokenKey)
      token = null
    }
  }
  try {
    const status = await api('/auth/registration-status')
    showAuth(status.can_register)
  } catch {
    showAuth(false, 'Не удалось подключиться к серверу')
  }
}

async function login(event) {
  event.preventDefault()
  const form = event.currentTarget
  const error = form.querySelector('.form-error')
  try {
    const result = await api('/auth/login', { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(form))) })
    token = result.access_token
    sessionStorage.setItem(tokenKey, token)
    renderAdmin()
  } catch (requestError) {
    error.textContent = requestError.message
  }
}

async function register(event) {
  event.preventDefault()
  const form = event.currentTarget
  const error = form.querySelector('.form-error')
  try {
    await api('/auth/register', { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(form))) })
    initializeAuth()
  } catch (requestError) {
    error.textContent = requestError.message
  }
}

function renderAdmin() {
  root.innerHTML = `
    <main class="admin-shell">
      <header class="admin-header">
        <div><p class="admin-kicker">LUXURY-AUTO / ADMIN</p><h1>Услуги</h1></div>
        <div class="header-actions"><a class="back-link" href="/">На сайт</a><button class="link-button" id="show-stats">Статистика</button><button class="link-button" id="logout">Выйти</button></div>
      </header>
      <section class="admin-layout">
        <form class="admin-card admin-form" id="service-form">
          <h2 id="service-form-title">Новая услуга</h2>
          <label>Название услуги<input name="service_name" required maxlength="255" /></label>
          <label>Описание<textarea name="service_description" rows="5"></textarea></label>
          <div class="number-grid">
            <label>Минимальный бюджет<input name="budget_min" type="number" min="0" required /></label>
            <label>Максимальный бюджет<input name="budget_max" type="number" min="0" required /></label>
            <label>Шаг бюджета<input name="budget_step" type="number" min="1" required value="1" /></label>
          </div>
          <label class="checkbox-label"><input name="is_active" type="checkbox" checked /> Показывать на сайте</label>
          <div class="form-actions"><button class="admin-button" type="submit">Сохранить</button><button class="link-button" type="button" id="cancel-edit">Очистить</button></div>
          <p class="form-error"></p>
        </form>
        <section class="admin-card"><div class="list-heading"><h2>Список услуг</h2><span id="service-count"></span></div><div id="service-list"></div></section>
      </section>
      <section class="admin-card admin-form admin-users-card">
        <h2>Добавить администратора</h2>
        <form id="admin-form" class="admin-form-inline">
          <input name="login" required minlength="3" placeholder="Логин" />
          <input name="nickname" required placeholder="Имя в панели" />
          <input name="password" type="password" required minlength="8" placeholder="Пароль от 8 символов" />
          <button class="admin-button" type="submit">Добавить</button>
        </form>
        <p class="form-error"></p>
      </section>
    </main>
  `
  document.querySelector('#logout').addEventListener('click', () => {
    sessionStorage.removeItem(tokenKey)
    token = null
    initializeAuth()
  })
  document.querySelector('#show-stats').addEventListener('click', showStatsModal)
  document.querySelector('#service-form').addEventListener('submit', saveService)
  document.querySelector('#cancel-edit').addEventListener('click', resetServiceForm)
  document.querySelector('#admin-form').addEventListener('submit', addAdmin)
  loadServices()
}

async function loadServices() {
  try {
    services = await api('/admin-settings')
    renderServiceList()
  } catch (error) {
    document.querySelector('#service-list').innerHTML = `<p class="form-error">${escapeHtml(error.message)}</p>`
  }
}

function renderServiceList() {
  document.querySelector('#service-count').textContent = `${services.length} шт.`
  document.querySelector('#service-list').innerHTML = services.length ? services.map((service) => `
    <article class="service-row">
      <div><h3>${escapeHtml(service.service_name)}</h3><p>${escapeHtml(service.service_description || 'Без описания')}</p><small>${service.budget_min}–${service.budget_max} ₽ / шаг ${service.budget_step} · ${service.is_active ? 'активна' : 'скрыта'}</small></div>
      <div class="row-actions"><button class="link-button" data-edit="${service.id}">Изменить</button><button class="danger-button" data-delete="${service.id}">Удалить</button></div>
    </article>
  `).join('') : '<p class="empty-state">Услуг пока нет.</p>'
  document.querySelectorAll('[data-edit]').forEach((button) => button.addEventListener('click', () => editService(Number(button.dataset.edit))))
  document.querySelectorAll('[data-delete]').forEach((button) => button.addEventListener('click', () => deleteService(Number(button.dataset.delete))))
}

function editService(id) {
  const service = services.find((item) => item.id === id)
  if (!service) return
  editingId = id
  const form = document.querySelector('#service-form')
  Object.entries(service).forEach(([key, value]) => {
    const field = form.elements[key]
    if (!field) return
    if (field.type === 'checkbox') field.checked = value
    else field.value = value ?? ''
  })
  document.querySelector('#service-form-title').textContent = 'Редактировать услугу'
  form.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function resetServiceForm() {
  editingId = null
  document.querySelector('#service-form').reset()
  document.querySelector('#service-form-title').textContent = 'Новая услуга'
  document.querySelector('[name="budget_step"]').value = 1
}

async function saveService(event) {
  event.preventDefault()
  const form = event.currentTarget
  const error = form.querySelector('.form-error')
  const values = Object.fromEntries(new FormData(form))
  values.is_active = form.elements.is_active.checked
  values.budget_min = Number(values.budget_min)
  values.budget_max = Number(values.budget_max)
  values.budget_step = Number(values.budget_step)
  try {
    await api(editingId ? `/admin-settings/${editingId}` : '/admin-settings', { method: editingId ? 'PUT' : 'POST', body: JSON.stringify(values) })
    resetServiceForm()
    await loadServices()
  } catch (requestError) {
    error.textContent = requestError.message
  }
}

async function deleteService(id) {
  if (!window.confirm('Удалить эту услугу?')) return
  try {
    await api(`/admin-settings/${id}`, { method: 'DELETE' })
    await loadServices()
  } catch (error) {
    window.alert(error.message)
  }
}

const PERIOD_TITLES = { day: 'За день', week: 'За неделю', month: 'За месяц' }

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const rest = seconds % 60
  const mm = String(minutes).padStart(2, '0')
  const ss = String(rest).padStart(2, '0')
  return hours > 0 ? `${hours}:${mm}:${ss}` : `${minutes}:${ss}`
}

function drawHeatmap(canvas, points) {
  const ratio = window.devicePixelRatio || 1
  const width = canvas.clientWidth || 900
  const height = Math.round(width * 0.62)
  canvas.width = Math.round(width * ratio)
  canvas.height = Math.round(height * ratio)
  canvas.style.height = `${height}px`

  const context = canvas.getContext('2d')
  context.scale(ratio, ratio)
  context.clearRect(0, 0, width, height)
  if (points.length === 0) return

  // Альфа подстраивается под число точек: иначе при тысячах точек «горит» вся карта.
  const alpha = Math.min(0.15, Math.max(0.03, 60 / points.length))
  const radius = Math.max(18, width * 0.022)

  for (const point of points) {
    const x = (point.x / 100) * width
    const y = (point.y / 100) * height
    const gradient = context.createRadialGradient(x, y, 0, x, y, radius)
    gradient.addColorStop(0, `rgba(214, 151, 70, ${alpha})`)
    gradient.addColorStop(1, 'rgba(214, 151, 70, 0)')
    context.fillStyle = gradient
    context.beginPath()
    context.arc(x, y, radius, 0, Math.PI * 2)
    context.fill()
  }
}

async function showStatsModal() {
  const overlay = document.createElement('div')
  overlay.className = 'stats-overlay'
  overlay.innerHTML = `
    <div class="stats-modal" role="dialog" aria-modal="true" aria-label="Статистика посетителей">
      <header class="stats-header">
        <div><p class="admin-kicker">LUXURY-AUTO / METRICS</p><h2>Статистика посетителей</h2></div>
        <button class="link-button" id="stats-close" aria-label="Закрыть">✕</button>
      </header>
      <p class="stats-note">Загружаем данные...</p>
    </div>
  `
  document.body.appendChild(overlay)

  const closeModal = () => {
    document.removeEventListener('keydown', escapeHandler)
    overlay.remove()
  }
  const escapeHandler = (event) => {
    if (event.key === 'Escape') closeModal()
  }
  overlay.addEventListener('click', (event) => {
    if (event.target === overlay) closeModal()
  })
  overlay.querySelector('#stats-close').addEventListener('click', closeModal)
  document.addEventListener('keydown', escapeHandler)

  let stats
  try {
    stats = await api('/behavior-metrics/stats')
  } catch (error) {
    overlay.querySelector('.stats-note').textContent = `Не удалось загрузить статистику: ${error.message}`
    return
  }

  const cards = Object.entries(stats.periods).map(([key, period]) => `
    <article class="stat-card">
      <h3>${PERIOD_TITLES[key] || key}</h3>
      <p class="stat-main"><strong>${formatDuration(period.avg_time_on_page)}</strong><span>среднее время на странице</span></p>
      <p class="stat-row"><span>Максимум</span><strong>${formatDuration(period.max_time_on_page)}</strong></p>
      <p class="stat-row"><span>Визитов</span><strong>${period.sessions}</strong></p>
    </article>
  `).join('')

  const modal = overlay.querySelector('.stats-modal')
  modal.innerHTML = `
    <header class="stats-header">
      <div><p class="admin-kicker">LUXURY-AUTO / METRICS</p><h2>Статистика посетителей</h2></div>
      <button class="link-button" id="stats-close" aria-label="Закрыть">✕</button>
    </header>
    <div class="stats-cards">${cards}</div>
    <section class="stats-heatmap">
      <h3>Хитмэп курсора</h3>
      <p class="stats-note">Чем теплее зона, тем дольше посетители держат курсор в этой области экрана.</p>
      <canvas id="stats-canvas" aria-label="Хитмэп позиций курсора"></canvas>
      <p class="stats-note">Всего визитов: ${stats.total_sessions} · точек курсора: ${stats.cursor_positions.length}</p>
    </section>
  `
  modal.querySelector('#stats-close').addEventListener('click', closeModal)
  drawHeatmap(modal.querySelector('#stats-canvas'), stats.cursor_positions)
}

initializeAuth()
