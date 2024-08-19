@echo off

:: Install the required packages
pip install -r requirements.txt

:: Run PyInstaller to build the executable
pyinstaller main.spec

:: Move the generated executable to the root directory
move /Y dist\main\main.exe .

@echo Done!
pause
