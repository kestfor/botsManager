FROM python:3.11-slim

# Устанавливаем зависимости для установки Docker CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      ca-certificates \
      gnupg && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Docker CLI (версию можно подобрать под свой хост)
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-24.0.5.tgz \
  | tar xzv --strip 1 -C /usr/local/bin docker/docker

# Install Docker Compose v2 plugin
RUN mkdir -p /usr/local/lib/docker/cli-plugins \
 && curl -fsSL \
      https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 \
    -o /usr/local/lib/docker/cli-plugins/docker-compose \
 && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
WORKDIR ./bot

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot/ ./bot/
COPY config.json ./

# Точка входа
CMD ["python", "-m", "bot.main"]
