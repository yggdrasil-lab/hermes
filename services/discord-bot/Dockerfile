FROM python:3.11-slim

WORKDIR /app

# Install git, nodejs, npm
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install @google/gemini-cli globally
RUN npm install -g @google/gemini-cli

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The bot will be mounted via Volume in dev, but COPY here for prod
# The Vault (knowledge) will be mounted at /vault
COPY . .

# Link the Docker Secret to where the CLI expects it (~/.gemini or ~/.config/...)
CMD ["sh", "-c", "mkdir -p /root/.gemini && ln -sf /run/secrets/.gemini /root/.gemini/settings.json && ln -sf /run/secrets/.gemini /root/.gemini/config.json && python bot.py"]
