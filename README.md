# World-Class SaaS Boilerplate

This is a production-ready, feature-rich SaaS boilerplate built with Flask, Stripe, Celery, and Docker. It provides a complete foundation for building and launching a modern subscription-based web application, saving you months of development time.

## Core Features

*   **Full User Authentication**: Secure registration, login, logout, and password reset flows.
*   **Stripe Subscriptions**: Complete integration with Stripe Checkout and the Stripe Customer Portal for managing subscriptions.
*   **Role-Based Access Control**:
    *   **Admin**: Access to a secure admin dashboard to manage users.
    *   **Subscribed User**: Access to premium, protected features.
    *   **Free User**: Access to public pages.
*   **Asynchronous Background Tasks**: Uses Celery and Redis to handle long-running tasks like sending emails without blocking web requests.
*   **Transactional Emails**: Sends welcome and password reset emails using Flask-Mail.
*   **Comprehensive Test Suite**: Includes a full suite of tests using `pytest` to ensure application reliability.
*   **Containerized Development**: Uses Docker and Docker Compose to create a reproducible, one-command development environment.
*   **Configuration Management**: Manages separate configurations for development, production, and testing.
*   **CLI for Admin Tasks**: Includes a command-line interface for creating admin users.

## Getting Started (Local Development)

Follow these steps to get the application running on your local machine.

### Prerequisites

*   Docker installed and running.
*   Git

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Create Your Environment File

Copy the example environment file and fill in your own secret keys and configuration.

```bash
cp .env.example .env
```

Now, open the `.env` file and add your credentials for Stripe, your email provider, and a new `SECRET_KEY`.

**Important**: For the Docker setup, the `DATABASE_URL` and `CELERY_BROKER_URL` should point to the service names defined in `docker-compose.yml` (e.g., `redis://redis:6379/0`).

### 3. Build and Run the Application

Use Docker Compose to build the images and start all the services (Flask Web App, Celery Worker, Redis).

```bash
docker-compose up --build
```

Your SaaS application is now running!

*   **Web Application**: http://localhost:5000
*   **Redis Commander (Optional, for viewing Redis data)**: http://localhost:8081

## Running Tests

To run the full test suite, execute the `pytest` command inside the `web` container:

```bash
docker-compose exec web pytest
```

## Available CLI Commands

You can use the `manage.py` script to perform administrative tasks.

### Create an Admin User

To create a user with administrative privileges, run the following command and replace the email and password with your desired credentials.

```bash
docker-compose exec web python manage.py create-admin admin@example.com your-strong-password
```

## Deployment

This boilerplate is designed to be easily deployable to any cloud provider that supports containers, such as Render, AWS, or DigitalOcean. The use of environment variables for configuration makes it straightforward to adapt to different hosting environments.

---

*This boilerplate was enhanced and reviewed by Gemini Code Assist.*"# AIGenesis_Engine" 
