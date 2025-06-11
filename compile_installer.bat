@echo off
:: Download icon if not exists
if not exist "atr_logo.ico" (
    powershell -Command "& {Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/The404Company/ATR/refs/heads/main/atr_logo.ico' -OutFile 'atr_logo.ico'}"
)

:: Compile installer with icon
pyinstaller --noconfirm ^
    --onefile ^
    --add-data "atr_logo.ico;." ^
    --icon=atr_logo.ico ^
    installer.py
