# Stage 1: Build frontend assets
FROM node:18-slim as frontend-builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the frontend source code
COPY . .

# Build the CSS. This runs the "build" script from your package.json
RUN npm run build

# Stage 2: Setup the Python application
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_CONFIG prod

# Create a non-root user and group for security
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create the instance folder and set permissions before switching user
RUN mkdir /app/instance
RUN chown nonroot:nonroot /app/instance

# Copy the application code
COPY --chown=nonroot:nonroot . .

# Copy the built static assets from the previous stage
COPY --from=frontend-builder --chown=nonroot:nonroot /app/app/static/css/output.css ./app/static/css/output.css

# Expose the port the app will run on
EXPOSE 5000

# Switch to the non-root user for running the application
USER nonroot

# The command to run the application (Render will use the PORT environment variable)
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
