@echo off
set BRAVE_PATH="C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
set DEBUG_PORT=9222

echo.
echo ============================================================
echo   BRAVE MAIN PROFILE BOT STARTER
echo ============================================================
echo.
echo IMPORTANT: 
echo 1. This will use your MAIN Brave profile (where you are already logged in).
echo 2. ALL existing Brave windows MUST be closed first.
echo 3. The script will try to close them for you.
echo.
set /p confirm="Close Brave and start in debug mode? (y/n): "
if /i not "%confirm%"=="y" exit /b

echo Closing Brave...
taskkill /F /IM brave.exe /T >nul 2>&1
timeout /t 2 >nul

echo Starting Brave with remote debugging on port %DEBUG_PORT%...
echo.

if not exist %BRAVE_PATH% (
    set BRAVE_PATH="C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
)
if not exist %BRAVE_PATH% (
    set BRAVE_PATH="%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"
)

if not exist %BRAVE_PATH% (
    echo ERROR: Brave browser not found. Please edit this .bat file.
    pause
    exit /b
)

:: We omit --user-data-dir to use your DEFAULT/MAIN profile
start "" %BRAVE_PATH% --remote-debugging-port=%DEBUG_PORT% --restore-last-session

echo Brave started! 
echo 1. Check if your Instagram tabs are open.
echo 2. Keep this Brave window open.
echo 3. Now you can run: python browser_bot.py
echo.
pause
