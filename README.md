# 🔢 Numerology Bot — Система Светланы Беловой

Telegram-бот для нумеролога. Рассчитывает число по системе Беловой и психоматрицу Пифагора.

## Стек
- **Python 3.11+**
- **aiogram 3.x** — Telegram Bot framework
- **SQLAlchemy + asyncpg** — async ORM + PostgreSQL driver
- **Railway** — деплой и хостинг БД

---

## Структура проекта

```
numerology-bot/
├── main.py                  # Точка входа
├── config.py                # Конфигурация из .env
├── requirements.txt
├── Procfile                 # Для Railway
├── .env.example             # Шаблон переменных окружения
├── handlers/
│   ├── start.py             # /start команда
│   ├── birthdate.py         # Обработка даты рождения
│   └── booking.py           # Запись к специалисту (FSM)
├── database/
│   ├── models.py            # SQLAlchemy модели (User, Booking)
│   └── db.py                # Движок, сессии, CRUD
├── numerology/
│   ├── belova.py            # Расчёт числа по системе Беловой
│   └── psychomatrix.py      # Квадрат Пифагора
└── keyboards/
    └── menus.py             # Inline-клавиатуры
```

---

## Локальный запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/your-repo/numerology-bot.git
cd numerology-bot
```

### 2. Создай виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Настрой переменные окружения

```bash
cp .env.example .env
```

Заполни `.env`:
```
BOT_TOKEN=твой_токен_из_BotFather
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/numerology
SPECIALIST_USERNAME=@твой_username
ADMIN_ID=твой_telegram_id
```

### 4. Запусти бота

```bash
python main.py
```

---

## Деплой на Railway

### 1. Создай проект на Railway
- Зайди на [railway.app](https://railway.app)
- New Project → Deploy from GitHub repo

### 2. Добавь PostgreSQL
- В проекте: **+ New** → **Database** → **PostgreSQL**
- Railway автоматически создаст `DATABASE_URL`

### 3. Настрой переменные окружения
В Railway → твой сервис → **Variables**:
```
BOT_TOKEN=твой_токен
DATABASE_URL=<скопируй из PostgreSQL сервиса — поле DATABASE_URL, замени postgresql:// на postgresql+asyncpg://>
SPECIALIST_USERNAME=@username
ADMIN_ID=твой_id
```

⚠️ **Важно**: Railway даёт DATABASE_URL с префиксом `postgresql://` — нужно заменить на `postgresql+asyncpg://` для asyncpg.

### 4. Procfile уже настроен
```
worker: python main.py
```

Railway увидит его автоматически.

---

## База данных

### Таблица `users`
| Поле | Тип | Описание |
|------|-----|----------|
| id | BigInteger | Telegram User ID (PK) |
| username | String | @username |
| first_name | String | Имя |
| birth_date | String | DD.MM.YYYY |
| belova_number | Integer | Число по системе Беловой |
| psychomatrix | String | JSON с данными психоматрицы |
| is_paid | Boolean | Статус оплаты |
| created_at | DateTime | Дата регистрации |

### Таблица `bookings`
| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | PK |
| user_id | BigInteger | Telegram User ID |
| preferred_time | String | Удобное время |
| contact_info | String | Контакт пользователя |
| status | String | pending / confirmed / done |
| created_at | DateTime | Дата записи |

---

## Как узнать свой Telegram ID (ADMIN_ID)
Напиши боту [@userinfobot](https://t.me/userinfobot) — он пришлёт твой ID.
