# Дизайн: Сбор поведенческих метрик и хитмэп

## Модель данных

Таблица `behavior_metrics` (SQLAlchemy, `app/models/behavior_metric.py`):

| Поле | Тип | Назначение |
|---|---|---|
| `id` | PK int | идентификатор |
| `session_id` | String(64), unique, index | UUID визита с клиента, ключ upsert |
| `application_id` | int, default 0 | всегда 0 по требованию |
| `time_on_page` | int | секунды на странице (накопительно) |
| `buttons_clicked` | Text | JSON-строка `{"кнопка": счётчик}` |
| `cursor_positions` | Text | JSON-строка `[{"x": %, "y": %}]` |
| `return_frequency` | int, default 0 | всегда 0 по требованию |
| `created_at` / `updated_at` | TimestampMixin | время первого и последнего запроса визита |

Таблица создаётся через `Base.metadata.create_all` при старте backend (как остальные).

## Upsert вместо insert

Клиент шлёт POST раз в секунду с накопительными данными. Чтобы не писать по строке в секунду:

- `BehaviorMetricCRUD.upsert(db, data)`: ищет строку по `session_id`;
- найдена — обновляет `time_on_page`, `buttons_clicked`, `cursor_positions`, `return_frequency`;
- не найдена — создаёт.

Итог: одна строка = один визит. `updated_at` — момент последнего «пульса» визита.

## API

### POST /api/behavior-metrics/ (публичный)

Pydantic-схема `BehaviorMetricCreate` (`app/schemas/behavior_metrics.py`):

- `session_id: str` (8–64 символа);
- `application_id: int = 0`;
- `time_on_page: int >= 0`;
- `buttons_clicked: str = ""`;
- `cursor_positions: str = ""`;
- `return_frequency: int = 0`.

Ответ: `200 {"status": "ok"}`. Ошибки валидации — стандартные 422.

### GET /api/behavior-metrics/stats (JWT)

Ответ:

```json
{
  "periods": {
    "day":   {"avg_time_on_page": 42, "max_time_on_page": 130, "sessions": 3},
    "week":  {"avg_time_on_page": 55, "max_time_on_page": 402, "sessions": 12},
    "month": {"avg_time_on_page": 61, "max_time_on_page": 900, "sessions": 47}
  },
  "total_sessions": 47,
  "cursor_positions": [{"x": 12.5, "y": 40.0}]
}
```

- периоды считаются по `updated_at` (последний пульс визита): день = 24 часа, неделя = 7 дней, месяц = 30 дней;
- `avg`/`max`/`count` — SQL-агрегаты `func.avg`, `func.max`, `func.count`;
- `cursor_positions` — точки из последних 1000 визитов (по `updated_at` desc), JSON каждой строки безопасно парсится, битые строки пропускаются;
- точек может быть много (1/сек), поэтому клиент рисует их полупрозрачными кругами с малой альфой — наложение даёт эффект тепла без предварительной кластеризации.

## Клиент: сбор метрик (frontend/src/metrics.js)

Модуль подключается из `main.js`, работает автономно:

- `session_id` — `crypto.randomUUID()` при загрузке страницы;
- `time_on_page` — `Math.round((Date.now() - startedAt) / 1000)`;
- клики: слушатель `click` на `document`, цель `closest('button, a, select, input, textarea')`, метка — `aria-label` или видимый текст (обрезка 60 символов), счётчик по метке;
- курсор: слушатель `mousemove` запоминает последнюю позицию; раз в секунду в массив добавляется точка в процентах окна: `x / innerWidth * 100`, `y / innerHeight * 100`;
- раз в секунду `fetch POST /api/behavior-metrics/` с полным накопительным состоянием; ошибки сети глушатся (метрики не должны ломать сайт).

## Клиент: модальное окно статистики (frontend/src/admin.js)

- кнопка «Статистика» в `header-actions` админ-панели;
- полноэкранное модальное окно (`position: fixed`, закрытие по кнопке и клику по фону);
- три карточки: «За день / За неделю / За месяц» — среднее время, максимальное время (формат `мм:сс`), число визитов;
- canvas-хитмэп: точки из `cursor_positions` (проценты 0–100) масштабируются в размер canvas; каждая точка — радиальный градиент-круг золотисто-оранжевого цвета с альфой ~0.06 и радиусом ~22px; плотные области перекрываются и «теплеют»;
- при пустых данных — заглушки «Нет данных».

## Риски

- объём `cursor_positions` растёт на 1 точку в секунду визита (за 10 минут ~600 точек, ~15 КБ JSON) — приемлемо для учебного контура;
- скролл не учитывается: точка привязана к видимой области окна, хитмэп показывает «экран», а не всю страницу — осознанное упрощение;
- `application_id` и `return_frequency` — заглушки под будущие интеграции, всегда 0.

## Верификация

- `python -m compileall`, `python -m pytest`;
- curl: публичный POST с двумя разными `session_id` и повторный POST того же `session_id` → в таблице 2 строки, а не 3;
- `GET /api/behavior-metrics/stats` без токена → 401, с токеном → агрегаты совпадают с записанным;
- `/` и `/admin/` через Nginx: страница отвечает, кнопка статистики открывает окно, хитмэп рисуется.
