@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

if /I "%~1"=="--install" goto :install
if /I "%~1"=="--uninstall" goto :uninstall

pushd "%SCRIPT_DIR%"
set "DEPS_STAMP=venv\.devmind_requirements_installed"

if not exist "venv\Scripts\activate.bat" (
    echo [DevMind] Initial setup: creating Python virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [DevMind] Setup failed while creating the virtual environment.
        popd
        endlocal
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [DevMind] Unable to activate the virtual environment.
    popd
    endlocal
    exit /b 1
)

if not exist "%DEPS_STAMP%" (
    echo [DevMind] Initial setup: installing project dependencies...
    pip install -r requirements.txt --quiet
    if %ERRORLEVEL% NEQ 0 (
        echo [DevMind] Dependency installation failed.
        popd
        endlocal
        exit /b 1
    )
    type nul > "%DEPS_STAMP%"
)

echo [DevMind] Starting DevMind CLI...
python main.py

popd
endlocal
goto :eof

:install
set "LAUNCHER_DIR=%USERPROFILE%\devmind-bin"
set "LAUNCHER_PATH=%LAUNCHER_DIR%\devmind.bat"

if not exist "%LAUNCHER_DIR%" mkdir "%LAUNCHER_DIR%"

(
    echo @echo off
    echo call "%SCRIPT_DIR%\devmind.bat" %%*
) > "%LAUNCHER_PATH%"

echo [DevMind] Launcher created: "%LAUNCHER_PATH%"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$target = '%LAUNCHER_DIR%';" ^
    "$current = [Environment]::GetEnvironmentVariable('Path','User');" ^
    "if ([string]::IsNullOrWhiteSpace($current)) { $current = $target }" ^
    "elseif (($current -split ';') -notcontains $target) { $current = $current.TrimEnd(';') + ';' + $target }" ^
    "[Environment]::SetEnvironmentVariable('Path', $current, 'User')"

if %ERRORLEVEL% NEQ 0 (
    echo [DevMind] Failed to update user PATH automatically.
    echo [DevMind] Please add this folder manually to PATH: "%LAUNCHER_DIR%"
) else (
    echo [DevMind] User PATH updated with "%LAUNCHER_DIR%".
    echo [DevMind] Close and reopen terminal, then run: devmind
)

endlocal
goto :eof

:uninstall
set "LAUNCHER_DIR=%USERPROFILE%\devmind-bin"
set "LAUNCHER_PATH=%LAUNCHER_DIR%\devmind.bat"

if exist "%LAUNCHER_PATH%" del "%LAUNCHER_PATH%"
echo [DevMind] Removed launcher: "%LAUNCHER_PATH%"
echo [DevMind] Note: "%LAUNCHER_DIR%" may still be present in PATH. Remove it manually if desired.

endlocal
goto :eof
