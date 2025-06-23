# Requests Web Platform

## About The Project

This project is a comprehensive web platform built with Django to manage internal company requests. It's designed to streamline various operational processes, from data manipulation tasks to compliance and accounting reports. The platform provides a user-friendly interface for creating, tracking, and managing requests through their entire lifecycle, from submission to completion.

Originally deployed on Heroku, the platform has been migrated to **Fly.io** for more robust and flexible deployment options. It features a sophisticated, event-driven notification system that integrates with Email, Telegram, and Slack to keep all stakeholders informed in real-time.

### Key Features

* **User Authentication and Management:** Secure login, registration, and profile management for all users.
* **Role-Based Permissions:** Different user roles (requester, operator, QA agent, admin) with distinct permissions and access levels.
* **Multi-Type Request System:** Supports a wide variety of request types, each with its own specific form, data fields, and processing logic. Current types include:
    * Generating XML
    * Property Records
    * Unit Transfer
    * Deactivation/Toggle
    * Address Validation
    * Stripe Disputes
* **Complete Request Lifecycle:** A well-defined status system tracks requests from "Pending" through "In Progress," "Blocked," "Sent to QA," and finally to "Completed."
* **Advanced Notification System:**
    * **Event-Driven:** Notifications are triggered by specific events in the request lifecycle (e.g., creation, approval, rejection).
    * **Multi-Channel:** Supports sending notifications via **Email**, **Telegram**, and **Slack**.
    * **Conversation Threading:** Both Slack and Email notifications are grouped into conversation threads, keeping all communication for a single request organized.
    * **Configurable Toggles:** Administrators can enable or disable notifications for each specific event directly from the Django Admin panel.
* **File Uploads and Management:** Users can attach files to requests, which are stored securely using AWS S3.
* **Task Scheduling and Asynchronous Processing:** Utilizes `django-q` for running background tasks, such as sending notifications and processing scheduled requests, without blocking the main application.
* **Detailed Reporting:** Features dashboards and reports for accounting, operations, and compliance, providing valuable insights into the operational workload.
* **Dynamic Pricing Module:** A system to manage and calculate the cost of different operations, which can be viewed in cost summary reports.
* **Deployment Ready:** Configured for seamless deployment and continuous integration using **GitHub Actions** and **Fly.io**.

### Tech Stack

This project is built with a modern and robust set of technologies:

* **Backend:**
    * ![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)
    * ![Django](https://img.shields.io/badge/Django-5.2.1-092E20?style=for-the-badge&logo=django)
    * **Database:** ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?style=for-the-badge&logo=postgresql)
    * **Asynchronous Tasks:** `django-q`
* **Frontend:**
    * HTML5, CSS3
    * ![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap)
    * ![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript)
* **Deployment & Infrastructure:**
    * **Hosting:** ![Fly.io](https://img.shields.io/badge/Fly.io-764ABC?style=for-the-badge&logo=fly)
    * **CI/CD:** ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions)
    * **File Storage:** ![Amazon S3](https://img.shields.io/badge/Amazon_S3-569A31?style=for-the-badge&logo=amazon-s3)
* **External Services:**
    * **Notifications:** Slack, Telegram
    * **Monitoring/Logging:** Configured for standard logging output compatible with platforms like Fly.io.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Before you begin, ensure you have the following installed on your system:
* **Python 3.12.x**
* **PostgreSQL** (A local instance running)
* `git` for version control

### Local Installation

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/oscarmbv/requests-webpage.git](https://github.com/oscarmbv/requests-webpage.git)
    cd requests-webpage
    ```

2.  **Create and activate a virtual environment:**
    * This project uses `venv`, which is included with Python.
    ```sh
    # Create the virtual environment
    python -m venv .venv

    # Activate it
    # On Windows:
    .\.venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    * All required packages are listed in `requirements.txt`.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up the Environment Variables:**
    * Create a `.env` file in the root directory of the project. You can copy the example structure from the section below.
    * Fill in the required values, especially `SECRET_KEY` and `DATABASE_URL` for your local database.

5.  **Set up the Database:**
    * Make sure your local PostgreSQL server is running.
    * Create a new database and a user for the project.
    * Update the `DATABASE_URL` in your `.env` file with your database credentials.

6.  **Run Database Migrations:**
    * This command will create all the necessary tables in your database based on the models defined in `tasks/models.py`.
    ```sh
    python manage.py migrate
    ```

7.  **Create a Superuser:**
    * This will allow you to access the Django Admin panel.
    ```sh
    python manage.py createsuperuser
    ```
    * Follow the prompts to create your admin account.

8.  **Run the Development Servers:**
    * You need to run two processes in separate terminals:
    * **Terminal 1: Django Development Server**
        ```sh
        python manage.py runserver
        ```
        The application will be available at `http://127.0.0.1:8000/`.
    * **Terminal 2: Django-Q Cluster**
        * This process handles all asynchronous tasks like sending notifications. It must be running for notifications to work.
        ```sh
        python manage.py qcluster
        ```

## Environment Variables

The project uses a `.env` file in the root directory to manage environment variables. Create this file and add the following variables.

```sh
# .env.example

# Django Core Settings
SECRET_KEY='your-super-secret-key-here'
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database URL
# Format: postgres://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL='postgres://user:password@localhost:5432/requests_db'

# Email Configuration (using Mailgun as an example)
DEFAULT_FROM_EMAIL='Your Name <mail@your-domain.com>'
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.mailgun.org'
EMAIL_PORT=587
EMAIL_HOST_USER='postmaster@your-domain.com'
EMAIL_HOST_PASSWORD='your-mailgun-smtp-password'
EMAIL_USE_TLS=True

# AWS S3 for File Storage
AWS_ACCESS_KEY_ID='your-aws-access-key'
AWS_SECRET_ACCESS_KEY='your-aws-secret-key'
AWS_STORAGE_BUCKET_NAME='your-s3-bucket-name'
AWS_S3_REGION_NAME='us-east-1' # e.g., us-east-1
AWS_S3_CUSTOM_DOMAIN='your-s3-bucket-name.s3.amazonaws.com'

# Notification Services
TELEGRAM_BOT_TOKEN='your-telegram-bot-token'
TELEGRAM_DEFAULT_CHAT_ID='your-telegram-chat-id'
SLACK_WEBHOOK_URL='[https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX](https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX)'

# Domain Configuration
# Used for generating absolute URLs in emails and other services
SITE_DOMAIN='[http://127.0.0.1:8000](http://127.0.0.1:8000)' # For local development
# For production: SITE_DOMAIN='[https://your-app.fly.dev](https://your-app.fly.dev)'

```

### Variable Details

| Variable                  | Description                                                                                             | Example                                             |
| ------------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| `SECRET_KEY`              | A unique, unpredictable value used for cryptographic signing. **Keep this secret!** | `'random-chars-!@#$qwe_rty'`                        |
| `DEBUG`                   | Set to `True` for development (shows detailed error pages) and `False` for production.                   | `True`                                              |
| `DATABASE_URL`            | The connection string for the PostgreSQL database.                                                      | `'postgres://user:pass@host:port/dbname'`           |
| `DEFAULT_FROM_EMAIL`      | The default email address used for sending notifications.                                                 | `'WebApp <noreply@example.com>'`                    |
| `EMAIL_*`                 | SMTP credentials for your email sending service (e.g., Mailgun, SendGrid).                                | `...`                                               |
| `AWS_*`                   | Credentials for your AWS S3 bucket where user-uploaded files are stored.                               | `...`                                               |
| `TELEGRAM_BOT_TOKEN`      | The token for your Telegram Bot used for sending notifications.                                         | `'123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'`      |
| `TELEGRAM_DEFAULT_CHAT_ID`| The default chat ID where general Telegram notifications will be sent.                                    | `'-100123456789'`                                   |
| `SLACK_WEBHOOK_URL`       | The Incoming Webhook URL from your Slack App for sending notifications.                                 | `'https://hooks.slack.com/services/...'`            |
| `SITE_DOMAIN`             | The public base URL of the application. Crucial for creating correct links in emails and notifications. | `'https://your-app-name.fly.dev'`                     |

## Deployment on Fly.io

This project has been migrated from Heroku and is now fully configured for deployment on the [Fly.io](https://fly.io/) platform. The deployment process uses a Dockerfile, is managed by the `fly.toml` configuration file, and can be automated with GitHub Actions.

The `entrypoint.sh` script ensures that database migrations are applied automatically before the application server starts.

The application runs two main processes on Fly.io, as defined in `fly.toml`:
1.  `web`: The main Django application served via Gunicorn.
2.  `worker`: The `django-q` cluster for processing asynchronous tasks.

### First-Time Setup (`fly launch`)

To launch the application on Fly.io for the first time:

1.  **Install `flyctl`:** Follow the official instructions at [fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/).

2.  **Login to Fly.io:**
    ```sh
    fly auth login
    ```

3.  **Launch the App:**
    * Run the launch command from the project's root directory.
    ```sh
    fly launch
    ```
    * `flyctl` will detect the `fly.toml` file and use its settings.
    * When prompted, choose a unique name for your application and select a region.
    * Select **Yes** when asked to set up a PostgreSQL database.
    * Select **No** when asked to deploy immediately. We need to set secrets first.

4.  **Set Secrets:**
    * Secrets are Fly.io's version of environment variables. You must set all the variables listed in the `.env.example` section, but adapted for production.
    * The `DATABASE_URL` is set automatically when you create the PostgreSQL database.
    * For the other secrets, use the command `fly secrets set VAR_NAME="VALUE"`.
    ```sh
    # Example for setting the secret key and a production domain
    fly secrets set SECRET_KEY="your_production_super_secret_key"
    fly secrets set DEBUG="False"
    fly secrets set SITE_DOMAIN="[https://your-app-name.fly.dev](https://your-app-name.fly.dev)"
    
    # Set all other required secrets (AWS, EMAIL, SLACK, TELEGRAM, etc.)
    fly secrets set AWS_ACCESS_KEY_ID="xxx"
    # ...and so on for all variables
    ```

5.  **Deploy for the first time:**
    ```sh
    fly deploy
    ```

### Continuous Deployment with GitHub Actions

The repository includes a GitHub Actions workflow file at `.github/workflows/fly-deploy.yml` that automates deployment.

* **Trigger:** The workflow runs automatically on every `push` to the `main` branch.
* **Setup:** To enable this, you must configure a single secret in your GitHub repository's settings (`Settings` > `Secrets and variables` > `Actions`):
    * `FLY_API_TOKEN`: You can get your token by running `fly auth token` in your terminal.

### Manual Deployment

If you need to deploy manually at any time, simply run:
```sh
fly deploy
```

---

## Notification System

The platform features a powerful, event-driven notification system designed to keep users informed across multiple channels.

### Architecture

The system is built around event-specific functions in `tasks/notifications.py`. When a specific action occurs in the application (e.g., a request is approved), a corresponding function (e.g., `notify_request_approved`) is called asynchronously by `django-q`. This function then dispatches notifications to the configured and enabled channels.

### Features & Configuration

#### 1. Conversation Threading
To keep communications organized, all notifications related to a single request are grouped into conversation threads.
* **Slack:** Uses Slack's native threading feature. The timestamp of the first message is saved in the `UserRecordsRequest.slack_thread_ts` field.
* **Email:** Simulates threading by using standard email headers (`Message-ID`, `In-Reply-To`, `References`). The ID of the first email is saved in the `UserRecordsRequest.email_thread_id` field.

#### 2. User-Specific Mentions (Slack)
For Slack notifications to mention a user directly (e.g., `@Oscar Barrios`), the user must configure their **Slack Member ID** in their profile page on the platform.
* **How to find the Slack Member ID:** In the Slack app, click your profile picture > `Profile` > `...` (More) > `Copy member ID`. It's a string that usually starts with a `U`.

#### 3. Administrator Toggles
Admins have granular control over which email notifications are sent. Using the Django Admin panel, they can enable or disable notifications for each specific event.
* **Location:** `/admin/tasks/notificationtoggle/`
* **Functionality:** Each event key has a corresponding `is_email_enabled` checkbox.

The available event keys that can be toggled are defined in `tasks/choices.py`:
* `new_request_created`
* `request_pending_approval`
* `request_approved`
* `scheduled_request_activated`
* `update_requested`
* `update_provided`
* `request_blocked`
* `request_resolved`
* `request_sent_to_qa`
* `request_rejected`
* `request_cancelled`
* `request_uncancelled`
* `request_completed`