# --------------------------------------------------------------------------------
# Stage 1 – Frontend build
# --------------------------------------------------------------------------------
# Use a minimal Node image for faster cold‑starts and lower attack surface.
FROM node:18-slim AS frontend-builder

# Ensure non‑interactive apt for potential extra tooling (can be removed if unused)
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Leverage Docker layer caching: install deps before copying the whole context.
COPY package*.json ./
RUN npm ci --omit=dev  # reproducible installs; skips devDeps for prod build

# Copy application source *after* dependencies to maximise cache hits.
COPY . .

# Build Tailwind / Vite / React static assets (relies on "build" script).
RUN npm run build


# --------------------------------------------------------------------------------
# Stage 2 – Python backend runtime
# --------------------------------------------------------------------------------
FROM python:3.10-slim AS runtime

# -------------------------
# Environment hardening
# -------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1         \
    FLASK_CONFIG=prod          \
    # Add the non‑root user's local bin to the PATH for pip‑installed CLIs
    PATH="/home/nonroot/.local/bin:${PATH}"

WORKDIR /app

# -------------------------
# Security: create dedicated user
# -------------------------
RUN addgroup --system nonroot && \
    adduser  --system --ingroup nonroot nonroot

# -------------------------
# Python dependencies
# -------------------------
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre‑create instance folder with correct ownership before dropping privileges.
RUN mkdir /app/instance && \
    chown nonroot:nonroot /app/instance

# -------------------------
# Application source & static assets
# -------------------------
# Copy backend source code with proper ownership to avoid runtime permission issues.
COPY --chown=nonroot:nonroot . .

# Bring in built CSS bundle from Stage 1; adjust paths if your build dir differs.
COPY --from=frontend-builder --chown=nonroot:nonroot /app/app/static/css/output.css ./app/static/css/output.css

# Switch to the least‑privileged user for execution.
USER nonroot

# -------------------------
# Entrypoint (override in render.yaml if needed)
# -------------------------
# CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-8000}", "wsgi:app"]
