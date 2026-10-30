@echo off
cd /d %~dp0
if not exist .venv py -m venv .venv
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if not exist .env copy .env.example .env
call .venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
