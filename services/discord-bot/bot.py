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

# Store sessions per user ID for conversation continuity
active_sessions = {}

@client.event
async def on_ready():
    global system_prompt
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

    # Handle Attachments
    attachments = message.attachments
    if attachments:
        import datetime
        # Use x/Temp for incoming files (Temporary holding)
        temp_dir = os.path.join(VAULT_PATH, "x", "Temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        uploaded_files = []
        for attachment in attachments:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{attachment.filename}"
            filepath = os.path.join(temp_dir, filename)
            
            try:
                await attachment.save(filepath)
                # Use relative path for the agent
                uploaded_files.append(f"x/Temp/{filename}")
                logger.info(f"Saved attachment: {filepath}")
            except Exception as e:
                logger.error(f"Failed to save attachment {filename}: {e}")

        if uploaded_files:
            content += f"\n\n[System: User attached files stored in x/Temp at:]\n" + "\n".join(uploaded_files)

    if not content:
        return

    # Build prompt with SYSTEM reference + USER
    # We rely on the model to read Hermes.md from the vault context.
    discord_prompt = (
        f"[SYSTEM: Role=Atlas/Meta/Agents/Hermes.md]\n"
        f"You are Hermes. Execute tools silently. Output ONLY the final response.\n"
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
            
            # Check for an active session to resume
            session_id = active_sessions.get(message.author.id)
            
            # Setup command
            # --yolo: auto-approve all tool calls (file edits + shell commands)
            # -p: non-interactive prompt mode (cleaner output)
            cmd_args = ["gemini", "--yolo", "-p"]
            if session_id:
                cmd_args.extend(["--resume", session_id])
            
            cmd_args.append(discord_prompt)
            
            proc = await run_gemini(cmd_args)
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                 logger.error(f"Gemini CLI Error: {stderr.decode()}")
                 await message.reply(f"⚠️ **Pantheon Error:**\n```\n{stderr.decode()}\n```")
                 return
            
            response_text = stdout.decode().strip()
            
            # Extract JSON output 
            try:
                import json
                import re
                
                # Remove any ANSI escape sequences added by the CLI
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_text = ansi_escape.sub('', response_text)
                
                if "{" in clean_text:
                    json_start = clean_text.find("{")
                    json_end = clean_text.rfind("}") + 1
                    json_str = clean_text[json_start:json_end]
                    
                    try:
                        output_data = json.loads(json_str)
                        
                        # Update active session ID
                        if "session_id" in output_data:
                            active_sessions[message.author.id] = output_data["session_id"]
                            
                        # Reassign output text
                        if "response" in output_data:
                            response_text = output_data["response"]
                            
                    except json.JSONDecodeError as je:
                        logger.error(f"Failed to parse JSON: {je}. Extracted string starts with: {json_str[:30]!r}")
            except Exception as e:
                logger.error(f"JSON logic error: {e}")
            
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
