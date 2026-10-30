@echo off
chcp 65001 >nul
title HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ TÍCH HỢP AI (KTX-AI)
cd /d %~dp0

echo ======================================================================
echo           HỆ THỐNG QUẢN LÝ KÝ TÚC XÁ TÍCH HỢP AI (KTX-AI)
echo ======================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [!] KHONG TIM THAY PYTHON TREN MAY!
    echo Vui long cai dat Python 3.10 tro len tai: https://www.python.org/downloads/
    echo (Luu y tich chon "Add Python to PATH" khi cai dat).
    echo.
    echo HOAC: Ban co the chay ngay ban dong goi khong can cai Python tai:
    echo        dist\KTX_Manager\KTX_Manager.exe
    echo ======================================================================
    pause
    exit /b 1
)

cd backend
if not exist .venv (
    echo [*] Phat hien lan dau chay - Dang tu dong tao moi truong ao (.venv)...
    python -m venv .venv
    echo [*] Dang cai dat cac goi thu vien can thiet tu requirements.txt...
    call .venv\Scripts\python.exe -m pip install -r requirements.txt
)

if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
    )
)

cd ..
echo.
echo [*] He thong dang khoi dong...
echo [*] Trinh duyet se tu dong mo tai: http://127.0.0.1:8000
echo [*] De DUNG he thong, dong cua so nay hoac chay file DUNG_CHUONG_TRINH.bat
echo ======================================================================
echo.

start "" "http://127.0.0.1:8000"
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

