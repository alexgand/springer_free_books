@echo off

::-- Get Python major version
setlocal
for /f "tokens=2 delims=. " %%f in ('python --version') do set majorVersion=%%f
echo Detected Python major version: %majorVersion%

::-- Create virtual environment
python -m venv .venv

::--- Activate virtual environment
call .venv\Scripts\activate.bat

::-- Upgrade pip at virtual environment
python -m pip install --upgrade pip

::-- Install requirements at virtual environment
if "%majorVersion%"=="2" (
  pip install -r requirements2x.txt
) else (
  pip install -r requirements.txt
)

::-- Run main program at virtual environment
python main.py

::-- Deactivate virtual environment
call .venv\Scripts\deactivate.bat

pause
