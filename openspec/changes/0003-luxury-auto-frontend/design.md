# Технический дизайн

## Стек

- Vite и npm.
- Vanilla JavaScript без нового UI-фреймворка.
- CSS с custom properties, CSS Grid/Flexbox и media queries.
- Google Fonts: `Manrope` для округлого основного текста и `DM Sans` для интерфейсных элементов.

## Структура frontend

- `frontend/package.json` — npm-скрипты и зависимости сборки.
- `frontend/index.html` — точка входа Vite.
- `frontend/src/main.js` — разметка страницы, состояние формы, API-запрос и аналитика.
- `frontend/src/style.css` — визуальная система и адаптивные стили.
- `frontend/dist/` — результат `npm run build`, раздаваемый Nginx.

## Страница

1. Шапка с логотипом Luxury-Auto, навигационными якорями и кнопкой перехода к форме.
2. Hero-блок с обещанием индивидуального обслуживания автомобилей, золотым бейджем статуса и декоративными плавающими кругами.
3. Блок услуг: детейлинг, техническое обслуживание, подготовка к продаже и сезонная защита.
4. Форма заявки в несколько визуальных секций:
   - имя и фамилия;
   - контакт и способ связи;
   - марка/модель автомобиля;
   - тип обслуживания;
   - размер автомобиля через range-slider;
   - желаемый бюджет через range-slider;
   - желаемый срок;
   - роль клиента;
   - удобное время;
   - комментарий.
5. После формы — компактные преимущества сервиса.

## API-контракт

Форма отправляет `POST /api/leads` с полями backend `LeadCreate` и вложенным `analytics`:

- `first_name`, `last_name`, `contact_value`;
- `business_niche` со значением `Luxury-Auto`;
- `company_size` — выбранный размер автомобиля;
- `business_info` — марка/модель и дополнительные сведения;
- `task_volume` — тип обслуживания;
- `budget`, `result_deadline`, `customer_role`, `task_type`;
- `product_interest`, `contact_method`, `preferred_time`, `comments`;
- `analytics` с временем на странице, кликами, паузами курсора, возвратами, событиями и техническими данными.

Текстовые значения передаются на русском языке, а диапазоны сохраняются в виде строк, совместимых с текущей схемой backend.

## Аналитика

Frontend считает:

- время на странице;
- клики по интерактивным элементам;
- паузы курсора в hero/form area;
- количество возвратов во вкладку;
- массив событий `page_view`, `form_start`, `field_change`, `submit_attempt`, `submit_success` или `submit_error`;
- технические данные браузера, экрана, языка и referrer.

Персональные данные не записываются в analytics-события отдельно от основной заявки.

## Nginx и сборка

Compose монтирует `./frontend/dist` в `/usr/share/nginx/html:ro`. Сборка выполняется командой `npm run build`; если npm не установлен на хосте, одноразовый Compose-сервис `frontend-build` выполняет тот же npm/Vite build внутри Node-контейнера и копирует результат в `frontend/dist`. Nginx продолжает проксировать `/api/` в backend.

## Проверка

- `npm install`.
- `npm run build`.
- `docker compose config --quiet`.
- Проверка `GET /` через Nginx возвращает собранный HTML с Luxury-Auto.
- Проверка `GET /api/health` остаётся успешной.
- Ручная проверка формы отправляет заявку и показывает подтверждение.
