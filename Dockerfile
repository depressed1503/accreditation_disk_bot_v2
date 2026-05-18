FROM python:3.12-slim

WORKDIR /app

# Устанавливаем uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости
RUN uv sync --frozen --no-cache

# Копируем код бота
COPY . .

# Запуск
CMD ["uv", "run", "main.py"]