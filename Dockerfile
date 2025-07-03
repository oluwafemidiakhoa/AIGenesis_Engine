# ────────────────────────────────────────────────────────────────
# Stage 1: Build frontend assets
# ────────────────────────────────────────────────────────────────
FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Install frontend dependencies
COPY package*.json ./
RUN npm install

# Copy frontend source files
COPY . .

# Run build script (must be defined in package.json)
RUN npm run build

# ────────────────────────────────────────────────────────────────
# Stage 2: Setup and run Python app
# ────────────────────────────────────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Environment config
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source files
COPY . .

# Copy built frontend assets (only CSS here)
COPY --from=frontend-builder /app/app/static/css/output.css ./app/static/css/output.css

# Entrypoint (Render sets the $PORT env variable automatically)
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "wsgi:app"]
