@echo off

:: Install the required packages
pip install -r requirements.txt

:: Run PyInstaller to build the executable
pyinstaller main.spec

:: If you have built before, you may need to clean the build rather than building it itself
::pyinstaller --clean main.spec 

@echo Done!
pause
