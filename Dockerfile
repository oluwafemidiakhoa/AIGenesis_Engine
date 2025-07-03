# ────────────────────────────────
# Stage 1: Tailwind CSS Builder
# ────────────────────────────────
FROM node:18-alpine AS tailwind-builder

WORKDIR /app

# Install Tailwind
COPY package*.json ./
RUN npm install

# Copy Tailwind input + config
COPY ./app/static/css ./app/static/css
COPY tailwind.config.js ./

# Build the CSS using Tailwind CLI
RUN npx tailwindcss -i ./app/static/css/input.css -o ./app/static/css/output.css

# ────────────────────────────────
# Stage 2: Python Backend Setup
# ────────────────────────────────
FROM python:3.10-slim

WORKDIR /app

# Python env settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app (excluding .dockerignore contents)
COPY . .

# Inject the built Tailwind CSS from the Node stage
COPY --from=tailwind-builder /app/app/static/css/output.css ./app/static/css/output.css

# Expose the correct port (optional: for local debugging)
EXPOSE 8000

# Run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "wsgi:app"]
