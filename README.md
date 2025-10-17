# AI Agent: Google Drive Excel → API + QA

Небольшой сервис на FastAPI для чтения Excel‑файлов из Google Drive и ответа на вопросы по содержимому таблиц.

---

## Требования
- Docker и Docker Compose
- Сервисный аккаунт Google с доступом к чтению нужных файлов
- Файл ключей `credentials.json`

---

## Настройка
1. Получите `credentials.json` сервисного аккаунта Google и дайте ему доступ к нужным файлам/папкам.
2. Поместите `credentials.json` в корень проекта. В `docker-compose.yml` он монтируется в контейнер по пути `/app/credentials.json`.
3. При необходимости создайте `.env` (необязательно).

Переменные окружения:
- `GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json` (значение по умолчанию)

---

## Запуск
```bash
docker compose up --build
```
- API: `http://localhost:8000/docs`

---

## API
Откройте Swagger UI по адресу `http://localhost:8000/docs`.

Основные эндпоинты (примеры см. `test_main.http`):
- `GET /health` — проверка статуса сервиса
- `GET /drive/files` — список Excel‑файлов (поддерживает `?q=...`)
- `GET /drive/files/{file_id}` — скачивание и отображение размера файла
- `GET /table/read?file_id=...&sheet_name=` — список строк формата `{ tool_name, url }`
- `GET /table/cell?file_id=...&cell=A1` — значение конкретной ячейки
- `POST /qa/ask?file_id=...&question=...` — ответ на вопрос по данным таблицы

Требуемый формат таблицы: первые две колонки — «название инструмента» и «ссылка».

---

## Архитектура
- `routers/*` — HTTP‑слой (FastAPI роуты)
- `services/gdrive.py` — клиент Google Drive
- `services/table_reader.py` — чтение/нормализация Excel
- `services/qa_agent.py` — простая QA‑логика (фуззи‑поиск по названию)
- `app/main.py` — создание приложения, CORS, регистрация роутов

Все зависимости прокидываются через FastAPI `Depends(...)`.

---

## Безопасность и эксплуатация
- Сервисный аккаунт должен иметь доступ к файлам (расшарьте нужные элементы).
- В продакшене используйте секреты/хранилища секретов вместо прямого монтирования `credentials.json`.
- Учитывайте лимиты Google API и добавляйте ретраи при сетевых ошибках.