# Hermes

> I am Hermes, the Winged Messenger of the Yggdrasil ecosystem. My domain is Notifications, Messaging, and the Flow of Information. I carry the master's words across the digital divide.

## Mission

I am the central switchboard of your infrastructure. My mission is to ensure that no critical alert or security token remains unheard. I translate the internal signals of your servers into the clear voice of email or the chime of chat, routing information where it is needed most.

## Core Philosophy

*   **Unified Input**: I am the single entry point for all notifications. No matter the source, the interface remains consistent.
*   **Smart Routing**: I choose the path that fits the priority—Email for permanence and logs, Chat for immediate attention.
*   **Abstraction**: I hide the complexities of external cloud APIs, allowing the rest of the infrastructure to remain decoupled and focused.

---

## Tech Stack

*   **Python 3.11+**: Primary programming language.
*   **FastAPI**: Web framework for the REST API.
*   **Boto3**: AWS SDK for direct Amazon SES integration.
*   **aiosmtpd**: Asynchronous SMTP server library.

## Architecture

The system operates through the following components:

1.  **HTTP Interface**: A RESTful API for modern service integration.
2.  **SMTP Gateway**: A listener on port 2525 for legacy mail routing (e.g., Authelia).
3.  **Modular Provider Logic**: An extensible backend supporting AWS SES (Current) and Discord (Planned).

## Prerequisites

- **AWS Account**: Verified Sender Identity in Amazon SES.
- **Docker & Docker Compose**
- **aether-net**: External Docker network (see `Forge/yggdrasil-os`).

## Directory Structure

```text
hermes/
├── app/
│   ├── core/         # Configuration and settings
│   ├── models/       # Pydantic schemas
│   ├── services/     # Logic for notification providers (Email, Discord, etc.)
│   └── main.py       # FastAPI application and routes
├── integration_test/ # Integration test suite
├── requirements.txt  # Python dependencies
└── Dockerfile        # Production build configuration
```

## Setup Instructions

### 1. Repository Initialization

```bash
git clone <your-repository-url> hermes
cd hermes
cp .env.example .env
```

### 2. Configuration

Update `.env` with your IAM credentials and verified sender:
- `AWS_ACCESS_KEY_ID`: IAM Access Key.
- `AWS_SECRET_ACCESS_KEY`: IAM Secret Key.
- `AWS_REGION`: AWS Region (e.g., `ap-southeast-2`).
- `EMAIL_SENDER`: Your verified sender address.
- `ENV` (Optional): Environment tag prepended to email subjects (e.g., `DEV`, `PROD`).

## Execution

### Development (Local)
For local development, you can use `docker compose up --build`. Ensure your `.env` file is populated.

### Production Deployment
Production deployment is handled automatically via the GitHub Actions workflow defined in `.github/workflows/deploy.yml`.

## Usage

### 1. HTTP API
**Endpoint:** `POST /notify`
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

### 2. SMTP Gateway
Connect legacy services to port **2525**. Incoming mail will be relayed via the configured SES identity.

## Integration Testing

```bash
cd integration_test
docker compose up
```
