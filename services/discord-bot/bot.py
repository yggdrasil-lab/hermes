import discord
import os
import asyncio
import logging

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
VAULT_PATH = os.getenv('VAULT_PATH', '/vault')

if not TOKEN:
    logger.error("DISCORD_TOKEN not found!")
    exit(1)

# Initialize Client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Cached at startup
personas = {}  # {'/zeus': 'Zeus', ...}
system_prompt = ""  # Hermes.md content

@client.event
async def on_ready():
    global personas, system_prompt
    logger.info(f'Logged in as {client.user} (ID: {client.user.id})')
    await client.change_presence(activity=discord.Game(name="Watching the Vault"))
    
    # Cache available personas from Agent files
    agents_dir = os.path.join(VAULT_PATH, "Atlas", "Meta", "Agents")
    if os.path.isdir(agents_dir):
        for f in os.listdir(agents_dir):
            if f.endswith('.md') and os.path.isfile(os.path.join(agents_dir, f)):
                name = f.replace('.md', '')
                personas[f'/{name.lower()}'] = name
    logger.info(f"Loaded {len(personas)} personas: {list(personas.values())}")
    
    # Cache Hermes system prompt
    hermes_path = os.path.join(VAULT_PATH, "Atlas", "Meta", "Agents", "Hermes.md")
    if os.path.exists(hermes_path):
        with open(hermes_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        logger.info("Loaded Hermes system prompt.")
    
    logger.info("Hermes is ready. ⚡")

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
    persona = 'Zeus'  # Default
    for cmd, name in personas.items():
        if content.lower().startswith(cmd):
            persona = name
            content = content[len(cmd):].strip()
            break
    
    # Build prompt with system context + persona
    discord_prompt = (
        f"[SYSTEM PROMPT]\n{system_prompt}\n[END SYSTEM PROMPT]\n\n"
        f"[ACTIVE PERSONA: {persona}]\n"
        f"Read and adopt Atlas/Meta/Agents/{persona}.md directives.\n\n"
        f"[USER MESSAGE]\n{content}"
    )

    # Ack with a reaction
    try:
        await message.add_reaction("👁️")
    except Exception as e:
        logger.debug(f"Reaction failed: {e}")

    async with message.channel.typing():

        async def run_gemini(command_args):
            return await asyncio.create_subprocess_exec(
                *command_args,
                cwd=VAULT_PATH,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        try:
            logger.info(f"Relaying to gemini-cli (In Vault)...")
            
            # --yolo: auto-approve all tool calls (file edits + shell commands)
            # -p: non-interactive prompt mode (cleaner output)
            # Note: .gemini/settings.json also sets auto_edit + includeThoughts: false
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
