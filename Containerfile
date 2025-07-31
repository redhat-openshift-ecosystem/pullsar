FROM node:24-slim AS frontend-builder

WORKDIR /app

RUN npm install -g pnpm@latest-10

COPY pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/

RUN pnpm install --frozen-lockfile

COPY apps/web/ ./apps/web/

RUN pnpm --filter web build


FROM python:3.13-slim AS python-builder

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libkrb5-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip install poetry

COPY apps/api/ ./apps/api/
COPY apps/worker/ ./apps/worker/

RUN python -m venv .venv
RUN . .venv/bin/activate && \
    cd apps/api && poetry install --no-root --without dev && \
    cd ../worker && poetry install --without dev


FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl jq && \
    curl -L https://github.com/operator-framework/operator-registry/releases/download/v1.33.0/linux-amd64-opm -o /usr/local/bin/opm && \
    chmod +x /usr/local/bin/opm && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


COPY --from=python-builder /app/.venv ./.venv

ENV PATH="/app/.venv/bin:$PATH"

RUN mkdir src

COPY apps/api/src/app ./src/app
COPY apps/worker/src/pullsar ./src/pullsar

ENV PYTHONPATH="/app/src"

COPY --from=frontend-builder /app/apps/web/dist ./static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
