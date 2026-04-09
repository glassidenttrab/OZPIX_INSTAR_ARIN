@echo off
setlocal

:: Check for common compilers
where cl.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Building with MSVC (cl.exe)...
    cl.exe /Iinclude src\sim\main.c src\sim\events.c /Fe:bin\sim.exe
    goto end
)

where gcc.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Building with GCC (gcc.exe)...
    if not exist bin mkdir bin
    gcc -o bin\sim.exe src\sim\main.c src\sim\events.c -Iinclude
    goto end
)

echo No supported compiler (cl.exe or gcc.exe) found in PATH.
echo Please ensure a C compiler is installed and added to your environment variables.

:end
if %ERRORLEVEL% equ 0 (
    echo Build Successful! Run bin\sim.exe to start simulation.
) else (
    echo Build Failed!
)
pause
