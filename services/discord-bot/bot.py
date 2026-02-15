import discord
import os
import asyncio
import logging
from discord.ext import commands

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('hermes_bot')

# Helper for secrets
def get_secret(name):
    # 1. Direct env var
    val = os.getenv(name)
    if val: return val
    
    # 2. _FILE suffix
    file_path = os.getenv(f"{name}_FILE")
    if file_path and os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read().strip()
            
    # 3. Docker Secret mount
    secret_path = f"/run/secrets/{name.lower()}"
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
            
    return None

# Environment Variables
TOKEN = get_secret('DISCORD_TOKEN')
GEMINI_CLI_PATH = os.getenv('GEMINI_CLI_PATH', 'gemini_cli.py')
VAULT_PATH = os.getenv('VAULT_PATH', '/vault')
MIMIR_MODEL = os.getenv('MIMIR_MODEL', 'gemini-pro')

if not TOKEN:
    logger.error("DISCORD_TOKEN not found!")
    exit(1)

# Initialize Bot
intents = discord.Intents.default()
intents.message_content = True  # Required for reading commands
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(activity=discord.Game(name="Watching the Vault"))

@bot.event
async def on_message(message):
    # Ignore self
    if message.author == bot.user:
        return

    # Only process DMs or whitelisted channel (optional layer, but server is private anyway)
    # Using 'Main' channel ID could be added here later.

    content = message.content.strip()
    if not content:
        return

    # Ack with a reaction
    try:
        await message.add_reaction("👁️")  # The All-Seeing Eye
    except:
        pass

    async with message.channel.typing():
        # Prepare CWD (Run in Vault)
        # This ensures the agent sees all files relative to Vault root.
        # History will be stored in .gemini/ inside the vault.
        cwd_path = VAULT_PATH
        
        # Check for GEMINI.md in Vault (Auto-loaded by CLI)
        if not os.path.exists(os.path.join(cwd_path, "GEMINI.md")):
             logger.error("CRITICAL: GEMINI.md not found in vault!")
             await message.reply("❌ **SYSTEM FAILURE:** Core Memory (`GEMINI.md`) is missing from the Vault.")
             return

        async def run_gemini(command_args):
            return await asyncio.create_subprocess_exec(
                *command_args,
                cwd=cwd_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        try:
            logger.info(f"Relaying to gemini-cli (In Vault)...")
            
            # Attempt 1: Resume (Last session in Vault folder)
            proc = await run_gemini(["gemini", "run", "--resume", content])
            stdout, stderr = await proc.communicate()
            
            # If failed (likely 'No session found to resume'), try fresh
            if proc.returncode != 0:
                logger.info("Resume failed (new session?), retrying without --resume...")
                proc = await run_gemini(["gemini", "run", content])
                stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                 logger.error(f"Gemini CLI Error: {stderr.decode()}")
                 await message.reply(f"⚠️ **Pantheon Error:**\n```\n{stderr.decode()}\n```")
                 return
            
            response_text = stdout.decode().strip()
            # Send (Chunked)
            # ... existing chunking logic ...
            
            # Check for empty response
            if not response_text:
                await message.reply("😶 The Oracle is silent. (Empty response)")
                return

            # Chunking Logic (Discord limits to 2000 chars)
            max_length = 2000
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            
            for chunk in chunks:
                await message.reply(chunk)
                
        except Exception as e:
            logger.error(f"Bot Exception: {e}")
            await message.reply(f"❌ **System Failure:** {str(e)}")

# Run Bot
bot.run(TOKEN)
