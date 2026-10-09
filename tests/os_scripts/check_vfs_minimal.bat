@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"
echo ### --vfs tests\vfs\minimal
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%ROOT%\tests\vfs\minimal" --script "%ROOT%\tests\scripts\vfs_info.txt" < nul
echo код возврата: %ERRORLEVEL%

echo.
echo ### тот же VFS + общий скрипт этапа 3
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%ROOT%\tests\vfs\minimal" --script "%ROOT%\tests\scripts\test_stage3.txt" < nul
echo код возврата: %ERRORLEVEL%

rmdir /s /q "%TMPD%"
