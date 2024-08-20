@echo off

:: Install the required packages
pip install -r requirements.txt

:: Run PyInstaller to build the executable
::pyinstaller main.spec

:: Clean the build
pyinstaller --clean main.spec 

@echo Done!
pause
