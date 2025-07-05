# --------------------------------------------------------------------------------
# Stage 1 — Frontend build
# --------------------------------------------------------------------------------
FROM node:18-slim AS frontend-builder

# Noninteractive (in case you need extra tooling later)
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Copy lockfiles first to leverage layer cache
COPY package*.json ./

# Install all deps (including devDeps so CLI tools like Tailwind/Vite are available)
RUN npm ci

# Copy source and build static assets
COPY . .
RUN npm run build

# --------------------------------------------------------------------------------
# Stage 2 — Python runtime
# --------------------------------------------------------------------------------
FROM python:3.10-slim

# Prevent Python from writing .pyc files & enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_CONFIG=prod

WORKDIR /app

# Create a non-root user for security
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Create instance folder (used by Flask) and set permissions
RUN mkdir /app/instance \
 && chown nonroot:nonroot /app/instance

# Copy application code and built frontend assets, set ownership to nonroot
COPY --chown=nonroot:nonroot . .
COPY --from=frontend-builder --chown=nonroot:nonroot \
    /app/app/static/css/output.css \
    ./app/static/css/output.css

# Switch to non-root user
USER nonroot

# Healthcheck so Docker (and Render, if it inspects) can verify readiness
HEALTHCHECK --interval=30s --timeout=5s \
  CMD wget --quiet --spider http://localhost:${PORT:-5000}/healthz || exit 1

# Note: Render overrides this via its Start Command (see render.yaml)
CMD ["bash", "-lc", "flask db upgrade && gunicorn --bind 0.0.0.0:$PORT wsgi:app"]
