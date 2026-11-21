@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting house editor...
echo Open in browser: http://127.0.0.1:8765/
echo (Keep this window open; close it or Ctrl+C to stop)
start "" http://127.0.0.1:8765/
"C:\Users\lyh\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe" editor_server.py
pause
