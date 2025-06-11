@echo off
echo Installing dependencies...
pip install pyinstaller pynput pyperclip pystray Pillow

echo Downloading icon...
if not exist "atr_logo.ico" (
    powershell -Command "& {Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/The404Company/ATR/refs/heads/main/atr_logo.ico' -OutFile 'atr_logo.ico'}"
)

echo Compiling ATR...
pyinstaller --noconfirm ^
    --onefile ^
    --windowed ^
    --icon=atr_logo.ico ^
    atr.py

echo Done! The executable is in the 'dist' folder.
pause
