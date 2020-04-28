@echo off

::-- Get Python major version
for /f "tokens=2 delims=. " %f in ('python --version') do set majorVersion=%f

::-- Create virtual environment
python -m venv .venv

::--- Activate virtual environment
call .venv\Scripts\activate.bat

::-- Upgrading pip at virtual environment
python -m pip install --upgrade pip

::-- Installing requirements at virtual environment
if "%majorVersion%"=="2" (
  pip install -r requirements2x.txt
) else (
  pip install -r requirements.txt
)

::-- Running main program
python main.py

pause
