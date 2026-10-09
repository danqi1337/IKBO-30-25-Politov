@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"

call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%ROOT%\tests\vfs\deep" --script "%ROOT%\tests\scripts\test_stage4.txt" < nul
echo код возврата: %ERRORLEVEL%

rmdir /s /q "%TMPD%"
