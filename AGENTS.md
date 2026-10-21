c# Project Rules & Architecture Context

## 1. Project Overview

- **Name & Purpose:** OfferPipeline — сервис для поиска и трекинга вакансий: парсинг вакансий с hh.ru, канбан-доска откликов (applications), профиль пользователя.
- **Tech Stack:**
  - **Backend:** Python 3.14 (см. `backend/.python-version`, `requires-python = ">=3.12"`), Django 6.1 + Django REST Framework 3.18, аутентификация — djangorestframework-simplejwt (JWT), CORS — django-cors-headers, парсинг — scrapling[fetchers] (Fetcher + impersonate='chrome'), HTTP-клиент — requests. Менеджер зависимостей — **uv** (`pyproject.toml` + `uv.lock`). БД — SQLite (`backend/db.sqlite3`).
  - **Frontend:** Vue 3.5 (`<script setup>` SFC), Vite 8, Pinia 4, Vue Router 4, axios, vuedraggable. В dev-режиме Vite проксирует `/api` на `http://localhost:8000` (см. `frontend/vite.config.js`).
- **Entry Points:**
  - Backend: `backend/manage.py` (settings — `config.settings`); dev-сервер: `uv run python manage.py runserver`.
  - Frontend: `frontend/index.html` → `src/main.js` → `src/App.vue`; dev-сервер: `npm run dev`.
  - CLI-парсер hh.ru: `backend/apps/parsing/management/commands/parse_hh_scraping.py` и standalone-скрипт `backend/parse_hh_scrapling.py`.

## 2. Directory Structure & Architecture

- **Ключевые папки:**
  - `backend/` — Django-проект (Python 3.14, управление зависимостями через uv).
    - `backend/config/` — конфигурация проекта: `settings.py`, `urls.py` (корневые URL), `asgi.py`, `wsgi.py`.
    - `backend/apps/parsing/` — приложение парсинга hh.ru: `services/hh_parser.py` (search_vacancies, fetch_vacancy_description, save_vacancy и др.), `views.py` (VacanciesSearchView, VacancyFullDescriptionView), `management/commands/parse_hh_scraping.py` (CLI-команда `parse_hh_scraping`).
    - `backend/apps/tracker/` — основное приложение: модели Vacancy/Application, serializers, ViewSet'ы (VacancyViewSet, ApplicationViewSet), регистрация через DRF DefaultRouter в `urls.py` (`/api/vacancies/`, `/api/applications/`), RegisterView/MeView.
    - `backend/apps/users/` — пользовательская модель и профиль.
    - `backend/db.sqlite3` — локальная БД (не коммитить дампы/секреты).
  - `frontend/` — Vue 3 SPA (Vite).
    - `frontend/src/views/` — страницы: SearchView, BoardView, LoginView, RegisterView, ProfileView.
    - `frontend/src/components/` — KanbanBoard, VacancyList, VacancySearchCard, FiltersPanel, ApplicationDetailModal.
    - `frontend/src/stores/` — Pinia-сторы: auth, search, tracker, applications.
    - `frontend/src/router/index.js` — маршруты SPA; `src/utils/vacancyFormatters.js` — утилиты форматирования.
- **Архитектурные паттерны:**
  - Backend: слоистая структура Django — models → services (бизнес-логика парсинга в `apps/parsing/services/`) → serializers → DRF views/viewsets. Все API под префиксом `/api/` (`config/urls.py`), JWT-аутентификация (SimpleJWT) задана в `REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`. БД — SQLite через стандартный ORM, миграции в `apps/*/migrations/`. Конфигурация — `config/settings.py` (SECRET_KEY/DEBUG пока захардкожены — учитывать комментарий «вынести в переменные окружения»).
  - Frontend: компонентная архитектура Vue 3 + Composition API (`<script setup>`), состояние — Pinia-сторы, запросы — axios (базовый `Authorization: Bearer` из localStorage ставится в `src/main.js`), навигация — Vue Router. В dev-режиме запросы `/api/*` проксируются на Django (`http://localhost:8000`).

## 3. Essential Commands (Build, Test, Lint)

Все backend-команды выполняются из `backend/`, frontend — из `frontend/`.

- **Install / Deps:**
  - Backend: `uv sync` (затем `uv run scrapling install` для fetcher'ов scrapling; при первом запуске — `uv run python manage.py migrate`)
  - Frontend: `npm install`
- **Build / Compile:**
  - Backend (проверка): `uv run python manage.py check` и `uv run python manage.py makemigrations --check --dry-run`
  - Frontend: `npm run build` (production-сборка), `npm run preview` (локальный просмотр сборки)
- **Run Tests:**
  - Backend: `uv run python manage.py test` (по приложению: `uv run python manage.py test apps.tracker`)
  - Frontend: тест-раннер не настроен (нет скрипта `test` в `package.json`)
- **Linter / Formatter:**
  - Backend: линтер/форматтер не настроен (нет ruff/flake8/black в зависимостях); базовая проверка синтаксиса — `uv run python -m compileall .`
  - Frontend: ESLint/Prettier не настроены; проверка — `npm run build` (Vite ловит синтаксические ошибки)
- **Dev-серверы и утилиты:**
  - Backend: `uv run python manage.py runserver` (порт 8000)
  - Frontend: `npm run dev` (Vite, порт 5173, прокси `/api` → :8000)
  - Админка: `uv run python manage.py createsuperuser`, затем `http://localhost:8000/admin/`
  - Парсинг hh.ru из CLI: `uv run python manage.py parse_hh_scraping`
## 4. Strict Coding & Tooling Rules

1. **Актуальность документации (No Hallucinations):**
   Перед использованием сторонних библиотек или новых возможностей языка всегда проверяй точные версии в файле зависимостей проекта. Если не уверен в сигнатуре функции или актуальном API — обязательно используй доступный инструмент веб-поиска (`pi-search` в Pi или `webfetch` в OpenCode), чтобы свериться с актуальной документацией.
2. **Точное редактирование файлов:**
   Никогда не редактируй файлы вслепую — сначала прочитай нужный участок. Если доступны хеш-якоря (`pi-hashline-edit-pro`), вноси правки строго через `replace`/`insert` по 4-символьным якорям; в противном случае используй штатный инструмент `edit` с точным совпадением контекста.
3. **Запрет на заглушки (No Slop):**
   Не оставляй в коде пустые реализации, комментарии вроде `// TODO: implement later` или `// ... остальной код без изменений`. Пиши полную рабочую логику, соблюдая стиль именования и обработки ошибок, принятый в соседних файлах проекта.
4. **Обязательная верификация перед ответом:**
   Задача НЕ считается выполненной, пока изменения не проверены. После правки кода обязательно запусти команду сборки/проверки типов или тесты через `bash`. Если сборка упала — исправь ошибки до того, как отчитаться о завершении.
5. **Стиль Backend (Django / Python 3.14):**
   - Python: современный синтаксис 3.12+ (PEP 604 union-типы `str | None`, f-строки, `pathlib.Path`). Аннотируй типами сигнатуры функций в сервисах (`apps/parsing/services/`), как в соседнем коде.
   - Django/DRF: бизнес-логика — в `services/` приложений, не во views; сериализация — только через serializers; маршруты — под префиксом `/api/`. Именование: модели в ед. числе (`Vacancy`, `Application`), viewset'ы/сериализаторы — `XViewSet`/`XSerializer`.
   - После изменения моделей всегда создавай и применяй миграции: `uv run python manage.py makemigrations && uv run python manage.py migrate`.
   - Парсинг — только через `scrapling.fetchers.Fetcher` с `impersonate='chrome'`; сеть и записи в БД не смешивай в одной функции (следуй разделению search/extract/save в `hh_parser.py`).
6. **Стиль Frontend (Vue 3 / Vite):**
   - SFC-компоненты — только с `<script setup>` (Composition API); логика запросов — в Pinia-сторах (`src/stores/`), компоненты не ходят в axios напрямую.
   - Форматирование — двойные кавычки, точки с запятой, отступ 2 пробела (как в существующих `.vue`/`.js` файлах); утилиты форматирования выноси в `src/utils/`.
   - Токен авторизации — только через localStorage (`accessToken`) и дефолтный заголовок axios, как в `src/main.js`; не дублируй логику авторизации в компонентах.
