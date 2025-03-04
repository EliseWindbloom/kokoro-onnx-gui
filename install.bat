@echo off
setlocal EnableDelayedExpansion

:: Display starting message
echo Starting installation for kokoro-onnx...

:: Check for Git
echo Checking for Git...
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed.
    echo Please download and install Git from https://git-scm.com/downloads
    echo After installing Git, run this installer again.
    pause
    exit /b 1
)

:: Check if kokoro-onnx folder already exists
if exist kokoro-onnx (
    echo A folder named 'kokoro-onnx' already exists in this directory.
    echo Please remove or rename it before running the installer again.
    pause
    exit /b 1
)

:: Create a virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    echo Ensure Python is installed correctly and try again.
    pause
    exit /b 1
)

:: Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install the package and additional dependencies
echo Installing kokoro-onnx and dependencies...
pip install . misaki[en] soundfile pygame ttkbootstrap
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages.
    echo Check your internet connection or pip configuration and try again.
    pause
    exit /b 1
)

:: Download model files if they don't exist
echo Downloading model files (this may take a few minutes)...
if not exist kokoro-v1.0.onnx (
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx' -OutFile 'kokoro-v1.0.onnx'" 2>nul
    if %errorlevel% neq 0 (
        echo WARNING: Failed to download kokoro-v1.0.onnx. You may need to download it manually from:
        echo https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
    )
) else (
    echo kokoro-v1.0.onnx already exists, skipping download.
)

if not exist voices-v1.0.bin (
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin' -OutFile 'voices-v1.0.bin'" 2>nul
    if %errorlevel% neq 0 (
        echo WARNING: Failed to download voices-v1.0.bin. You may need to download it manually from:
        echo https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
    )
) else (
    echo voices-v1.0.bin already exists, skipping download.
)

:: Display completion message and usage instructions
echo.
echo Installation completed successfully!
echo.
echo ### Usage Instructions ###
echo.
echo **To run the example:**
echo   - Double-click 'run_example.bat' to run the example script (examples\save.py).
echo     This will generate an audio file using the default settings.
echo.
echo **To use kokoro-onnx in your own scripts:**
echo   1. Open a Command Prompt.
echo   2. Navigate to the 'kokoro-onnx-windows' folder by typing: cd %CD%
echo   3. Activate the virtual environment by running: venv\Scripts\activate
echo   4. Write and run your Python scripts using the 'kokoro_onnx' package.
echo      Example: python -c "import kokoro_onnx; print('kokoro_onnx installed')"
echo.
echo **Optional: Improve Performance**
echo   - For possible better performance (e.g., improved language support), install espeak-ng.
echo   - Download and install it from: https://github.com/espeak-ng/espeak-ng/releases
echo   - Follow the instructions there to set it up on your system.
echo.
echo If you encounter issues, ensure you have:
echo   - An active internet connection.
echo   - Git and Python installed and added to your PATH.
echo   - At least 500MB of free disk space for the model files.
echo.
pause
