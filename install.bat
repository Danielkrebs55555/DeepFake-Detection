@echo off
setlocal enabledelayedexpansion

:: Check if Python 3.10.0 is installed
python --version 2>nul | findstr /C:"Python 3.10.0" >nul
if %errorlevel% neq 0 (
    echo Python 3.10.0 not found. Installing...
    
    :: Download Python 3.10.0 installer
    curl -o python_installer.exe https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe
    
    :: Install Python 3.10.0 silently with Add to PATH option
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    
    :: Wait for installation to complete
    timeout /t 30
    
    :: Delete installer
    del python_installer.exe
    
    :: Refresh environment variables
    call refreshenv.cmd 2>nul
    if !errorlevel! neq 0 (
        echo Refreshing environment variables...
        for /f "tokens=*" %%a in ('path') do set "PATH=%%a"
    )
) else (
    echo Python 3.10.0 is already installed.
)

:: Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Removing existing virtual environment...
    rmdir /s /q venv
)
python -m venv venv

:: Activate virtual environment and install requirements
echo Activating virtual environment and installing requirements...
call venv\Scripts\activate.bat
if exist requirements.txt (
    pip install -r requirements.txt
    if !errorlevel! equ 0 (
        echo Requirements installed successfully.
    ) else (
        echo Error installing requirements.
        exit /b 1
    )
) else (
    echo requirements.txt not found.
    exit /b 1
)

echo Setup completed successfully.
pause