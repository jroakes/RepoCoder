@echo off
setlocal enabledelayedexpansion

echo RepoCoder PyPI Publishing Script
echo ================================

REM Navigate to the project root directory (one level up from scripts)
cd /d %~dp0\..

REM Activate virtual environment
call repocoder_env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment repocoder_env.
    echo Please make sure it exists and the path is correct.
    exit /b 1
)

REM Check for Python installation
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the system PATH.
    exit /b 1
)

REM Install or upgrade required tools
echo Installing/upgrading required tools...
pip install --upgrade setuptools wheel twine
if %errorlevel% neq 0 (
    echo Failed to install required tools.
    exit /b 1
)

REM Load PyPI token from .env file
for /f "tokens=2 delims==" %%a in ('findstr /I "PYPI_TOKEN" .env') do set PYPI_TOKEN=%%a
if "%PYPI_TOKEN%"=="" (
    echo PYPI_TOKEN not found in .env file.
    exit /b 1
)

REM Update version number using update_version.py
echo Updating version number...
python scripts\update_version.py
if %errorlevel% neq 0 (
    echo Failed to update version number.
    exit /b 1
)

REM Clean up old distribution files
if exist dist rmdir /s /q dist

REM Create distribution files
echo Creating distribution files...
python setup.py sdist bdist_wheel
if %errorlevel% neq 0 (
    echo Failed to create distribution files.
    echo Please ensure setup.py is correctly configured.
    exit /b 1
)

REM Check the package
echo Checking the package...
twine check dist/*
if %errorlevel% neq 0 (
    echo Package check failed. Please review the errors above.
    exit /b 1
)

REM Prompt for PyPI upload
set /p upload_choice=Do you want to upload to PyPI? (Y/N): 
if /i "%upload_choice%"=="Y" (
    REM Upload to PyPI using the token
    set TWINE_USERNAME=__token__
    set TWINE_PASSWORD=%PYPI_TOKEN%
    twine upload dist/*
    if %errorlevel% neq 0 (
        echo Failed to upload to PyPI. Please check your token and network connection.
        exit /b 1
    )
    echo Package uploaded successfully to PyPI!
) else (
    echo Package not uploaded. You can manually upload later using: twine upload dist/*
)

REM Deactivate virtual environment
call deactivate

echo Script completed successfully.
pause