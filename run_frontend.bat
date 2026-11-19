@echo off
setlocal enabledelayedexpansion
echo ========================================================
echo Starting KMP + TruCortex + Bloomfire Frontend (Vite)
echo ========================================================
cd /d %~dp0frontend

set "NPM_EXE="

:: 1. Check if npm is in PATH
where npm >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "NPM_EXE=npm"
    goto :found_npm
)

:: 2. Check standard Node.js installation paths on C:
if exist "C:\Program Files\nodejs\npm.cmd" (
    set "NPM_EXE=C:\Program Files\nodejs\npm.cmd"
    set "PATH=C:\Program Files\nodejs;%PATH%"
    goto :found_npm
)

if exist "C:\Program Files (x86)\nodejs\npm.cmd" (
    set "NPM_EXE=C:\Program Files (x86)\nodejs\npm.cmd"
    set "PATH=C:\Program Files (x86)\nodejs;%PATH%"
    goto :found_npm
)

for /d %%D in ("C:\Users\%USERNAME%\AppData\Roaming\nvm\v*") do (
    if exist "%%D\npm.cmd" (
        set "NPM_EXE=%%D\npm.cmd"
        set "PATH=%%D;%PATH%"
        goto :found_npm
    )
)

:found_npm
if "%NPM_EXE%"=="" (
    echo [ERROR] Could not find npm or Node.js on C: drive.
    echo Please ensure Node.js is installed from https://nodejs.org
    pause
    exit /b 1
)

echo Using NPM: "%NPM_EXE%"

if not exist node_modules (
    echo Installing npm dependencies...
    call "%NPM_EXE%" install
)

echo Starting Vite Dev Server on http://localhost:5173...
call "%NPM_EXE%" run dev
pause
