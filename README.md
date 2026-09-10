# TeamFinder

Веб-платформа, где разработчики, дизайнеры и другие специалисты находят команду для pet-проектов: публикуют идеи, откликаются на чужие и собирают состав по навыкам.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

## Возможности

- Регистрация и вход по email, смена пароля, кастомная модель пользователя
- Профили с аватаром, контактами, GitHub и блоком «О себе»
- Автогенерация аватара по инициалам, если пользователь не загрузил свой
- Навыки в профиле: добавление и удаление без перезагрузки страницы, автодополнение и создание нового тега
- Фильтрация участников по навыку
- Карточки pet-проектов: создание, редактирование, статус «открыт / закрыт», участники
- Присоединение к проекту и завершение проекта автором
- Публичные страницы проекта и профиля, копирование ссылки
- Пагинация списков (12 элементов на страницу)
- Django Admin для модерации пользователей и проектов

## Стек

| Слой | Технологии |
|------|------------|
| Backend | Django 5.2, Python |
| База данных | PostgreSQL 16 |
| Инфраструктура | Docker Compose |
| Медиа | Pillow (аватары) |
| Конфиг | python-decouple (`.env`) |

## Быстрый старт

### Требования

- Python 3.12+
- Docker Desktop (для PostgreSQL)

### 1. Клонирование и окружение

```bash
git clone https://github.com/diedjest/team-finder-ad.git
cd team-finder-ad

python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Переменные окружения

Скопируйте пример и заполните значения:

```bash
cp .env_example .env
```

| Переменная | Назначение |
|------------|------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django |
| `DJANGO_DEBUG` | Режим отладки (`True` при локальной разработке) |
| `POSTGRES_DB` | Имя базы |
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль |
| `POSTGRES_HOST` | Хост (`localhost` при локальном Docker) |
| `POSTGRES_PORT` | Порт (`5436` в `docker-compose.yml`) |
| `TASK_VERSION` | Набор шаблонов (`2` — текущий UI) |

Секретный ключ можно сгенерировать так:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. База данных

```bash
docker compose up -d
python manage.py migrate
python manage.py createsuperuser
```

Порт PostgreSQL снаружи — `5436`, чтобы не конфликтовать с локальным `5432`.

### 4. Запуск

```bash
python manage.py runserver
```

Приложение: [http://localhost:8000](http://localhost:8000)

Остановить БД:

```bash
docker compose down
```

## Структура проекта

```
team-finder-ad/
├── team_finder/      # настройки Django, URL, WSGI/ASGI
├── users/            # пользователи, навыки, аутентификация
├── projects/         # проекты и участие в команде
├── templates_var2/  # HTML-шаблоны
├── static/           # CSS и JS
├── docker-compose.yml
└── requirements.txt
```

## Что можно посмотреть в коде

- Кастомный `User` с логином по email (`users/models.py`)
- AJAX-эндпоинты навыков (`users/views.py`, `static/js/skills.js`)
- Модель проекта и участие через M2M (`projects/models.py`)

## Лицензия

Учебный / портфолио-проект. Код можно изучать и форкать без ограничений, если не указано иное.
