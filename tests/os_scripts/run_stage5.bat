@echo off
chcp 65001 > nul
set ROOT=%~dp0..\..
set TMPD=%TEMP%\emulator_check_%RANDOM%
mkdir "%TMPD%"
set VFS=%ROOT%\tests\vfs\deep

dir /s /b "%VFS%" > "%TMPD%\before.txt"
call "%ROOT%\run.bat" --headless --log "%TMPD%\log.csv" --vfs "%VFS%" --script "%ROOT%\tests\scripts\test_stage5.txt" < nul
echo код возврата: %ERRORLEVEL%
dir /s /b "%VFS%" > "%TMPD%\after.txt"
fc "%TMPD%\before.txt" "%TMPD%\after.txt" > nul && (echo VFS на диске не изменилась: OK) || (echo VFS на диске изменилась: ОШИБКА)

rmdir /s /q "%TMPD%"
