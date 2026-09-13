import './style.css'

const app = document.querySelector('#app')
const startedAt = Date.now()
const events = [{ type: 'page_view', at: new Date().toISOString() }]
let clickCount = 0
let cursorPauses = 0
let formStarted = false
let returnVisits = 0
let lastMoveAt = Date.now()

let services = []

app.innerHTML = `
  <main class="site-shell">
    <div class="ambient ambient-one"></div>
    <div class="ambient ambient-two"></div>
    <div class="ambient ambient-three"></div>
    <nav class="topbar">
      <a class="brand" href="#top" aria-label="Luxury-Auto, на главную">
        <span class="brand-mark">L</span>
        <span><strong>LUXURY</strong><small>AUTO SERVICE</small></span>
      </a>
      <div class="nav-links">
        <a href="#services">Услуги</a>
        <a href="#request">Консультация</a>
      </div>
      <a class="nav-phone" href="tel:+79990000000">+7 999 000 00 00 <span>↗</span></a>
    </nav>

    <section class="hero" id="top">
      <div class="hero-copy">
        <p class="eyebrow"><span></span> Премиальный уход без компромиссов</p>
        <h1>Ваш автомобиль.<br /><em>Наше мастерство.</em></h1>
        <p class="hero-text">Luxury-Auto возвращает автомобилю состояние, в котором он был создан. Персональный сервис, деликатный подход и результат, который видно в каждой линии.</p>
        <div class="hero-actions">
          <a class="button button-gold" href="#request">Рассчитать обслуживание <span>↓</span></a>
          <div class="trust-note"><strong>12 лет</strong><span>заботимся<br />о вашем авто</span></div>
        </div>
      </div>
      <div class="hero-visual" aria-hidden="true">
        <div class="visual-ring"></div>
        <div class="visual-label"><span>THE ART OF</span><strong>DETAIL</strong></div>
        <div class="visual-orbit orbit-one"></div>
        <div class="visual-orbit orbit-two"></div>
      </div>
      <div class="scroll-cue"><span></span> Листайте, чтобы узнать больше</div>
    </section>

    <section class="services section" id="services">
      <div class="section-heading"><p class="eyebrow"><span></span> Что мы делаем</p><h2>Сервис, который<br /><em>соответствует вам.</em></h2></div>
      <div class="service-grid"></div>
    </section>

    <section class="request-section section" id="request">
      <div class="section-heading request-heading"><p class="eyebrow"><span></span> Персональный расчёт</p><h2>Расскажите нам<br /><em>о вашем автомобиле.</em></h2><p class="section-lead">Заполните короткую форму. Мы изучим запрос и свяжемся с вами, чтобы подобрать идеальное решение.</p></div>
      <form class="request-card" id="lead-form">
        <div class="form-progress"><span>01 — О вас</span><span>02 — Об автомобиле</span><span>03 — Детали</span></div>
        <div class="form-section"><div class="form-section-title"><span>01</span><div><h3>Контактные данные</h3><p>Как к вам обратиться?</p></div></div><div class="field-grid"><label>Имя *<input name="first_name" required placeholder="Александр" /></label><label>Фамилия *<input name="last_name" required placeholder="Волков" /></label><label class="wide">Телефон или e-mail *<input name="contact_value" required placeholder="+7 999 000 00 00" /></label><label>Способ связи<select name="contact_method"><option>Телефон</option><option>WhatsApp</option><option>Telegram</option><option>E-mail</option></select></label></div></div>
        <div class="form-section"><div class="form-section-title"><span>02</span><div><h3>Ваш автомобиль</h3><p>Несколько деталей помогут нам подготовиться.</p></div></div><div class="field-grid"><label class="wide">Марка и модель *<input name="business_info" required placeholder="Например, Porsche Cayenne 2024" /></label><label>Размер автомобиля<select name="company_size"><option>Компактный</option><option selected>Средний</option><option>Большой SUV</option><option>Премиальный / спорткар</option></select></label><label>Тип обслуживания<select name="task_volume" id="service-select" required></select></label></div></div>
        <div class="form-section"><div class="form-section-title"><span>03</span><div><h3>Задача и пожелания</h3><p>Настроим предложение под ваш сценарий.</p></div></div><div class="field-grid"><label class="range-label wide">Ориентировочный бюджет <output id="budget-output"></output><input class="range" name="budget" id="budget" type="range" /><span class="range-scale"><i id="budget-min"></i><i id="budget-max"></i></span></label><label>Желаемый срок<select name="result_deadline"><option>В ближайшие дни</option><option>В течение недели</option><option>В течение месяца</option><option>Дата не важна</option></select></label><label>Ваша роль<select name="customer_role"><option>Владелец автомобиля</option><option>Представитель компании</option><option>Автодилер</option><option>Другое</option></select></label><label>Удобное время<select name="preferred_time"><option>Утро, 9:00–12:00</option><option>День, 12:00–18:00</option><option>Вечер, 18:00–21:00</option><option>В любое время</option></select></label><label class="wide">Комментарий<textarea name="comments" rows="4" placeholder="Расскажите, какой результат вы хотите получить..."></textarea></label></div></div>
        <input type="hidden" name="product_interest" value="Обслуживание Luxury-Auto" /><input type="hidden" name="task_type" value="Индивидуальный расчёт" />
        <div class="form-footer"><p>Нажимая кнопку, вы соглашаетесь на обработку данных для связи по заявке.</p><button class="button button-gold" type="submit">Отправить заявку <span>↗</span></button></div><div class="form-status" role="status" aria-live="polite"></div>
      </form>
    </section>

    <footer><div class="brand"><span class="brand-mark">L</span><span><strong>LUXURY</strong><small>AUTO SERVICE</small></span></div><p>Искусство заботы об автомобиле.</p><span>© 2025 Luxury-Auto</span></footer>
  </main>
`

const form = document.querySelector('#lead-form')
const budget = document.querySelector('#budget')
const budgetOutput = document.querySelector('#budget-output')
const budgetMin = document.querySelector('#budget-min')
const budgetMax = document.querySelector('#budget-max')
const serviceSelect = document.querySelector('#service-select')
const serviceGrid = document.querySelector('.service-grid')
const status = document.querySelector('.form-status')

function record(type, details = {}) {
  events.push({ type, at: new Date().toISOString(), ...details })
}

function formatBudget(value) {
  return `${Number(value).toLocaleString('ru-RU')} ₽`
}

function escapeHtml(value = '') {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;')
}

function applyServiceSettings(service) {
  const min = Number(service.budget_min)
  const max = Number(service.budget_max)
  const step = Number(service.budget_step)
  const value = Math.min(max, Math.max(min, Math.round((min + max) / 2 / step) * step))

  budget.min = min
  budget.max = max
  budget.step = step
  budget.value = value
  budgetOutput.textContent = formatBudget(value)
  budgetMin.textContent = `от ${formatBudget(min)}`
  budgetMax.textContent = `до ${formatBudget(max)}`
}

function renderServices() {
  serviceGrid.innerHTML = services.map((service, index) => `
    <article class="service-card" data-service-id="${service.id}">
      <span class="service-number">${String(index + 1).padStart(2, '0')}</span>
      <h3>${escapeHtml(service.service_name)}</h3>
      <p>${escapeHtml(service.service_description || '')}</p>
      <a href="#request" aria-label="Выбрать услугу ${escapeHtml(service.service_name)}">Подробнее <span>↗</span></a>
    </article>
  `).join('')

  serviceSelect.innerHTML = services.map((service) => `
    <option value="${service.id}">${escapeHtml(service.service_name)}</option>
  `).join('')

  if (services.length > 0) applyServiceSettings(services[0])
}

async function loadServices() {
  try {
    const response = await fetch('/api/admin-settings')
    if (!response.ok) throw new Error('services_request_failed')

    services = (await response.json()).filter((service) => service.is_active)
    if (services.length === 0) throw new Error('no_active_services')

    renderServices()
    record('services_loaded', { count: services.length })
  } catch (error) {
    serviceGrid.innerHTML = '<p class="form-status error">Не удалось загрузить список услуг. Обновите страницу и попробуйте ещё раз.</p>'
    serviceSelect.innerHTML = '<option value="">Услуги временно недоступны</option>'
    serviceSelect.disabled = true
    budget.disabled = true
    record('services_load_error')
  }
}

serviceSelect.addEventListener('change', () => {
  const service = services.find((item) => String(item.id) === serviceSelect.value)
  if (service) {
    applyServiceSettings(service)
    record('service_change', { service_id: service.id })
  }
})

serviceGrid.addEventListener('click', (event) => {
  const card = event.target.closest('[data-service-id]')
  if (!card) return

  const service = services.find((item) => String(item.id) === card.dataset.serviceId)
  if (service) {
    serviceSelect.value = String(service.id)
    applyServiceSettings(service)
    record('service_select', { service_id: service.id })
  }
})

budget.addEventListener('input', () => {
  budgetOutput.value = formatBudget(budget.value)
  budgetOutput.textContent = formatBudget(budget.value)
  record('field_change', { field: 'budget' })
})

form.addEventListener('focusin', (event) => {
  if (!formStarted && event.target.matches('input, select, textarea')) {
    formStarted = true
    record('form_start')
  }
})

document.addEventListener('click', (event) => {
  if (event.target.closest('a, button, select, input')) clickCount += 1
})

document.addEventListener('mousemove', () => {
  const now = Date.now()
  if (now - lastMoveAt > 1800) cursorPauses += 1
  lastMoveAt = now
})

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) returnVisits += 1
})

form.addEventListener('submit', async (event) => {
  event.preventDefault()
  const submitButton = form.querySelector('button[type="submit"]')
  const data = Object.fromEntries(new FormData(form))
  const selectedService = services.find((service) => String(service.id) === serviceSelect.value)
  data.business_niche = 'Luxury-Auto'
  data.task_volume = selectedService?.service_name || data.task_volume
  data.product_interest = selectedService?.service_name || data.product_interest
  data.analytics = {
    time_on_page_seconds: Math.round((Date.now() - startedAt) / 1000),
    button_clicks: clickCount,
    cursor_pauses: cursorPauses,
    return_visits: returnVisits,
    events: [...events, { type: 'submit_attempt', at: new Date().toISOString() }],
    technical_info: { user_agent: navigator.userAgent, language: navigator.language, screen: `${window.innerWidth}x${window.innerHeight}`, referrer: document.referrer || 'direct' },
  }
  submitButton.disabled = true
  submitButton.innerHTML = 'Отправляем...'
  status.className = 'form-status'
  status.textContent = ''
  try {
    const response = await fetch('/api/leads', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
    if (!response.ok) throw new Error('request_failed')
    const result = await response.json()
    record('submit_success', { lead_id: result.id })
    status.className = 'form-status success'
    status.textContent = `Заявка №${result.id} принята. Мы свяжемся с вами в ближайшее время.`
    form.reset()
    if (services.length > 0) {
      serviceSelect.value = String(services[0].id)
      applyServiceSettings(services[0])
    }
  } catch (error) {
    record('submit_error')
    status.className = 'form-status error'
    status.textContent = 'Не удалось отправить заявку. Проверьте соединение и попробуйте ещё раз.'
  } finally {
    submitButton.disabled = false
    submitButton.innerHTML = 'Отправить заявку <span>↗</span>'
  }
})

loadServices()
