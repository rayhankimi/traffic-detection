FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/usr/local/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV PIP_DEFAULT_TIMEOUT=1000

# Install dependencies system
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    cmake \
    curl \
    ca-certificates \
    libffi-dev \
    libssl-dev \
    libopenblas-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    python3-wheel \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==1.5.1

WORKDIR /project

# Tahap ini hanya akan dijalankan ulang jika pyproject.toml atau poetry.lock berubah
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi

# Copy source code setelah install selesai
# Jika Anda hanya mengubah main.py, step di atas tidak akan dijalankan ulang karena cached
COPY app ./app

CMD ["poetry", "run", "python", "app/main.py"]

