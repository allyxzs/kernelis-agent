FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KERNELIS_POLICY=safe

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENTRYPOINT ["kernelis"]
CMD ["doctor"]
