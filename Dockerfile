# ───────────── Stage 1: Build CSS with Tailwind ─────────────
FROM node:18-alpine AS tailwind-builder

# Set working directory
WORKDIR /app

# Install Tailwind
COPY package*.json ./
RUN npm install

# Copy Tailwind input source
COPY ./app/static/css ./app/static/css

# Run Tailwind build
RUN npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css

# ───────────── Stage 2: Python backend ─────────────
FROM python:3.10-slim

WORKDIR /app

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Bring over the compiled CSS
COPY --from=tailwind-builder /app/app/static/css/output.css ./app/static/css/output.css

# Entrypoint for Render
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "wsgi:app"]
