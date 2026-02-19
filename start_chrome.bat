@echo off
set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
set DEBUG_PORT=9222
set USER_DATA_DIR="C:\chrome_debug_profile"

echo Starting Chrome with remote debugging on port %DEBUG_PORT%...
echo Using user data directory: %USER_DATA_DIR%
echo.
echo IMPORTANT: Close all other Chrome windows before running this script if you want to use your main profile.
echo Or just use this separate profile for the bot.
echo.

if not exist %CHROME_PATH% (
    set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

start "" %CHROME_PATH% --remote-debugging-port=%DEBUG_PORT% --user-data-dir=%USER_DATA_DIR%

echo Chrome started. Please log in to Instagram now.
pause
