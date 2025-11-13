@echo off
REM Optimized build script for Marwan CRM
REM This script builds the executable with size optimizations

echo Building Marwan CRM with optimizations...
echo.

REM Check if UPX is available (optional but recommended for size reduction)
where upx >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo UPX found - will use compression
) else (
    echo UPX not found - install UPX for better compression (optional)
    echo Download from: https://upx.github.io/
)

echo.
echo Running PyInstaller...
python -m PyInstaller Marwan_CRM.spec --clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Executable location: dist\Marwan_CRM.exe
    echo.
    
    REM Show file size
    for %%A in (dist\Marwan_CRM.exe) do (
        set size=%%~zA
        set /a sizeMB=%%~zA/1048576
        echo File size: !sizeMB! MB
    )
) else (
    echo.
    echo Build failed! Check errors above.
    exit /b 1
)

pause

