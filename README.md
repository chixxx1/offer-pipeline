# OfferPipeline

Сервис для поиска и трекинга вакансий: парсинг вакансий с hh.ru, умный подбор по профилю и навыкам, трекинг откликов на канбан-доске.

## Основные возможности

- **Парсинг и поиск вакансий с hh.ru** — поиск по запросу с фильтрами, защита от капчи (scrapling + impersonate='chrome'), подгрузка полного описания вакансии по требованию.
- **Расширенный профиль кандидата** — навыки, опыт работы, образование, несколько вариантов профиля под разные специализации, хранение файлов резюме (PDF/DOCX).
- **Канбан-доска откликов** — Drag & Drop по колонкам статусов, заметки, история изменений, дедлайны.
- **Рекомендации по профилю** — персонализированный список вакансий с фильтрами по варианту профиля, только новые.

## Технологический стек

### Backend
- Python 3.14 (`requires-python = ">=3.12"`)
- Django 6.1 + Django REST Framework 3.18
- djangorestframework-simplejwt (JWT-аутентификация)
- django-cors-headers (CORS)
- scrapling[fetchers] (Fetcher + `impersonate='chrome'`) — парсинг hh.ru
- requests — HTTP-клиент
- `uv` — менеджер зависимостей (`pyproject.toml` + `uv.lock`)
- SQLite — база данных

### Frontend
- Vue 3.5 (Composition API, `<script setup>` SFC)
- Vite 8 — dev-сервер и сборка
- Pinia 4 — управление состоянием
- Vue Router 4 — навигация
- Axios — HTTP-запросы (токен через `localStorage` + заголовок `Authorization: Bearer`)
- vuedraggable — Drag & Drop для канбан-доски

## Структура проекта

```
offer-pipeline/
├── README.md
├── AGENTS.md
├── backend/                 # Django-проект
│   ├── pyproject.toml       # Зависимости и uv-конфигурация
│   ├── uv.lock
│   ├── manage.py
│   ├── db.sqlite3           # Локальная БД
│   ├── config/              # Конфигурация Django (settings, urls, asgi, wsgi)
│   ├── apps/
│   │   ├── parsing/         # Парсинг hh.ru
│   │   │   ├── services/hh_parser.py
│   │   │   ├── views.py
│   │   │   └── management/commands/parse_hh_scraping.py
│   │   ├── tracker/         # Ядро: Vacancy, Application, VacancyRecommendation
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services/matching.py
│   │   │   └── management/commands/check_recommendations.py
│   │   └── users/           # Пользователь и профиль (навыки, опыт, образование, резюме)
│   └── apps/*/migrations/   # Миграции Django
└── frontend/                # Vue 3 SPA (Vite)
    ├── package.json
    ├── vite.config.js       # Прокси
    ├── index.html
    └── src/
        ├── main.js          # Точка входа, авторизация через axios
        ├── App.vue
        ├── router/          # Vue Router (маршруты SPA)
        ├── views/           # Страницы: BoardView, SearchView, LoginView, RegisterView, ProfileView
        ├── components/      # Компоненты: KanbanBoard, VacancyList, VacancySearchCard, и др.
        ├── stores/          # Pinia-сторы: auth, search, tracker, applications, recommendations
        └── utils/           # Утилиты (vacancyFormatters)
```

## Быстрый старт

Все команды backend выполняются из директории `backend/`, frontend — из `frontend/`.

### Backend

1. Установить зависимости:
   ```bash
   cd backend
   uv sync
   uv run scrapling install
   ```

2. Применить миграции:
   ```bash
   uv run python manage.py migrate
   ```

3. Запустить dev-сервер (порт 8000):
   ```bash
   uv run python manage.py runserver
   ```

4. (Опционально) Создать суперпользователя для админки:
   ```bash
   uv run python manage.py createsuperuser
   ```
   Админка: `http://localhost:8000/admin/`

### Frontend

1. Установить зависимости:
   ```bash
   cd frontend
   npm install
   ```

2. Запустить dev-сервер (порт 5173):
   ```bash
   npm run dev
   ```

Приложение будет доступно по адресу `http://localhost:5173`. Запросы `/api/*` автоматически проксируются на Django (`http://localhost:8000`).


### Маршруты API
Все эндпоинты под префиксом `/api/`:
- `POST /api/auth/register/` — регистрация
- `POST /api/auth/login/` — получение JWT-токенов
- `POST /api/auth/refresh/` — обновление access-токена
- `GET /api/auth/me/` — текущий пользователь
- `GET /api/vacancies/search/` — поиск вакансий hh.ru
- `GET /api/vacancies/<id>/full-description/` — полное описание вакансии
- `GET /api/vacancies/`, `POST /api/vacancies/` — вакансии (ViewSet)
- `GET /api/applications/`, `POST /api/applications/` — отклики (ViewSet)
- `GET /api/recommendations/` — рекомендации (фильтры: `variant_id`, `only_new`, `min_score`)
- `POST /api/recommendations/sync/` — синхронизация рекомендаций
- `POST /api/recommendations/<id>/dismiss/` — скрыть рекомендацию
- `POST /api/recommendations/mark-seen/` — отметить просмотренными
- `GET /api/profile/`, `PATCH /api/profile/` — профиль пользователя
- `GET /api/skills/` — список навыков (автодополнение)