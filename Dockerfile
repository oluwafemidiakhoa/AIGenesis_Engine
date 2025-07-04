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

# Add the non-root user's local bin to the PATH
ENV PATH="/home/nonroot/.local/bin:${PATH}"

# Create a non-root user and group for security
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create the instance folder and set permissions before switching user
RUN mkdir /app/instance
RUN chown nonroot:nonroot /app/instance

# Copy the application code and entrypoint script
COPY --chown=nonroot:nonroot . .
# Ensure the entrypoint script has Unix line endings and is executable.
# This prevents issues when developing on Windows.
RUN sed -i 's/\r$//' entrypoint.sh
RUN chmod +x entrypoint.sh

# Copy the built static assets from the previous stage
COPY --from=frontend-builder --chown=nonroot:nonroot /app/app/static/css/output.css ./app/static/css/output.css

# Switch to the non-root user for running the application
USER nonroot

# The entrypoint script will run migrations (if applicable) and then execute the CMD
ENTRYPOINT ["./entrypoint.sh"]

CMD ["/bin/sh", "-c", "gunicorn --bind 0.0.0.0:$PORT wsgi:app"]
