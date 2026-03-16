@echo off
setlocal

REM Askpass helper for Git on Windows without relying on sh/bash.
REM Requires env vars:
REM   - GITHUB_USERNAME
REM   - GITHUB_TOKEN  (GitHub PAT)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0git_askpass.ps1" %*
exit /b %ERRORLEVEL%

