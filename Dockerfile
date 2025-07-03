# Stage 1: Build frontend assets
# Use a slim Node.js image to build our static assets. This keeps the build
# environment separate from our final, smaller production image.
FROM node:18-slim as frontend-builder

# Set the working directory inside the container
WORKDIR /app

# Copy package management files first to leverage Docker layer caching.
# This layer will only be rebuilt if package.json or package-lock.json changes.
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application source code needed for the build.
# This includes the tailwind config and the input CSS file.
COPY . .

# Build the production CSS file.
# This runs the "build" script defined in your package.json.
RUN npm run build


# Stage 2: Setup the final Python application
# Use a slim Python image for a smaller final container size.
FROM python:3.10-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_CONFIG prod

# Create a non-root user and group for security. Running as a non-root user
# is a critical security best practice for containers.
RUN addgroup --system nonroot && adduser --system --ingroup nonroot nonroot

# Set the working directory
WORKDIR /app

# Copy requirements file and install Python dependencies as the root user
# before switching to the non-root user.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container, changing ownership to the non-root user.
COPY --chown=nonroot:nonroot . .

# Copy the built static assets from the frontend-builder stage, also changing ownership.
COPY --from=frontend-builder --chown=nonroot:nonroot /app/app/static/css/output.css ./app/static/css/output.css

# Expose the port the app will run on. Render will map this to the public internet.
# While Render provides $PORT, exposing a default is good practice.
EXPOSE 5000

# Add a healthcheck to ensure the application is running correctly.
# Render uses its own health check, but this is good practice for portability.
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Switch to the non-root user for running the application
USER nonroot

# The command to run the application.
# Gunicorn is a production-ready WSGI server.
# Render will automatically provide and substitute the $PORT variable.
CMD gunicorn --bind 0.0.0.0:$PORT wsgi:app
