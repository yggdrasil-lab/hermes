#!/bin/bash
set -e

# Setup Host Directories for Hermes
echo "Ensuring host directories exist..."

# Obsidian Vault Path
if [ ! -d "/opt/atlas/vault" ]; then
    echo "Creating /opt/atlas/vault..."
    sudo mkdir -p /opt/atlas/vault
    # Ensure uid/gid 1000:1000 owns it so the Discord Bot / Gemini CLI container can read/write to it.
    sudo chown -R 1000:1000 /opt/atlas/vault
fi

echo "Host setup complete."
