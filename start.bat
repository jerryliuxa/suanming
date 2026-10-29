@echo off
chcp 65001 >nul
cd /d %~dp0
title 玄机阁 - 八字排盘命理平台
echo.
echo   正在启动 玄机阁 · 八字排盘命理平台 ...
echo   （如 8766 端口被占用，可改用: python -m server.main 8800）
echo.
start "" http://127.0.0.1:8766
python -m server.main 8766
pause
