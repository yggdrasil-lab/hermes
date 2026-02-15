import discord
import os
import asyncio
import logging
import shutil
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

# Initialize Client (Simpler than Bot for event-only logic)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    await client.change_presence(activity=discord.Game(name="Watching the Vault"))

@client.event
async def on_message(message):
    logger.info(f"Received message from {message.author}: '{message.content}'")

    # Ignore self
    if message.author == client.user:
        return

    # Smart Trigger:
    # 1. Always respond to DMs
    # 2. Respond to Channels ONLY if mentioned
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = client.user in message.mentions

    if not is_dm and not is_mentioned:
        return

    content = message.content.strip()
    
    # If mentioned in channel, strip the mention to get clean prompt
    if is_mentioned:
        content = content.replace(f'<@{client.user.id}>', '').replace(f'<@!{client.user.id}>', '').strip()

    if not content:
        return

    # --- Persona Routing ---
    # Dynamically discover active agents from Vault
    agents_dir = os.path.join(VAULT_PATH, "Atlas", "Meta", "Agents")
    personas = {}
    if os.path.isdir(agents_dir):
        for f in os.listdir(agents_dir):
            if f.endswith('.md') and os.path.isfile(os.path.join(agents_dir, f)):
                name = f.replace('.md', '')
                personas[f'/{name.lower()}'] = name
    
    persona = 'Zeus'  # Default
    for cmd, name in personas.items():
        if content.lower().startswith(cmd):
            persona = name
            content = content[len(cmd):].strip()
            break
    
    # Build Discord-aware prompt with persona directive
    # Read the Hermes agent file as the system prompt (single source of truth)
    hermes_prompt_path = os.path.join(VAULT_PATH, "Atlas", "Meta", "Agents", "Hermes.md")
    system_prompt = ""
    if os.path.exists(hermes_prompt_path):
        with open(hermes_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
    
    discord_prompt = (
        f"[SYSTEM PROMPT]\n{system_prompt}\n[END SYSTEM PROMPT]\n\n"
        f"[ACTIVE PERSONA: {persona}]\n"
        f"Read and adopt Atlas/Meta/Agents/{persona}.md directives.\n\n"
        f"[USER MESSAGE]\n{content}"
    )

    # Ack with a reaction
    try:
        await message.add_reaction("👁️")  # The All-Seeing Eye
    except:
        pass

    async with message.channel.typing():
        # Prepare CWD (Run in Vault)
        cwd_path = VAULT_PATH
        
        # Check for GEMINI.md location
        root_gemini = os.path.join(cwd_path, "GEMINI.md")
        alt_gemini = os.path.join(cwd_path, "Atlas", "Meta", "GEMINI.md")
        
        if not os.path.exists(root_gemini):
            # Try to start from Atlas/Meta
            if os.path.exists(alt_gemini):
                try:
                    # Create symlink in root so CLI finds it
                    os.symlink(alt_gemini, root_gemini)
                    logger.info("Symlinked Atlas/Meta/GEMINI.md to root.")
                except Exception as e:
                    logger.warning(f"Could not symlink GEMINI.md: {e}")
                    # Keep going, maybe CLI allows config or we rely on copy? 
                    # For now, fail if we can't link, as CLI is dumb.
                    # Or maybe we can just copy it?
                    try:
                        import shutil
                        shutil.copy(alt_gemini, root_gemini)
                        logger.info("Copied GEMINI.md to root (Symlink failed).")
                    except Exception as copy_e:
                        logger.error(f"Failed to copy GEMINI.md: {copy_e}")
                        await message.reply(f"❌ **System Failure:** Could not stage `GEMINI.md` from `Atlas/Meta`.")
                        return
            else:
                 logger.error("CRITICAL: GEMINI.md not found in root OR Atlas/Meta!")
                 await message.reply("❌ **SYSTEM FAILURE:** Core Memory (`GEMINI.md`) is missing from the Vault (Checked Root and `Atlas/Meta`).")
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
            
            # --yolo: auto-approve file edits
            # -p: non-interactive prompt mode (cleaner output)
            proc = await run_gemini(["gemini", "--yolo", "-p", discord_prompt])
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                 logger.error(f"Gemini CLI Error: {stderr.decode()}")
                 await message.reply(f"⚠️ **Pantheon Error:**\n```\n{stderr.decode()}\n```")
                 return
            
            response_text = stdout.decode().strip()
            
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
client.run(TOKEN)
