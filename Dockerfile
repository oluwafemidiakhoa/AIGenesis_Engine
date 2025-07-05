# --------------------------------------------------------------------------------
# Dockerfile — multi-stage build for frontend & Python backend
# --------------------------------------------------------------------------------

# Stage 1 — Frontend build
FROM node:18-slim AS frontend-builder
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Install all deps (including devDeps for Tailwind/Vite)
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npm run build

# Stage 2 — Python runtime
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_CONFIG=prod

WORKDIR /app

# Create non-root user
RUN addgroup --system nonroot \
 && adduser --system --ingroup nonroot nonroot

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Prepare instance folder
RUN mkdir /app/instance \
 && chown nonroot:nonroot /app/instance

# Copy app code + built assets
COPY --chown=nonroot:nonroot . .
COPY --from=frontend-builder --chown=nonroot:nonroot \
    /app/app/static/css/output.css \
    ./app/static/css/output.css

USER nonroot

# Healthcheck for /healthz
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget --quiet --spider http://localhost:${PORT:-5000}/healthz || exit 1

# Entrypoint (can be overridden by Render’s Start Command)
CMD ["bash", "-lc", "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT wsgi:app"]
