@echo off

:: Ensure the script operates in the directory one level out where it resides
cd %~dp0..

:: Ask the user if they want to install requirements
set /p install_reqs="Do you want to install requirements? (y/n): "
if /i "%install_reqs%"=="y" (
    pip install -r resources\requirements.txt
) else (
    echo Skipping requirements installation.
)

:: Ask the user if they want to build the executable from the main.spec file
set /p build_exe="Do you want to build the executable from the main.spec? (y/n): "
if /i "%build_exe%"=="y" (
    :: Assuming the spec file is inside the 'resources' folder, adjust as necessary
    echo Current directory: %cd%
    pyinstaller --clean main.spec
) else (
    echo Skipping executable build.
)

:: Check if the executable exists in the 'dist' folder and move it
if exist dist\main.exe (
    move dist\main.exe .
    echo Executable moved to current directory.
    
    :: Delete the dist directory after moving the executable
    rmdir /s /q dist
    echo dist directory deleted.

    :: Delete the build directory after the executable has been built and moved
    rmdir /s /q build
    echo build directory deleted
    
) else (
    echo Executable not found, skipping move.
)
pause
