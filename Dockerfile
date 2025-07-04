# --------------------------------------------------------------------------------
# Stage 1 – Frontend build
# --------------------------------------------------------------------------------
FROM node:18-slim AS frontend-builder

# Install runtime + dev dependencies required for the asset pipeline (e.g. Tailwind)
WORKDIR /app

# Copy package manifests first so we can leverage Docker layer‑cache
COPY package*.json ./
# Use deterministic installs; **do NOT omit dev dependencies** because Tailwind is
# typically defined as a devDependency and is required at build‑time.
RUN npm ci

# Copy the remainder of the source and build the static assets.
COPY . .
# Runs whatever `"build"` targets you defined (e.g., Tailwind, Vite, React).
RUN npm run build

# --------------------------------------------------------------------------------
# Stage 2 – Python runtime
# --------------------------------------------------------------------------------
FROM python:3.10-slim

WORKDIR /app

# Basic runtime env flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_CONFIG=prod \
    PATH="/home/nonroot/.local/bin:${PATH}"

# Create a non‑privileged user
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime directories + permissions before switching to non‑root
RUN mkdir /app/instance && chown nonroot:nonroot /app/instance

# Copy application code and pre‑built static assets
COPY --chown=nonroot:nonroot . .
COPY --from=frontend-builder --chown=nonroot:nonroot /app/app/static/css/output.css ./app/static/css/output.css

USER nonroot

# Healthcheck keeps Render/K8s happy and catches crash‑loops early
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:5000/healthz || exit 1
