@echo off
:: Ask the user if they want to install requirements
set /p install_reqs="Do you want to install requirements? (y/n): "
if /i "%install_reqs%"=="y" (
    pip install -r resources\requirements.txt
) else (
    echo Skipping requirements installation.
)

:: Ask the user if they want to install from the main.spec file
set /p build_exe="Do you want to build the executable from main.spec? (y/n): "
if /i "%build_exe%"=="y" (
    :: Move back from the resources directory to the supremeslicer directory
    echo Current directory: %cd%
    pyinstaller main.spec
) else (
    echo Skipping executable build.
)

:: Move the output exe from the dist folder back to the parent directory
if exist dist\main.exe (
    move dist\main.exe ..
    echo Executable moved to parent directory.
) else (
    echo Executable not found, skipping move.
)
pause
