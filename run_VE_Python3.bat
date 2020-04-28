@echo off

::--- Create virtual environment
python -m venv .venv

::--- Activate virtual environment
call .venv\Scripts\activate.bat

::-- Upgrading pip at virtual environment
python -m pip install --upgrade pip

::-- Installing requirements at virtual environment
pip install -r requirements.txt

::-- Running main program
python main.py

pause
