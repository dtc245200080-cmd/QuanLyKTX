@echo off
chcp 65001 >nul
title DỪNG HỆ THỐNG KTX-AI
cd /d %~dp0

echo [*] Dang tim va dung cac tien trinh dang chay tren cong 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>nul
)
taskkill /F /IM KTX_Manager.exe >nul 2>nul

echo [OK] Da dung he thong KTX-AI thanh cong.
pause

