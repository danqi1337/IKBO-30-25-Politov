@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"

echo ### --vfs --log --script --headless одновременно
call "%ROOT%\run.bat" --headless --vfs "%TMPD%\some-vfs" --log "%TMPD%\log.csv" --script "%ROOT%\tests\scripts\test_stage2.txt" < nul
echo код возврата: %ERRORLEVEL%

echo.
echo ### справка --help
call "%ROOT%\run.bat" --help

rmdir /s /q "%TMPD%"
