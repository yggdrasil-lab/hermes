# Hermes: Unified Notification Gateway

Hermes is a centralized microservice for handling multi-channel notifications. Currently, it supports sending emails via AWS SES, with planned support for Discord and other channels.

## Features

- **Multi-channel support**: Easily extensible architecture for different notification providers.
- **RESTful API**: Simple POST endpoint for triggering notifications.
- **Dockerized**: Ready for production deployment using Docker.
- **Validation**: Strict schema validation using Pydantic.

## Tech Stack

- **Python 3.11+**
- **FastAPI**
- **Boto3** (AWS SDK)
- **Pydantic Settings** (Configuration management)

## Getting Started

### Prerequisites

- AWS Account with SES (Simple Email Service) configured.
- Verified Sender Identity (Email or Domain) in AWS SES.
- Docker (optional, for containerized deployment).

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your credentials:
   - `AWS_ACCESS_KEY_ID`: Your AWS access key.
   - `AWS_SECRET_ACCESS_KEY`: Your AWS secret key.
   - `AWS_REGION`: The AWS region where SES is configured (e.g., `us-east-1`).
   - `EMAIL_SENDER`: The verified email address you are sending from.

### Running with Docker

1. Build the image:
   ```bash
   docker build -t hermes .
   ```
2. Run the container:
   ```bash
   docker run --env-file .env -p 8000:8000 hermes
   ```

### Running Locally (Development)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

### Send a Notification

**Endpoint:** `POST /notify`

**Request Body:**

```json
{
  "channel": "email",
  "recipient": "recipient@example.com",
  "subject": "Test Notification",
  "body": "This is a notification sent via Hermes."
}
```

**Example with cURL:**

```bash
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "subject": "Hello",
    "body": "World"
  }'
```

## Project Structure

```text
hermes/
├── app/
│   ├── core/         # Configuration and settings
│   ├── models/       # Pydantic schemas
│   ├── services/     # Logic for notification providers (Email, Discord, etc.)
│   └── main.py       # FastAPI application and routes
├── requirements.txt  # Python dependencies
└── Dockerfile        # Production build configuration
```
