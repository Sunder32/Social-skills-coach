"""
Backend entry point for PyInstaller
"""
import os
import sys

# Set the base directory for the bundled app
if getattr(sys, 'frozen', False):
    # Running as compiled
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
    
    # Load production.env from the same directory as executable
    from dotenv import load_dotenv
    env_path = os.path.join(BASE_DIR, 'production.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        # Try .env as fallback
        env_path = os.path.join(BASE_DIR, '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
    
    # Create data directory for SQLite if it doesn't exist
    data_dir = os.path.join(BASE_DIR, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Now import and run the app
import uvicorn
from app.main import app

if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 8001))
    host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    
    print(f"Starting Social Skills Coach Backend on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
