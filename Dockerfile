FROM python:3.11

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl build-essential && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY . .

# Disable Poetry's virtualenv
ENV POETRY_VIRTUALENVS_CREATE=false

# Install dependencies
RUN poetry install --no-root --only main

# Load .env and run the app via a shell
CMD bash -c "export $(grep -v '^#' .env | xargs) && poetry run python -m src.api.server"
