import asyncio
import uvicorn
from app.main import app
from app.smtp import create_smtp_controller

async def main():
    # 1. Configure FastAPI (Uvicorn)
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)

    # 2. Configure SMTP Server
    smtp_controller = create_smtp_controller(host="0.0.0.0", port=2525)
    
    print("Starting Hermes Unified Gateway...")
    print("HTTP API listening on port 8000")
    print("SMTP Server listening on port 2525")

    # 3. Start SMTP Controller
    smtp_controller.start()

    try:
        # 4. Run Uvicorn (blocking, so we await it)
        # Note: server.serve() creates its own loop if not in one, 
        # but here we are in 'main', so we task it.
        # Actually uvicorn.Server.serve() is an async method in newer versions.
        await server.serve()
    finally:
        print("Shutting down SMTP Server...")
        smtp_controller.stop()

if __name__ == "__main__":
    asyncio.run(main())
