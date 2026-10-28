@echo off
setlocal
title EdgeGuard AI - Push to GitHub
echo =====================================================================
echo    EdgeGuard AI: One-Click GitHub Repository Upload
echo =====================================================================
echo.
echo 1. Create a new EMPTY repository on GitHub (https://github.com/new)
echo    Name it: EdgeGuard-AI
echo    (Do NOT check "Add a README file", .gitignore, or license)
echo.
set /p REPO_URL="Paste your GitHub repository URL: "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered. Aborted.
    pause
    exit /b 1
)

echo.
echo Configuring remote and pushing branch 'main'...
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo [SUCCESS] EdgeGuard AI has been published to GitHub!
    echo =====================================================================
) else (
    echo.
    echo [NOTICE] If prompted, sign in via browser or Personal Access Token (PAT).
)

pause
