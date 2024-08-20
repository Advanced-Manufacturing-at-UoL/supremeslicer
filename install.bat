@echo off

:: Upgrade pip
python -m pip install --upgrade pip

:: Install the required packages
pip install -r requirements.txt

:: Run PyInstaller to build the executable
pyinstaller --noconfirm .\main.spec

:: If you have built before, you may need to clean the build rather than building it itself
::pyinstaller --clean --noconfirm .\main.spec 

@echo Done!
pause
