import os
import sys
import time
import socket
import webbrowser
import threading
from pathlib import Path

# Explicit imports to guide PyInstaller dependency analysis
import fastapi
import starlette
import pydantic
import sqlalchemy
import jose
import pwdlib
import multipart
import openai
import dotenv
import uvicorn

# Set base dir
if getattr(sys, "frozen", False):
    bundle_dir = Path(sys._MEIPASS)
    exe_dir = Path(sys.executable).resolve().parent
else:
    bundle_dir = Path(__file__).resolve().parent
    exe_dir = bundle_dir

os.environ["KTX_BASE_DIR"] = str(bundle_dir)

# Database file in exe_dir so it persists
db_path = exe_dir / "ktx_ai.db"
if not db_path.exists() and (bundle_dir / "backend" / "ktx_ai.db").exists():
    try:
        import shutil
        shutil.copyfile(str(bundle_dir / "backend" / "ktx_ai.db"), str(db_path))
    except Exception as e:
        print(f"[!] Warning copying database: {e}")

os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

# Ensure backend is on sys.path
backend_path = bundle_dir / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def find_available_port(start_port: int = 8000) -> int:
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def open_browser(port: int):
    time.sleep(1.2)
    url = f"http://127.0.0.1:{port}"
    print(f"\n[*] Dang mo trinh duyet tai: {url}")
    webbrowser.open(url)

def main():
    port = 8000
    if is_port_in_use(port):
        print(f"[!] Cong {port} dang duoc su dung, chuyen sang cong khac...")
        port = find_available_port(8001)

    print("=" * 60)
    print(" HE THONG QUAN LY KY TUC XA TICH HOP AI (KTX-AI)")
    print("=" * 60)
    print(f"[*] May chu dang khoi chay tai: http://127.0.0.1:{port}")
    print("[*] Nhan Ctrl + C de dung may chu.")
    print("=" * 60)

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
