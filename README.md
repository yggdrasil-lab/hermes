# Hermes

> I am Hermes, the Winged Messenger of the Yggdrasil ecosystem. My domain is Notifications, Messaging, and the Flow of Information. I carry the master's words across the digital divide.

## Mission

I am the central switchboard and intelligence interface of your infrastructure. My mission is two-fold:
1.  **Notification Gateway:** Ensure no critical alert remains unheard, translating internal signals into Email or Chat.
2.  **Interactive Intelligence:** Provide a secure, private interface to the Second Brain via Discord, powered by the Google Gemini CLI.

## Core Philosophy

*   **Unified Input**: I am the single entry point for all notifications.
*   **Smart Routing**: I choose the path that fits the priority—Email for logs, Chat for attention.
*   **Secure Intelligence**: I expose the power of the Second Brain (Vault) through a sandboxed, private Discord channel, maintaining full context and history.

---

## Tech Stack

*   **Python 3.11+**: Core logic for API and Bot.
*   **FastAPI**: Notification Gateway REST API.
*   **Discord.py**: Interactive Bot interface.
*   **Google Gemini CLI (Node.js)**: Headless AI agent for processing prompts and vault queries.
*   **Boto3**: AWS SES integration.

## Architecture

The system operates through two primary microservices:

### 1. Notification Gateway (API)
*   **HTTP Interface**: RESTful API for service integration.
*   **SMTP Gateway**: Listener on port 2525 for legacy mail routing.
*   **AWS SES**: Backend for reliable email delivery.

### 2. Discord Bot (Interface)
*   **Private Channel**: Secure interface to the system.
*   **Gemini CLI**: Headless agent running in the Vault context.
*   **Session Persistence**: Maintains daily conversation history.
*   **Vault Access**: Read/Write access to the Second Brain for journaling and querying.

## Prerequisites

- **AWS Account**: Verified Sender Identity in Amazon SES.
- **Docker & Docker Compose**
- **aether-net**: External Docker network (see `Forge/yggdrasil-os`).

## Directory Structure

```text
hermes/
├── app/              # Notification Gateway (API)
│   ├── core/
│   ├── services/
│   └── main.py
├── services/         # Microservices
│   └── discord-bot/  # Discord Interface + Gemini CLI
├── integration_test/
├── scripts/          # Deployment & Secret Utils
└── docker-compose.yml
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

Update `.env` (or Github Secrets for Prod) with:

### Notification Gateway
- `AWS_ACCESS_KEY_ID`: IAM Access Key.
- `AWS_SECRET_ACCESS_KEY`: IAM Secret Key.
- `AWS_REGION`: AWS Region (e.g., `ap-southeast-2`).
- `EMAIL_SENDER`: Your verified sender address.

### Discord Bot (Secrets)
- `DISCORD_TOKEN`: Bot Token from Developer Portal.
- `GEMINI_CONFIG`: Contents of `~/.gemini/config.json` (Auth).
- `OBSIDIAN_VAULT_PATH`: Host path to the Second Brain (Environment Variable).

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
